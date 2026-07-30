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
    claimDetails: dict


class ChatRequest(BaseModel):
    # session_id: str
    query: str
    claim_details: dict | None = None
    chat_history: list | None = None


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
def get_json_query_response(request: JsonQueryRequest):

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


@router.post("/chat", response_model=QueryResponse)
def get_chat_response(request: ChatRequest):

    try:
        # call service
        # print(request.query)
        print("Calling LLM Agent...")
        result = run_insurance_agent(
            request.query, request.claim_details, request.chat_history
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch response: {str(e)}",
        )

    return QueryResponse(response=result)
