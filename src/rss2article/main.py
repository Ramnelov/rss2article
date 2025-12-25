import asyncio

from rss2article.config import Settings
from rss2article.db.engine import create_engine
from rss2article.db.session import create_sessionmaker
from rss2article.services.ingest import ingest_feeds


def main() -> int:
    settings = Settings()
    engine = create_engine(settings)
    SessionLocal = create_sessionmaker(engine)

    asyncio.run(
        ingest_feeds(
            [
                "https://techradar.com/rss",
                "http://www.reddit.com/r/MachineLearning/.rss",
                "http://neurosciencenews.com/feed/",
            ],
            SessionLocal,
        )
    )
    return 0
