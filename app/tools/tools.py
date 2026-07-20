from typing import Final
from langchain_core.tools import tool

COLLECTION_NAME: Final = ""


@tool
def vector_search_tool(
    query: str, top_k: int = 5, collection_name: str = COLLECTION_NAME
) -> list:
    """
    Searches the PostegreSQL database. Use this for conceptual, semantic,
    conversational, or natural language insurance queries
    where the exact keywords don't matter, but the meaning does.
    Ideal for general coverage rules or scenarios exaplined in plain english.

    Args:
        query (str): User query to search for.
        top_k (int): Number of top results to return. Defaults to 5.

    Returns:
        list[dict[str, any]]: A list of dictionaries containing the retrieved
        document text, metadata.
    """

    print("Calling ==> vector_search_tool")
    print(f"Query : {query}")
    print("*****************")

    return [{"content": "Final Vector search results."}]


@tool
def fts_search_tool(
    query: str, top_k: int = 5, collection_name: str = COLLECTION_NAME
) -> list:
    """
    queary contains specific keywords or patterns

    Args:
        query (str): User query to search for.
        top_k (int): Number of top results to return. Defaults to 5.

    Returns:
        list[dict[str, any]]: A list of dictionaries containing the retrieved
        document text, metadata.
    """

    print("Calling ==> fts_search_tool")
    print(f"Query : {query}")
    print("*****************")

    return [{"content": "FTS Vector search results."}]


@tool
def hybrid_search_tool(
    query: str, top_k: int = 5, collection_name: str = COLLECTION_NAME
) -> list:
    """
    Query is combination of the simple text and also contains any specific keywords or patterns.

    Args:
        query (str): User query to search for.
        top_k (int): Number of top results to return. Defaults to 5.

    Returns:
        list[dict[str, any]]: A list of dictionaries containing the retrieved
        document text, metadata.
    """

    print("Calling ==> hybrid_search_tool")
    print(f"Query : {query}")
    print("*****************")

    return [{"content": "Final Hybrid search results."}]


search_tools = [vector_search_tool, fts_search_tool, hybrid_search_tool]
