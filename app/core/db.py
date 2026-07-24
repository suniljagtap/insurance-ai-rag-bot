import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from psycopg import OperationalError
from psycopg.errors import ConnectionTimeout

# uv add langchain-openai

load_dotenv()

# PG_CONNECTION = os.getenv("PG_CONNECTION_STRING")
PG_CONNECTION = (
    f"{os.getenv("PG_CONNECTION_STRING")}"
    f"?connect_timeout={os.getenv('PG_CONNECT_TIMEOUT', '3')}"
)


def get_embeddings():
    try:
        return OpenAIEmbeddings(model=os.getenv("EMBEDDING_MODEL"), dimensions=1536)
    except Exception as e:
        print(f"Unable to create embeddings due to {e}")
        raise RuntimeError("Internal error") from e


def get_vector_store(collection_name: str, pre_delete_collection: bool = False):
    try:
        return PGVector(
            collection_name=collection_name,
            connection=PG_CONNECTION,
            embeddings=get_embeddings(),
            use_jsonb=True,  # for better querying during retrieval
            pre_delete_collection=pre_delete_collection,
        )
    except ConnectionTimeout as exc:
        print(f"Connection could not be established due to {exc}")
        # raise TimeoutError(
        #     "Timed out connecting to the vector database after 5 seconds."
        # ) from exc

    except Exception as e:
        print(f"Error facing when intializing PGVector due to {e}")
        raise RuntimeError("Internal error") from e
