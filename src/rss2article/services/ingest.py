from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from rss2article.clients.rss import fetch_feed_items
from rss2article.db.repositories.feed_items import upsert_feed_item
from rss2article.db.repositories.feeds import get_or_create_feed


async def ingest_feeds(
    feed_urls: list[str], SessionLocal: async_sessionmaker[AsyncSession]
) -> None:
    for feed_url in feed_urls:
        items = fetch_feed_items(feed_url)

        async with SessionLocal() as session:
            async with session.begin():
                feed = await get_or_create_feed(session, feed_url)
                for item in items:
                    await upsert_feed_item(session, feed.id, item)
