from __future__ import annotations

import logging
import os
import sys


def setup_logging(level: str | int | None = None) -> None:
    root = logging.getLogger()
    if root.handlers:
        return

    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO")

    if isinstance(level, str):
        level = level.upper()

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root.setLevel(level)
    root.addHandler(handler)
