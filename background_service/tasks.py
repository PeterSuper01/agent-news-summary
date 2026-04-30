import logging

from app.config import settings
from news.loader import TheGuardianLoader
from news.allowed_sections import allowed_sections
from database.db_maneger import db

logger = logging.getLogger(__name__)


def update_news_by_section(section: str):
    logger.info("Fetching news for section: %s", section)
    loader = TheGuardianLoader(api_key=settings.THEGUARDIAN_API_KEY)
    docs = loader.load(
        params={
            "page-size": settings.THEGUARDIAN_NEWS_UPDATE_PAGE_SIZE,
            "order-by": "newest",
        },
        section=section,
    )
    logger.info("Fetched %d articles for section: %s", len(docs), section)
    if docs:
        db.add_documents(docs)
        logger.info("Updated %d docs for section: %s", len(docs), section)
    else:
        logger.info("No new docs for section: %s", section)


def update_all_sections(sections: list[str]):
    logger.info("Starting news update for %d sections", len(sections))
    for section in sections:
        try:
            logger.info("Updating section: %s", section)
            update_news_by_section(section)
        except Exception as e:
            logger.error("Failed to update section %s: %s", section, e, exc_info=True)
    logger.info("News update completed")


def clear_expired_news(days: int = 7):
    logger.info("Clearing news older than %d days", days)
    db.clear_expired_news(days=days)
    logger.info("Expired news cleanup completed")


if __name__ == "__main__":
    update_all_sections(allowed_sections)
