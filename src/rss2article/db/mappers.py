from __future__ import annotations

from rss2article.db.models import FeedItemORM
from rss2article.domain.models import FeedItem


def orm_to_feed_item(row: FeedItemORM) -> FeedItem:
    return FeedItem(
        entry_id=row.entry_id,
        title=row.title,
        link=row.link,
        author=row.author,
        published_at=row.published_at,
        content_text=row.content_text,
    )
