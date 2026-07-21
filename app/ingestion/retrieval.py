import psycopg
import os
from core.db import get_vector_store
from langchain_community.retrievers import BM25Retriever
from langchain_openai import ChatOpenAI
from collections import defaultdict
from psycopg.rows import dict_row

# from collections import defaultdict
from .ingestion import document_splitter, file_path

_raw_conn = os.getenv("PG_CONNECTION_STRING_FTS")


def fts_search(query: str, k=5, collection_name: str = "insurance_claim"):
    """Keyword search against the stored chunks using Postgres' tsvector/tsquery/ts_rank"""
    sql = """
       SELECT
           e.document                                               AS content,
           e.cmetadata                                              AS metadata,
           ts_rank(
               to_tsvector('english', e.document),
               plainto_tsquery('english', %(query)s)
           )                                                        AS fts_rank
       FROM  langchain_pg_embedding  e
       JOIN  langchain_pg_collection c ON c.uuid = e.collection_id
       WHERE c.name = %(collection)s
         AND to_tsvector('english', e.document)
             @@ plainto_tsquery('english', %(query)s)
       ORDER BY fts_rank DESC
       LIMIT %(k)s;
   """

    with psycopg.connect(_raw_conn, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"query": query, "collection": collection_name, "k": k})
            rows = cur.fetchall()

    output = [
        {
            "content": row["content"],
            "metadata": row["metadata"],
            "fts_rank": round(float(row["fts_rank"]), 4),
        }
        for row in rows
    ]

    # print(output)
    return output


# Perform cosine similarity vector search (Top-K = 5)
def vector_search(query, k=5, collection_name: str = "insurance_claim"):
    print("Trying vector search")
    print(query, collection_name)
    vector_store = get_vector_store(collection_name, pre_delete_collection=False)
    results = vector_store.similarity_search_with_score(query=query, k=k)

    document = [
        {"text": doc.page_content, "score": score, "metadata": doc.metadata}
        for doc, score in results
    ]

    return document


def hybrid_search(
    query,
    vector_weight=0.5,
    bm25_weight=0.5,
    k=5,
    collection_name: str = "insurance_claim",
):
    chunks = document_splitter(file_path)
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
