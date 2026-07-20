# Load the pdf file from data folder
# extract the content
# arrive at the chunking strategy

# Load the embedding model
# embed the chunks
# connect to postges and activate pgvector extension
# save the vector embeddings and original text in db

# uv add python-dotenv langchain-community pypdf
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
separators: list = ["\n\n", "\n", ". ", " "]  # put '##' at 2nd position

# ["##", "\n\n", "\n", ". ", " "]  # put '##' at 2nd position


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
    # quote = "Words are flowing out like endless rain into a paper cup,\nthey slither while they pass,\nthey slip away across the universe."
    chunks = splitter.split_documents(docs)
    # chunks = splitter.split_text(quote)
    # for i, doc in enumerate(chunks):
    #     print(len(doc.page_content), doc.page_content.replace("\n", " "))
    #     print("\n")
    # print([len(chunk["page_content"]) for chunk in chunks])
    return chunks


def ingest_pdf(filepath: str):
    """ingesting the document chunks in the vector db"""
    # 4 load the embedding model & 5 generate the embeddings
    # 6. save it in vector db
    chunks = document_splitter(filepath)
    print("ingestion started")
    vector_store = get_vector_store(
        collection_name="insurance_claim", pre_delete_collection=True
    )
    vector_store.add_documents(chunks)
    print("Ingestion Completed")


# def ingest_pdf_old(file_path: str):
#     """
#     function to ingest the pdf
#     """
#     print("Ingestion Started")
#     # 1 load pdf
#     loader = PyPDFLoader(file_path)
#     docs = loader.load()

#     # 2. Metadata enrichment (for citataion)
#     for i, doc in enumerate(docs):
#         doc.metadata.update(
#             {
#                 "source": file_path,
#                 "document_extension": "pdf",
#                 "page": doc.metadata.get("page"),
#                 "source_date": doc.metadata.get("creationdate", datetime.today),
#                 "last_updated": os.path.getmtime(file_path),
#                 "chunk_index": i,
#             }
#         )

#     # print(docs)
#     # print("Before Chunking")
#     ### testing
#     for doc in docs:
#         print(doc.metadata)
#         print("\n")

#     # 3. Chunking
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=800,  # upto 800 characters
#         chunk_overlap=160,  # upto 160 characters
#         separators=["\n\n", "\n", ". ", " "],
#     )

#     chunks = splitter.split_documents(docs)
#     print("Total Chunks")
#     print(len(chunks))
# max_length = max(len(chunk) for chunk in chunks)
# print("max length of chunk: ", max_length)

# 4 load the embedding model & 5 generate the embeddings
# 6. save it in vector db
# vector_store = get_vector_store(collection_name="insurance_claim")
# vector_store.add_documents(chunks)

# print("Ingestion Completed")


# ingest_pdf("data/Capstone_Project_4_Insurance_Claims_FAQ.pdf")
ingest_pdf("data/Capstone_Project_4_Insurance_Claims_FAQ.pdf")
# to run this try the following command (from the project root):
# uv run python -m app.ingestion.ingestion
# uv run python -m ingestion.ingestion
