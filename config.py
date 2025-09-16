import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class BotConfig:
    telegram_bot_token: str


def load_config() -> BotConfig:
    """Load configuration values from environment variables and .env file."""
    load_dotenv()
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not telegram_bot_token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is not set. Create a .env file with TELEGRAM_BOT_TOKEN=..."
        )
    return BotConfig(telegram_bot_token=telegram_bot_token)

