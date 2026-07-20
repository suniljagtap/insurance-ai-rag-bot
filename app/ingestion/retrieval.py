# This example demonstrates hybrid retrival (vector and bm25/fts based search )
# This is good when you are looking for exact keyword based search
# So, we should build a hybrid retrieval that combines both vector search and keyword search (FTS)
# because we use pgvector
# RRF (needed to combine results and rerank them)
import re
import psycopg
import os
from core.db import get_vector_store
from langchain_community.retrievers import BM25Retriever
from langchain_openai import ChatOpenAI
from collections import defaultdict
from .ingestion import document_splitter

# from langchain.retrievers
from psycopg.rows import dict_row

# PGVector connection string uses SQLAlchemy format: postgresql+psycopg://...
# psycopg.connect needs standard format: postgresql://...
_raw_conn = os.getenv("PG_CONNECTION_STRING_FTS")

# hybrid searching (50/50) searching


# Perform cosine similarity vector search (Top-K = 5)
def vector_search(query, k=5, collection_name: str = "insurance_claim"):
    print("trying vector search, first method")
    print(query, collection_name)
    vector_store = get_vector_store(collection_name, pre_delete_collection=False)
    results = vector_store.similarity_search_with_score(query=query, k=k)

    ### testing
    document = [
        {"text": doc.page_content, "score": score, "metadata": doc.metadata}
        for doc, score in results
    ]

    return document


# convert consine distance into similarity score
def cosine_similarity_search(query, k=5, collection_name: str = "insurance_claim"):
    print("trying vector search")
    print(query, collection_name)
    vector_store = get_vector_store(collection_name, pre_delete_collection=False)
    results = vector_store.similarity_search_with_score(query=query, k=k)
    formatted_results = []

    for doc, distance in results:

        similarity = 1 - distance

        formatted_results.append(
            {
                "content": doc.page_content,
                "similarity": similarity,
                "metadata": doc.metadata,
            }
        )
    print("got documents")
    return formatted_results


def hybrid_search(
    query,
    vector_weight=0.5,
    bm25_weight=0.5,
    k=5,
    collection_name: str = "insurance_claim",
):
    chunks = document_splitter("data/Capstone_Project_4_Insurance_Claims_FAQ.pdf")
    bm25_retriever = BM25Retriever.from_documents(chunks)
    # Retrieve top 5 keyword matches
    bm25_retriever.k = 5
    # Vector Search
    vector_store = get_vector_store(collection_name, pre_delete_collection=False)
    vector_results = vector_store.similarity_search_with_score(query, k=k)
    # BM25 Search
    bm25_results = bm25_retriever.invoke(query)
    scores = defaultdict(lambda: {"vector_score": 0, "bm25_score": 0, "doc": None})
    # Normalize Vector Scores
    for doc, distance in vector_results:
        # pgvector returns distance
        # convert to similarity
        vector_score = 1 - distance
        key = doc.page_content
        scores[key]["vector_score"] = vector_score
        scores[key]["doc"] = doc
    # Normalize BM25 Scores
    max_bm25 = max([1 for _ in bm25_results], default=1)
    for rank, doc in enumerate(bm25_results):
        bm25_score = 1 / (rank + 1)
        key = doc.page_content
        scores[key]["bm25_score"] = bm25_score
        scores[key]["doc"] = doc
    # Hybrid scoring
    final_results = []
    for item in scores.values():
        hybrid_score = (
            vector_weight * item["vector_score"] + bm25_weight * item["bm25_score"]
        )

        final_results.append(
            {
                "document": item["doc"],
                "score": hybrid_score,
                "vector_score": item["vector_score"],
                "bm25_score": item["bm25_score"],
            }
        )
    # Sort highest score
    final_results.sort(key=lambda x: x["score"], reverse=True)
    return final_results[:k]


if __name__ == "__main__":

    # user_query = {
    #     "question": "Is this motor insurance claim eligible for coverage?",
    #     "claim_details": {
    #         "claim_id": "CLM001",
    #         "policy_id": "POL00234",
    #         "claim_type": "Motor",
    #         "incident_type": "Repair",
    #         "incident_date": "2026-02-10",
    #         "reported_delay_days": 2,
    #         "estimated_damage": 300000,
    #         "idv": 800000,
    #         "deductible": 10000,
    #         "previous_claims_90_days": 2,
    #         "documents_submitted": ["Policy Copy", "Repair Estimate"],
    #         "policy_status": "Active",
    #     },
    # }

    ### first method trying start
    # claim = user_query["claim_details"]

    # rag_query = f"""
    # Question:
    # {user_query["question"]}

    # Claim Details:
    # Claim Type: {claim["claim_type"]}
    # Incident Type: {claim["incident_type"]}
    # Incident Date: {claim["incident_date"]}
    # Reported Delay Days: {claim["reported_delay_days"]}
    # Estimated Damage: {claim["estimated_damage"]}
    # IDV: {claim["idv"]}
    # Deductible: {claim["deductible"]}
    # Previous Claims in 90 Days: {claim["previous_claims_90_days"]}
    # Policy Status: {claim["policy_status"]}
    # Documents Submitted: {", ".join(claim["documents_submitted"])}
    # """
    # results = vector_store.similarity_search_with_score(query=rag_query, k=5)

    ### first method trying end
    ### 2nd method
    # retrieval_query = user_query["question"]

    # vector_store = get_vector_store(
    #     collection_name="insurance_claim", pre_delete_collection=False
    # )
    # documents = vector_store.similarity_search(retrieval_query, k=5)

    # prompt = f"""
    # You are an insurance claim evaluator.

    # Use the policy documents below to decide eligibility.

    # Policy Documents:
    # {documents}

    # Claim Details:
    # {user_query["claim_details"]}

    # Question:
    # {user_query["question"]}

    # Provide:
    # 1. Eligibility decision
    # 2. Reasoning
    # 3. Relevant policy clauses
    # """
    ###2nd method end
    user_query = " Is a claim automatically rejected if fraud is suspected?"
    results = cosine_similarity_search(user_query)
    # print(type(results))
    # vector_search function
    # for doc in results:
    #     print(doc["text"].replace("\n", " "))
    #     print(doc["score"])
    # for cosine_similarity function
    # for doc in results:
    #     # print(doc)
    #     print(doc["content"].replace("\n", " "))
    #     print(doc["similarity"])
    # uv run python -m app.retrieval.retrieval_v2
    # uv run python -m ingestion.retrieval

    model = ChatOpenAI(model="gpt-5-mini")
    context = " ".join([item["content"] for item in results])
    prompt = f"""
    Answer the question using only the context.
    Context:
    {context}
    Question:
    {user_query}

    """
    response = model.invoke(prompt)
    print(response.content)

    # query = "What is the IRDAI-mandated maximum turnaround time for settling a health insurance claim? "

    # results = hybrid_search(query)
    # # for doc in results:
    # #     # print(doc)
    # #     print(doc["document"].page_content.replace("\n", " "))
    # #     print(doc["score"])
    # #     print(doc["vector_score"])
    # #     print(doc["bm25_score"])

    # # print(results)

    # # use retrieved doc for RAG
    # context = "\n\n".join(
    #     [r["document"].page_content.replace("\n", " ") for r in results]
    # )

    # from langchain_openai import ChatOpenAI

    # llm = ChatOpenAI(model="gpt-5-mini")
    # answer = llm.invoke(f"""
    # Answer using only this context:
    # {context}
    # Question:
    # {query}
    # """)
    # print(f"query is {query}")
    # print(answer.content)
