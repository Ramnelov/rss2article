from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class FeedItem(BaseModel):
    entry_id: str
    title: str
    link: str
    author: str
    published_at: datetime
    content_text: str
