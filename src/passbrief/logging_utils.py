"""Logging utilities for PassBrief."""

from __future__ import annotations

import logging
import os
from typing import Mapping

_LEVELS: Mapping[str, int] = {
    "full": logging.DEBUG,
    "critical": logging.WARNING,
    "silent": logging.ERROR,
}


def setup_logging(default_level: str | None = None) -> None:
    """Configure application logging based on the ``APP_LOG`` environment variable."""

    env_level = os.getenv("APP_LOG", "critical").lower()
    target = _LEVELS.get(default_level or env_level, logging.WARNING)
    logging.basicConfig(
        level=target,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
