"""
Pydantic schemas for structured LLM outputs.
These models ensure reliable, type-safe responses from the LLM.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, List, Optional, Any


# ============== Orchestrator Schemas ==============

class IntentClassification(BaseModel):
    """Response schema for intent detection in the orchestrator."""
    intent: Literal["ANALYTICS", "SEO", "BOTH"] = Field(
        description="The classified intent: ANALYTICS for GA4 data, SEO for audit data, BOTH for combined queries"
    )


class DecomposedQuery(BaseModel):
    """Response schema for query decomposition in multi-agent scenarios."""
    analytics_query: str = Field(
        description="The specific question for the Analytics agent focusing on metrics like views, users, sessions"
    )
    seo_query: str = Field(
        description="The specific question for the SEO agent focusing on URL metadata, titles, descriptions"
    )
    output_format: Literal["json", "natural_language"] = Field(
        default="natural_language",
        description="Output format: 'json' if user explicitly requests JSON, otherwise 'natural_language'"
    )
    limit: int = Field(
        default=10,
        description="Number of results requested (default: 10)"
    )


# ============== Analytics Agent Schemas ==============

class DateRange(BaseModel):
    """Date range for GA4 queries."""
    start_date: str = Field(description="Start date in YYYY-MM-DD format or relative like '7daysAgo'")
    end_date: str = Field(description="End date in YYYY-MM-DD format or relative like 'yesterday'")


class OrderByField(BaseModel):
    """Order by specification for GA4 queries."""
    field: str = Field(description="Field name to order by (metric or dimension)")
    desc: bool = Field(default=True, description="True for descending order, False for ascending")

    @field_validator('field', mode='before')
    @classmethod
    def normalize_field_name(cls, v: Any, info) -> str:
        """Accept 'field' directly if provided."""
        return v
    
    def __init__(self, **data):
        # Handle 'field_name' as an alias for 'field'
        if 'field_name' in data and 'field' not in data:
            data['field'] = data.pop('field_name')
        super().__init__(**data)


class GA4QueryPlan(BaseModel):
    """Response schema for GA4 query planning."""
    metrics: List[str] = Field(
        description="List of GA4 metric names like 'activeUsers', 'screenPageViews', 'sessions'"
    )
    dimensions: List[str] = Field(
        default=[],
        description="List of GA4 dimension names like 'date', 'pagePath', 'country'"
    )
    date_ranges: List[DateRange] = Field(
        description="List of date ranges for the query"
    )
    order_by: Optional[List[OrderByField]] = Field(
        default=None,
        description="Optional ordering specification"
    )


# ============== SEO Agent Schemas ==============

class SEOCodeResponse(BaseModel):
    """Response schema for SEO code generation."""
    code: str = Field(
        description="Python code to execute. Must populate a 'result' variable with the final answer. Do not include markdown fencing."
    )
