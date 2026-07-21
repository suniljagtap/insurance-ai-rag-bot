import shutil
from pathlib import Path
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from app.agents.rag_agents import run_insurance_agent

router = APIRouter(prefix="/api/v1/user")


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    response: str


@router.post("/query", response_model=QueryResponse)
def get_text_query_response(request: QueryRequest):

    try:
        # call service
        print(request.query)
        print("LLM Agent called...")
        result = run_insurance_agent(request.query)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch response: {str(e)}",
        )

    return QueryResponse(response=result)