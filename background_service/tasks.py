import time

from app.config import settings
from news.loader import TheGuardianLoader
from news.allowed_sections import allowed_sections
from database.db_maneger import db


def update_news_by_section(section: str):
    loader = TheGuardianLoader(api_key=settings.THEGUARDIAN_API_KEY)
    docs = loader.load(
        params={
            "page-size": settings.THEGUARDIAN_NEWS_UPDATE_PAGE_SIZE,
            "order-by": "newest",
        },
        section=section,
    )
    if len(docs) > 0:
        db.add_documents(docs)


def update_all_sections(sections: list[str]):
    for section in sections:
        try:
            update_news_by_section(section)
        except Exception as e:
            print(f"Error updating news for section {section}: {e}")


def clear_expired_news(days: int = 7):
    db.clear_expired_news(days=days)


if __name__ == "__main__":
    update_all_sections(allowed_sections)
