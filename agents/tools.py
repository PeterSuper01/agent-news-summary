from enum import Enum

from langchain_core.documents import Document
from langchain_core.tools import tool

from app.config import settings
from database.db_maneger import db
from news.allowed_sections import AllowedSectionInput, AllowedQueryInput
from news.format_utils import format_news_articles
from news.loader import TheGuardianLoader


@tool(args_schema=AllowedSectionInput)
def load_latest_news_from_the_guardian(section_input: AllowedSectionInput) -> str:
    """
    Fetch the lastest news articles from The Guardian for a given section.
    Include the title, public date, and body of the news article.
    Args:
        section_input: The section on the news website.
    Returns:
        A string containing the title, public date, and body of the news article.
    """
    try:
        loader = TheGuardianLoader(api_key=settings.THEGUARDIAN_API_KEY)
        docs = loader.load(
            params={"page-size": 5, "order-by": "newest"}, section=section_input.value
        )
        if not docs:
            return "No news articles found for the given section."
        return format_news_articles(docs)
    except Exception as e:
        return f"Error loading news articles: {e}"


@tool(args_schema=AllowedQueryInput)
def retrieve_news_from_vectorstore(
    query: str, section_input: AllowedSectionInput
) -> str:
    """
    Retrieve the news from the vectorstore.
    Args:
        query: The query to search the news.
        section_input: The section on the news website.
    Returns:
        A string containing the news articles.
    """
    docs = db.search(query, section_input, k=settings.VECTORSTORE_SEARCH_K)
    return format_news_articles(docs)
