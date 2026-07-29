import shutil
from typing import Any, Dict
from pathlib import Path
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status, Body
from app.agents.rag_agents import run_insurance_agent

router = APIRouter(prefix="/api/v1/user")


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    response: str


class JsonQueryRequest(BaseModel):
    query: str
    claimDetails: Dict[str, Any]


@router.post("/query", response_model=QueryResponse)
def get_text_query_response(request: QueryRequest):

    try:
        # call service
        print(request.query)
        print("LLM Agent called...")
        result = run_insurance_agent(query=request.query)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch response: {str(e)}",
        )

    return QueryResponse(response=result)


@router.post("/claimQuery", response_model=QueryResponse)
def get_text_query_response(request: JsonQueryRequest):

    try:
        # call service
        print(request.query)
        print("LLM Agent called...")
        result = run_insurance_agent(request.query, request.claimDetails)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch response: {str(e)}",
        )

    return QueryResponse(response=result)
