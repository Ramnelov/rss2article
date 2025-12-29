from openai import AsyncOpenAI

from rss2article.config import Settings

settings = Settings()

client = AsyncOpenAI(api_key=settings.openai_api_key)
