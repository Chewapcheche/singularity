"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class BotConfig:
    bot_token: str
    admin_telegram_id: int | None
    content_file: Path
    media_root: Path


def _resolve_path(value: str, *, default: str) -> Path:
    path = Path(value or default)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def load_config() -> BotConfig:
    """Load bot settings from environment variables."""
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is required. Create it with @BotFather and set the environment variable.")

    admin_raw = os.getenv("ADMIN_TELEGRAM_ID", "").strip()
    admin_id = int(admin_raw) if admin_raw else None

    return BotConfig(
        bot_token=token,
        admin_telegram_id=admin_id,
        content_file=_resolve_path(os.getenv("CONTENT_FILE", ""), default="content/guide.json"),
        media_root=_resolve_path(os.getenv("MEDIA_ROOT", ""), default="media"),
    )
