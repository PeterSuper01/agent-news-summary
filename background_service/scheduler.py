from apscheduler.schedulers.blocking import BlockingScheduler

from app.config import settings
from background_service.tasks import clear_expired_news, update_all_sections
from news.allowed_sections import allowed_sections


def create_news_update_scheduler(sections: list[str]):
    scheduler = BlockingScheduler()
    scheduler.add_job(
        update_all_sections,
        "interval",
        hours=settings.THEGUARDIAN_NEWS_UPDATE_INTERVAL_HOURS,
        id="update_all_sections",
        replace_existing=True,
        args=[sections],
    )
    return scheduler


def create_expired_news_cleanup_scheduler():
    scheduler = BlockingScheduler()
    scheduler.add_job(
        clear_expired_news,
        "interval",
        days=1,
        id="clear_expired_news",
        replace_existing=True,
    )
    return scheduler


if __name__ == "__main__":
    scheduler = create_news_update_scheduler(allowed_sections)
    scheduler.start()
