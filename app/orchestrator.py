import logging
import json
import re
from urllib.parse import urlparse

from app.models import QueryRequest
from app.agents.analytics import analytics_agent
from app.agents.seo import seo_agent
from app.llm.client import llm_client
from app.llm.schemas import IntentClassification, DecomposedQuery, MultiAgentResponse

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        pass

    async def route_request(self, request: QueryRequest):
        """
        Routes the request to the appropriate agent(s).
        
        Tier 1/2: Simple routing based on propertyId presence
        Tier 3: LLM-based intent detection for multi-agent queries
        """
        query = request.query.lower()
        
        # Tier 3: Detect if this might be a multi-agent query
        intent = await self._detect_intent(request.query, request.propertyId)
        logger.debug(f"Detected intent: {intent}")
        
        if intent == "BOTH":
            # Multi-agent fusion query
            return await self._handle_multi_agent_query(request)
        elif intent == "ANALYTICS" and request.propertyId:
            # Pure Analytics query
            return await analytics_agent.process_query(request.query, request.propertyId)
        elif intent == "SEO":
            # Pure SEO query
            return await seo_agent.process_query(request.query)
        else:
            # Fallback: Use simple routing
            if request.propertyId:
                return await analytics_agent.process_query(request.query, request.propertyId)
            else:
                return await seo_agent.process_query(request.query)

    async def _detect_intent(self, query: str, property_id: str = None) -> str:
        """Use LLM with structured output to detect query intent for routing."""
        prompt = f"""You are an intent classifier for a data analytics system.

Available agents:
1. ANALYTICS - Handles Google Analytics 4 (GA4) data: users, sessions, page views, traffic sources, etc.
2. SEO - Handles Screaming Frog SEO audit data: URLs, title tags, meta descriptions, indexability, HTTP status, etc.

User Query: "{query}"
Property ID Provided: {bool(property_id)}

Classify the query into ONE of these categories:
- ANALYTICS: Query only needs GA4 data
- SEO: Query only needs SEO audit data  
- BOTH: Query needs data from both sources (e.g., "top pages by views AND their title tags")
        
Return a JSON object with a single field "intent" containing one of the above values."""
        
        try:
            result = llm_client.chat_structured(
                [{"role": "user", "content": prompt}],
                response_model=IntentClassification,
                model="gemini-2.5-flash"
            )
            return result.intent
        except Exception as e:
            logger.error(f"Intent detection error: {e}")
            return "UNKNOWN"

    async def _decompose_query(self, query: str) -> DecomposedQuery:
        """Use LLM with structured output to break down multi-agent query into agent-specific sub-queries."""
        prompt = f"""You are a query decomposition expert for a multi-agent analytics system.

User Query: "{query}"

Break this query into specific sub-tasks for two agents:
1. Analytics Agent - handles GA4 data (page views, users, sessions, traffic)
2. SEO Agent - handles Screaming Frog data (title tags, meta descriptions, indexability, URLs)

Provide:
- analytics_query: The specific question for the Analytics agent (focus on metrics like views, users, sessions)
- seo_query: The specific question for the SEO agent (focus on URL metadata)
- output_format: "json" if user explicitly requests JSON output, otherwise "natural_language"
- limit: Number of results if specified in the query (default: 10)"""
        
        try:
            result = llm_client.chat_structured(
                [{"role": "user", "content": prompt}],
                response_model=DecomposedQuery,
                model="gemini-2.5-flash"
            )
            return result
        except Exception as e:
            logger.error(f"Query decomposition error: {e}")
            # Fallback to default decomposition
            return DecomposedQuery(
                analytics_query="Get top 20 pages by page views for the last 14 days",
                seo_query="List all URLs with title tags, meta descriptions, and indexability status",
                output_format="json" if "json" in query.lower() else "natural_language",
                limit=10
            )

    def _normalize_url(self, url: str) -> str:
        """Normalize URL/path for matching between GA4 and SEO data."""
        if not url:
            return ""
        
        # If it's a full URL, extract the path
        if url.startswith("http"):
            parsed = urlparse(url)
            path = parsed.path
        else:
            path = url
        
        # Normalize: lowercase, remove trailing slash (except for root)
        path = path.lower().rstrip("/")
        if not path:
            path = "/"
        
        return path

    async def _handle_multi_agent_query(self, request: QueryRequest) -> str:
        """Handle queries that require data from both Analytics and SEO agents."""
        
        # Step 1: Decompose the query into agent-specific sub-queries
        decomposition = await self._decompose_query(request.query)
        logger.debug(f"Query decomposition: {decomposition}")
        
        # Access Pydantic model attributes directly
        analytics_query = decomposition.analytics_query
        seo_query = decomposition.seo_query
        output_format = decomposition.output_format
        limit = decomposition.limit
        
        # Step 2: Get Analytics data if propertyId is available
        analytics_data = None
        if request.propertyId:
            try:
                analytics_data = await analytics_agent.process_query(analytics_query, request.propertyId)
            except Exception as e:
                analytics_data = f"Analytics error: {str(e)}"
        
        # Step 3: Get SEO data
        try:
            seo_data = await seo_agent.process_query(seo_query)
        except Exception as e:
            seo_data = f"SEO error: {str(e)}"
        
        # Step 4: Fuse the results using LLM
        json_instruction = ""
        if output_format == "json":
            json_instruction = """
            IMPORTANT: The user explicitly requested JSON output.
            Return the answer as a valid JSON array of objects. Each object should contain the relevant fields from both data sources.
            Example format:
            [
                {"page": "/path", "views": 1000, "title": "Page Title", "indexability": "Indexable"},
                ...
            ]
            """
        
        fusion_prompt = f"""
        You are a data analyst combining results from multiple sources.
        
        Original User Query: "{request.query}"
        Requested Result Limit: {limit}
        
        Analytics Data (GA4 - page views, users, sessions):
        {analytics_data if analytics_data else "No analytics data available"}
        
        SEO Audit Data (URLs, title tags, meta descriptions, indexability):
        {seo_data[:4000] if seo_data else "No SEO data available"}
        
        Instructions:
        1. Match pages between the two data sources by comparing paths/URLs
        2. GA4 uses 'pagePath' (e.g., /pricing), SEO uses full URLs (e.g., https://example.com/pricing)
        3. Provide a comprehensive answer combining insights from both sources
        4. Limit results to {limit} items unless otherwise specified
        5. If data from one source is missing, explain what was available
        
        REQUIRED OUTPUT STRUCTURE:
        Return a JSON object with exactly two fields:
        - "answer": The comprehensive answer string (or JSON string if requested).
        - "references": A list of source URLs used.
        
        {json_instruction}
        """
        
        try:
            fused_response = llm_client.chat_structured(
                [{"role": "user", "content": fusion_prompt}],
                response_model=MultiAgentResponse,
                model="gemini-2.5-flash"
            )
            return fused_response.answer
        except Exception as e:
            # Fallback: Return whatever data we have
            return f"Multi-agent query partially completed.\n\nAnalytics: {analytics_data}\n\nSEO: {seo_data}"

orchestrator = Orchestrator()

