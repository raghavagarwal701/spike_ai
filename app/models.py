
from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    query: str
    propertyId: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
