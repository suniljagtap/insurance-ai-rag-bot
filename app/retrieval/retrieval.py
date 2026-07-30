import psycopg
import os
from app.core.db import get_vector_store
from langchain_community.retrievers import BM25Retriever
from langchain_openai import ChatOpenAI
from collections import defaultdict
from psycopg.rows import dict_row
from psycopg.errors import ConnectionTimeout

# from collections import defaultdict
# from app.ingestion import document_splitter, file_path
from app.ingestion.ingestion import document_splitter, file_path

# _raw_conn = os.getenv("PG_CONNECTION_STRING_FTS")
_raw_conn = (
    f"{os.getenv("PG_CONNECTION_STRING_FTS")}"
    f"?connect_timeout={os.getenv('PG_CONNECT_TIMEOUT', '3')}"
)
# chunks = document_splitter(file_path)
# bm25_retriever = BM25Retriever.from_documents(chunks)


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
    try:
        with psycopg.connect(_raw_conn, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql, {"query": query, "collection": collection_name, "k": k}
                )
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
    except ConnectionTimeout as exc:
        print(f"Connection could not be established due to {exc}")
        # raise TimeoutError(
        #     "Timed out connecting to the vector database after 5 seconds."
        # ) from exc
    except Exception as e:
        print(f"Error occured while doing FTS search due to {e}")


# Perform cosine similarity vector search (Top-K = 5)
def vector_search(query, k=5, collection_name: str = "insurance_claim"):
    try:
        print("Trying vector search")
        vector_store = get_vector_store(collection_name, pre_delete_collection=False)
        results = vector_store.similarity_search_with_score(query=query, k=k)

        document = [
            {"text": doc.page_content, "score": score, "metadata": doc.metadata}
            for doc, score in results
        ]

        return document
    except ConnectionTimeout as exc:
        print(f"Connection could not be established due to {exc}")
        # raise TimeoutError(
        #     "Timed out connecting to the vector database after 5 seconds."
        # ) from exc
    except Exception as e:
        print(f"Error occured while doing vector search due to {e}")


def hybrid_search(
    query,
    vector_weight=0.5,
    bm25_weight=0.5,
    k=5,
    collection_name: str = "insurance_claim",
):
    # Retrieve top 5 keyword matches
    chunks = document_splitter(file_path)
    bm25_retriever = BM25Retriever.from_documents(chunks)
    bm25_retriever.k = k
    try:
        # Vector Search
        vector_store = get_vector_store(collection_name, pre_delete_collection=False)
        vector_results = vector_store.similarity_search_with_score(query, k=k)
        # BM25 Search
        bm25_results = bm25_retriever.invoke(query)
    except Exception as e:
        print(f"Error occured while invoking query during hybrid search due to {e}")

    try:
        rrf_scores = {}
        chunk_map = {}
        for rank, (doc, score) in enumerate(vector_results):
            # Use the first 120 chars of the chunk text as an identity key.
            # Same chunk retrieved by both searches -> same key -> its scores add up.
            key = doc.page_content[:200]
            # RRF formula: score += 1 / (k_constant + rank). Better rank (smaller number)
            # gives a bigger score. .get(key, 0) lets us accumulate across both loops.
            rrf_scores[key] = rrf_scores.get(key, 0) + vector_weight / (60 + rank + 1)
            # Remember the full chunk so we can rebuild the final list from the winning keys.
            chunk_map[key] = {
                "content": doc.page_content,
                "metadata": doc.metadata,
            }
    except Exception as e:
        print(f"Error occured while doing hybrid search due to {e}")
    try:
        # Same pass over the FTS results. A chunk found by BOTH searches gets scored
        # twice here, which is exactly how RRF rewards agreement between the two methods.
        for rank, doc in enumerate(bm25_results):
            key = doc.page_content[:200]
            rrf_scores[key] = rrf_scores.get(key, 0) + bm25_weight / (60 + rank + 1)
            chunk_map[key] = {
                "content": doc.page_content,
                "metadata": doc.metadata,
            }

        # this line sorts the results of the RRF calculation so that,
        # the higher scoring doc/chunk appear at the very top of the final list
        ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        # print(ranked)
        return [chunk_map[key] for key, _ in ranked[:k]]

    except ConnectionTimeout as exc:
        print(f"Connection could not be established due to {exc}")
        # raise TimeoutError(
        #     "Timed out connecting to the vector database after 5 seconds."
        # ) from exc
    except Exception as e:
        print(f"Error occured while doing hybrid search due to {e}")

    # scores = defaultdict(lambda: {"vector_score": 0, "bm25_score": 0, "doc": None})
    # # Normalize Vector Scores
    # for doc, distance in vector_results:
    #     # pgvector returns distance
    #     # convert to similarity
    #     vector_score = 1 - distance
    #     key = doc.page_content
    #     scores[key]["vector_score"] = vector_score
    #     scores[key]["doc"] = doc
    # # Normalize BM25 Scores
    # for rank, doc in enumerate(bm25_results):
    #     bm25_score = 1 / (rank + 1)
    #     key = doc.page_content
    #     scores[key]["bm25_score"] = bm25_score
    #     scores[key]["doc"] = doc
    # # Hybrid scoring
    # final_results = []
    # for item in scores.values():
    #     hybrid_score = (
    #         vector_weight * item["vector_score"] + bm25_weight * item["bm25_score"]
    #     )

    #     final_results.append(
    #         {
    #             "document": item["doc"],
    #             "score": hybrid_score,
    #             "vector_score": item["vector_score"],
    #             "bm25_score": item["bm25_score"],
    #         }
    #     )
    # # Sort highest score
    # final_results.sort(key=lambda x: x["score"], reverse=True)
    # return final_results[:k]
