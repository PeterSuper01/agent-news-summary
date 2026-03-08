from langchain_core.documents import Document

from app.config import settings


def format_news_articles(docs: list[Document]) -> str:
    formatted_results = []
    for i, doc in enumerate(docs):
        title = doc.metadata.get("title", "No title")
        date = doc.metadata.get("public_date_plain", "Unknown date")
        article_url = doc.metadata.get(
            "article_url", "https://www.theguardian.com/international"
        )
        content = doc.page_content[: settings.THEGUARDIAN_NEWS_SUMMARY_MAX_LENGTH]
        formatted_results.append(
            f"[News {i+1}] Title: {title}\nDate: {date}\nArticle URL: {article_url}\nContent: {content}\n---"
        )
    return "\n".join(formatted_results)
