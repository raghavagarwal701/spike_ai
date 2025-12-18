import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("server.log")
    ]
)
logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException
from app.models import QueryRequest, QueryResponse
from app.orchestrator import orchestrator
from app.llm.client import llm_client

app = FastAPI()

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    try:
        # For now, just echo through orchestrator
        answer = await orchestrator.route_request(request)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}
