from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from rss2article.clients.openai import client
from rss2article.db.mappers import orm_to_feed_item
from rss2article.db.repositories.feed_items import get_feed_items_by_entry_ids
from rss2article.db.repositories.relevance import (
    get_unclassified_feed_entry_ids_by_feed_url,
    upsert_relevance,
)
from rss2article.domain.models import FeedItem

log = logging.getLogger(__name__)


RELEVANCE_SYSTEM = (
    "Du är en noggrann nyhetsklassificerare för Buzzter.se för en svensk B2B-publik "
    "inom omvärldsbevakning och framtidsanalys. Bedöm ENDAST relevans utifrån texten. "
    "Gissa inte fakta. Svara med strikt JSON och inget annat."
)

RELEVANCE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "relevant": {"type": "boolean"},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "pest": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["Policy", "Ekonomi", "Socialt", "Teknik"],
            },
            "minItems": 0,
            "maxItems": 2,
        },
        "category": {
            "type": "string",
            "enum": [
                "Teknik",
                "Konsument",
                "Policy",
                "Ekonomi",
                "Arbetsliv",
                "Energi",
                "Säkerhet",
                "Övrigt",
            ],
        },
        "why": {"type": "string"},
        "must_have_evidence": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": 3,
        },
        "reject_reason": {"type": "string"},
    },
    "required": [
        "relevant",
        "confidence",
        "pest",
        "category",
        "why",
        "must_have_evidence",
        "reject_reason",
    ],
}


async def classify_with_llm(feed_item: FeedItem) -> tuple[bool, str]:
    published_date = feed_item.published_at.date().isoformat()  # YYYY-MM-DD
    article_text = (feed_item.content_text or "")[:8000]  # clip for cost/speed

    user_prompt = f"""
Uppgift: Bedöm om artikeln är relevant för Buzzter.

Relevans om minst ett gäller:
- PEST: Policy/Reglering
- PEST: Ekonomi/marknad/investeringar
- PEST: Sociala trender/konsumentbeteenden
- PEST: Teknik (AI, cyber, plattformar, industri/energi-tech, telekom, biotech)
- Tydlig B2B-implikation (bransch/värdekedja)

Ej relevant om:
- sport/underhållning utan trend-/policy-/marknadskoppling
- lokalt/isolering utan bredare implikation
- rykten/clickbait utan stöd i texten

Metadata:
- Title: {feed_item.title}
- Author: {feed_item.author}
- Publiceringsdatum: {published_date}
- URL: {feed_item.link}

Artikeltext:
\"\"\"{article_text}\"\"\"
""".strip()

    resp = await client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": RELEVANCE_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "buzzter_relevance",
                "strict": True,
                "schema": RELEVANCE_SCHEMA,
            }
        },
    )

    data = json.loads(resp.output_text)

    return bool(data["relevant"]), str(data["why"])


async def classify_relevance(
    feed_urls: list[str], SessionLocal: async_sessionmaker[AsyncSession]
) -> None:

    missing_ids: list[str] = []
    async with SessionLocal() as session:
        for feed_url in feed_urls:
            missing_ids.extend(
                await get_unclassified_feed_entry_ids_by_feed_url(session, feed_url)
            )
        feed_items_orm = await get_feed_items_by_entry_ids(session, missing_ids)
    feed_items = [orm_to_feed_item(o) for o in feed_items_orm]

    sem = asyncio.Semaphore(16)

    async def classify_one(item: FeedItem):
        async with sem:
            return await classify_with_llm(item)

    results = await asyncio.gather(*(classify_one(i) for i in feed_items))

    async with SessionLocal() as session:
        async with session.begin():
            for orm_item, (relevant, why) in zip(feed_items_orm, results, strict=True):
                why = (why or "").strip()[:2048] or "—"
                await upsert_relevance(
                    session,
                    feed_item_id=orm_item.id,
                    relevant=relevant,
                    why=why,
                )
