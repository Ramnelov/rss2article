from __future__ import annotations

from rss2article.db.models import FeedItemORM
from rss2article.domain.models import FeedItem


def orm_to_feed_items(rows: list[FeedItemORM]) -> list[FeedItem]:
    return [
        FeedItem(
            entry_id=r.entry_id,
            title=r.title,
            link=r.link,
            author=r.author,
            published_at=r.published_at,
            content_text=r.content_text,
        )
        for r in rows
    ]
