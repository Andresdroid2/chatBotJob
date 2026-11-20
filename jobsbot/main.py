import logging

from telegram.ext import Application

from .bot import check_jobs, register_handlers
from .config import load_settings
from .db import init_db


def build_application(token: str, database_url: str, interval_minutes: int) -> Application:
    application = Application.builder().token(token).build()
    application.bot_data["session_factory"] = init_db(database_url)
    register_handlers(application)
    application.job_queue.run_repeating(check_jobs, interval=interval_minutes * 60, first=10)
    return application


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    settings = load_settings()
    application = build_application(
        settings.telegram_token, settings.database_url, settings.check_interval_minutes
    )
    application.run_polling()