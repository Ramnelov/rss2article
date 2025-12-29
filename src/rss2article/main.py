import asyncio

from rss2article.config import Settings
from rss2article.db.engine import create_engine
from rss2article.db.init_db import init_db
from rss2article.db.session import create_sessionmaker
from rss2article.services.ingest import ingest_feeds
from rss2article.services.relevance import classify_relevance


async def run() -> None:
    settings = Settings()
    engine = create_engine(settings)
    SessionLocal = create_sessionmaker(engine)

    feed_urls = [
        "https://www.butikstrender.se/feed/",
        "https://www.dagligvarunytt.se/rss.xml",
        "https://www.ehandel.se/feed",
        "https://www.market.se/rss.xml",
        "https://news.cision.com/ListItems?format=rss",
        "https://www.handelstrender.se/feed/",
        "https://www.retaildive.com/feeds/news/",
        "https://www.retailgazette.co.uk/feed/",
        "https://insideretail.asia/feed/",
    ]

    try:
        await init_db(engine)
        await ingest_feeds(
            feed_urls,
            SessionLocal,
        )
        await classify_relevance(
            feed_urls,
            SessionLocal,
        )
    finally:
        await engine.dispose()


def main() -> int:
    asyncio.run(run())
    return 0
