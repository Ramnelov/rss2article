from __future__ import annotations

import re

from bs4 import BeautifulSoup

_WHITESPACE_RE = re.compile(r"\s+")


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text(separator=" ", strip=True)
    return _WHITESPACE_RE.sub(" ", text).strip()
