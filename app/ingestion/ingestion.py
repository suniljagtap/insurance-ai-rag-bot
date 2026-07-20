from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import date, datetime
from core.db import get_vector_store
import os

load_dotenv()


# constants
chunk_size: int = 800
chunk_overlap: int = 160
separators: list = ["\n\n", "\n", ". ", " "]
file_path = "data/Capstone_Project_4_Insurance_Claims_FAQ.pdf"


def load_document(filepath: str):
    """loads the given pdf"""
    print("loading the document")
    loader = PyPDFLoader(filepath)
    docs = loader.load()
    print("document loaded")
    return docs


def document_splitter(filepath: str):
    """splits the document with Recursive text splitter"""
    docs = load_document(filepath)

    # encriching the document metadata for citation
    for i, doc in enumerate(docs):
        doc.metadata.update(
            {
                "source": filepath,
                "document_extension": "pdf",
                "page": doc.metadata.get("page"),
                "source_date": doc.metadata.get("creationdate", datetime.today),
                "last_updated": os.path.getmtime(filepath),
                "chunk_index": i,
            }
        )

    print("Splitting the document with recursive strategy")
    # creating an instance of the splitter class
    splitter = RecursiveCharacterTextSplitter(
        separators=separators, chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    chunks = splitter.split_documents(docs)
    return chunks


def ingest_pdf(filepath: str):
    """ingesting the document chunks in the vector db"""
    # load the embedding model & generate the embeddings
    # save it in vector db
    chunks = document_splitter(filepath)
    print("ingestion started")
    vector_store = get_vector_store(
        collection_name="insurance_claim", pre_delete_collection=True
    )
    vector_store.add_documents(chunks)
    print("Ingestion Completed")


ingest_pdf(file_path)
# uv run python -m ingestion.ingestion
