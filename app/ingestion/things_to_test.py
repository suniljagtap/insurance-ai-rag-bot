# Perform cosine similarity vector search (Top-K = 5)
def vector_search(query, k=5):

    results = vector_store.similarity_search_with_score(query=query, k=k)

    return results


# convert consine distance into similarity score
def cosine_similarity_search(query, k=5):

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

    return formatted_results


# Use retrieved chunks for RAG generation
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-5-mini")
context = "\n\n".join([item["content"] for item in results])
prompt = f"""
Answer the question using only the context.
Context:
{context}
Question:
{query}

"""
response = llm.invoke(prompt)
print(response.content)


## run this:
results = cosine_similarity_search("Explain embeddings", k=5)


for result in results:

    print("----------------")
    print("Similarity:", result["similarity"])

    print(result["content"])

# execute search with vector search
query = "How does semantic search work using embeddings?"


results = vector_search(query, k=5)


for doc, score in results:

    print("-------------------------")

    print("Cosine Distance:", score)

    print("Document:", doc.page_content)

    print("Metadata:", doc.metadata)

# Use retrieved chunks in your RAG pipeline

context = "\n\n".join([doc.page_content for doc, score in results])
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-5-mini")

prompt = f"""
Use the context below to answer the question.

Context:
{context}

Question:
{query}
"""

response = llm.invoke(prompt)
print(response.content)


# add metadata filtering
results = vector_store.similarity_search_with_score(
    query="Explain embeddings", k=5, filter={"source": "embeddings"}
)


### for BM25
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document

CONNECTION_STRING = "postgresql+psycopg2://postgres:password@localhost:5432/ragdb"
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
documents = [
    Document(
        page_content="RAG combines retrieval with generation to improve LLM responses.",
        metadata={"source": "rag"},
    ),
    Document(
        page_content="Vector databases store embeddings for semantic search.",
        metadata={"source": "vector"},
    ),
    Document(
        page_content="BM25 is a keyword based ranking algorithm used in information retrieval.",
        metadata={"source": "bm25"},
    ),
    Document(
        page_content="Embeddings convert text into numerical vectors.",
        metadata={"source": "embedding"},
    ),
    Document(
        page_content="Large language models use transformer architectures.",
        metadata={"source": "llm"},
    ),
]
vector_store = PGVector.from_documents(
    documents,
    embedding_model,
    collection_name="hybrid_rag",
    connection=CONNECTION_STRING,
    use_jsonb=True,
)
print("PGVector created")

# create retreiver
from langchain_community.retrievers import BM25Retriever

bm25_retriever = BM25Retriever.from_documents(documents)

# Retrieve top 5 keyword matches
bm25_retriever.k = 5


# hybrid searching (50/50) searching
from collections import defaultdict


def hybrid_search(query, vector_weight=0.5, bm25_weight=0.5, k=5):

    # -------------------------
    # Vector Search
    # -------------------------

    vector_results = vector_store.similarity_search_with_score(query, k=k)

    # -------------------------
    # BM25 Search
    # -------------------------

    bm25_results = bm25_retriever.invoke(query)

    scores = defaultdict(lambda: {"vector_score": 0, "bm25_score": 0, "doc": None})

    # -------------------------
    # Normalize Vector Scores
    # -------------------------

    for doc, distance in vector_results:

        # pgvector returns distance
        # convert to similarity

        vector_score = 1 - distance

        key = doc.page_content

        scores[key]["vector_score"] = vector_score
        scores[key]["doc"] = doc

    # -------------------------
    # Normalize BM25 Scores
    # -------------------------

    max_bm25 = max([1 for _ in bm25_results], default=1)

    for rank, doc in enumerate(bm25_results):

        # Reciprocal rank normalization

        bm25_score = 1 / (rank + 1)

        key = doc.page_content

        scores[key]["bm25_score"] = bm25_score
        scores[key]["doc"] = doc

    # -------------------------
    # Hybrid scoring
    # -------------------------

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


# run hybrid search
query = "How does semantic search work using embeddings?"
results = hybrid_search(query, vector_weight=0.5, bm25_weight=0.5, k=5)

for result in results:

    print("----------------------")
    print("Hybrid Score:", result["score"])
    print("Vector Score:", result["vector_score"])
    print("BM25 Score:", result["bm25_score"])
    print(result["document"].page_content)


# use retrieved doc for RAG
context = "\n\n".join([r["document"].page_content for r in results])

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-5-mini")
answer = llm.invoke(f"""
Answer using only this context:
{context}
Question:
{query}
""")
print(answer.content)



# for claim
retrieval_query = user_query["question"]

documents = vector_store.similarity_search(
    retrieval_query,
    k=5
)

prompt = f"""
You are an insurance claim evaluator.

Use the policy documents below to decide eligibility.

Policy Documents:
{documents}

Claim Details:
{user_query["claim_details"]}

Question:
{user_query["question"]}

Provide:
1. Eligibility decision
2. Reasoning
3. Relevant policy clauses
"""