import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass(frozen=True)
class Settings:
    telegram_token: str
    database_url: str
    check_interval_minutes: int

def load_settings() -> Settings:
    load_dotenv()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token or token == "pega-aqui-tu-token":
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN in your .env file.")
    return Settings(
        telegram_token=token,
        database_url=os.environ.get("DATABASE_URL", "sqlite:///data/bot.db"),
        check_interval_minutes=int(os.environ.get("CHECK_INTERVAL_MINUTES", "360")),
    )