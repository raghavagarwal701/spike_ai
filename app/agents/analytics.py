import logging
import os
import json
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Metric,
    Dimension,
    FilterExpression,
    OrderBy
)
from app.llm.client import llm_client
from app.llm.schemas import GA4QueryPlan

logger = logging.getLogger(__name__)

# GA4 Allowlist - Safe metrics and dimensions
# Reference: https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema
ALLOWED_METRICS = {
    "activeUsers", "newUsers", "totalUsers",
    "sessions", "sessionsPerUser", "engagedSessions",
    "screenPageViews", "screenPageViewsPerSession", "screenPageViewsPerUser",
    "eventCount", "eventsPerSession",
    "bounceRate", "engagementRate",
    "averageSessionDuration", "userEngagementDuration",
    "conversions", "totalRevenue",
    "transactions", "purchaseRevenue",
    "addToCarts", "checkouts",
    "dauPerMau", "dauPerWau", "wauPerMau",
    "crashFreeUsersRate", "crashAffectedUsers",
    "firstTimePurchasers", "firstTimePurchaserConversionRate",
    "itemsViewed", "itemsAddedToCart", "itemsPurchased",
    "itemRevenue", "itemListViews", "itemListClicks",
    "promotionViews", "promotionClicks",
}

ALLOWED_DIMENSIONS = {
    "date", "dateHour", "dateHourMinute",
    "year", "month", "week", "day", "dayOfWeek", "dayOfWeekName", "hour",
    "pagePath", "pageTitle", "pagePathPlusQueryString", "landingPage", "landingPagePlusQueryString",
    "hostname", "fullPageUrl",
    "sessionSource", "sessionMedium", "sessionSourceMedium", "sessionCampaignName",
    "sessionDefaultChannelGroup", "sessionManualAdContent",
    "firstUserSource", "firstUserMedium", "firstUserSourceMedium", "firstUserCampaignName",
    "country", "city", "region", "continent",
    "deviceCategory", "operatingSystem", "browser", "platform", "mobileDeviceModel",
    "language", "screenResolution",
    "eventName", "isConversionEvent",
    "newVsReturning", "userAgeBracket", "userGender",
    "itemName", "itemId", "itemCategory", "itemBrand",
}


class AnalyticsAgent:
    def __init__(self):
        # Set credentials env var for Google Client
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
        
    def _get_client(self):
         return BetaAnalyticsDataClient()

    async def process_query(self, query: str, property_id: str):
        # 1. Infer GA4 parameters using LLM
        plan = self._infer_plan_with_llm(query)
        if not plan:
            return "I could not understand how to query GA4 for that request."
        
        logger.debug(f"Raw GA4 Plan: {plan}")
        
        # 2. Validate plan against allowlist
        validated_plan = self._validate_plan(plan)
        if not validated_plan.get('metrics'):
            return "None of the inferred metrics are valid for GA4. Please try rephrasing your query."
            
        logger.debug(f"Validated GA4 Plan: {validated_plan}")

        # 3. Construct Request
        request = self._build_request(property_id, validated_plan)

        # 4. Execute Request
        try:
            client = self._get_client()
            response = client.run_report(request)
        except Exception as e:
            return f"Error executing GA4 query: {str(e)}"

        # 5. Summarize results
        summary = self._summarize_response(query, response)
        return summary

    def _validate_plan(self, plan: GA4QueryPlan) -> dict:
        """Validate and filter plan against safe allowlists."""
        validated = {}
        
        # Validate metrics (access Pydantic model attributes directly)
        raw_metrics = plan.metrics
        valid_metrics = [m for m in raw_metrics if m in ALLOWED_METRICS]
        invalid_metrics = [m for m in raw_metrics if m not in ALLOWED_METRICS]
        
        if invalid_metrics:
            logger.warning(f"Filtered out invalid metrics: {invalid_metrics}")
        
        validated['metrics'] = valid_metrics
        
        # Validate dimensions
        raw_dimensions = plan.dimensions
        valid_dimensions = [d for d in raw_dimensions if d in ALLOWED_DIMENSIONS]
        invalid_dimensions = [d for d in raw_dimensions if d not in ALLOWED_DIMENSIONS]
        
        if invalid_dimensions:
            logger.warning(f"Filtered out invalid dimensions: {invalid_dimensions}")
            
        validated['dimensions'] = valid_dimensions
        
        # Pass through date ranges (convert Pydantic models to dicts)
        validated['date_ranges'] = [dr.model_dump() for dr in plan.date_ranges]
        
        # Pass through order_by if fields are valid
        if plan.order_by:
            valid_order = []
            for o in plan.order_by:
                if o.field in ALLOWED_METRICS or o.field in ALLOWED_DIMENSIONS:
                    valid_order.append(o.model_dump())
                else:
                    logger.warning(f"Filtered out invalid order_by field: {o.field}")
            if valid_order:
                validated['order_by'] = valid_order
        
        return validated

    def _infer_plan_with_llm(self, query: str) -> GA4QueryPlan | None:
        """Use LLM with structured output to infer GA4 query parameters."""
        prompt = f"""You are a Google Analytics 4 (GA4) expert. 
User Query: "{query}"

Extract the parameters to query GA4 Data API:
- metrics: List of metric names (e.g., "activeUsers", "screenPageViews", "sessions")
- dimensions: List of dimension names (e.g., "date", "pagePath", "country")
- date_ranges: List of date ranges with start_date and end_date (YYYY-MM-DD or relative like "7daysAgo", "yesterday")
- order_by: Optional list of ordering with field name and desc (true/false)

IMPORTANT: Use standard GA4 API metric and dimension names:
- For users: activeUsers, newUsers, totalUsers
- For views: screenPageViews
- For sessions: sessions, engagedSessions
- For pages: pagePath, pageTitle
- For traffic: sessionSource, sessionMedium"""
        
        try:
            result = llm_client.chat_structured(
                [{"role": "user", "content": prompt}],
                response_model=GA4QueryPlan,
                model="gemini-2.5-flash"
            )
            return result
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return None

    def _build_request(self, property_id: str, plan: dict):
        date_ranges = [DateRange(start_date=d['start_date'], end_date=d['end_date']) for d in plan.get('date_ranges', [])]
        metrics = [Metric(name=m) for m in plan.get('metrics', [])]
        dimensions = [Dimension(name=d) for d in plan.get('dimensions', [])]
        
        # Basic OrderBy implementation
        order_bys = []
        if 'order_by' in plan:
            for o in plan['order_by']:
                field = o['field']
                desc = o.get('desc', True)
                # Determine if it's a metric or dimension orderby
                if field in ALLOWED_METRICS:
                    order_bys.append(OrderBy(metric=OrderBy.MetricOrderBy(metric_name=field), desc=desc))
                else:
                    order_bys.append(OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name=field), desc=desc))

        return RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=date_ranges,
            dimensions=dimensions,
            metrics=metrics,
            order_bys=order_bys
        )

    def _summarize_response(self, query: str, response):
        # Convert response to text format for LLM summary
        data_text = "GA4 Report:\n"
        
        # Headers
        headers = [h.name for h in response.dimension_headers] + [h.name for h in response.metric_headers]
        data_text +=  " | ".join(headers) + "\n"
        
        # Rows
        for row in response.rows:
            values = [v.value for v in row.dimension_values] + [v.value for v in row.metric_values]
            data_text += " | ".join(values) + "\n"
            
        if not response.rows:
            data_text += "No data returned.\n"

        prompt = f"""
        User Query: "{query}"
        Data Context:
        {data_text}
        
        Provide a concise natural language answer to the user's query based on the data above.
        If the data is empty, explain that no data was found for the requested period.
        """
        
        return llm_client.chat([{"role": "user", "content": prompt}], model="gemini-2.5-flash")

analytics_agent = AnalyticsAgent()
