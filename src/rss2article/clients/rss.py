from __future__ import annotations

import hashlib
import logging

import feedparser

from rss2article.domain.models import FeedItem
from rss2article.utils.datetime import struct_time_to_utc_datetime
from rss2article.utils.html import html_to_text

log = logging.getLogger(__name__)


def entry_id_from_link(link: str) -> str:
    return hashlib.sha256(link.encode("utf-8")).hexdigest()[:32]


def _extract_content_html(entry: feedparser.FeedParserDict) -> str | None:
    content = entry.get("content")
    if isinstance(content, list) and content:
        for part in content:
            if isinstance(part, dict):
                v = part.get("value")
                if isinstance(v, str) and v.strip():
                    return v

    dc = entry.get("dc_content")
    if isinstance(dc, str) and dc.strip():
        return dc
    if isinstance(dc, list) and dc:
        for part in dc:
            if isinstance(part, dict):
                v = part.get("value") or part.get("#text")
                if isinstance(v, str) and v.strip():
                    return v
            elif isinstance(part, str) and part.strip():
                return part

    summary = entry.get("summary")
    if isinstance(summary, str) and summary.strip():
        return summary

    description = entry.get("description")
    if isinstance(description, str) and description.strip():
        return description

    return None


def fetch_feed_items(feed_url: list[str]) -> list[FeedItem]:

    items: list[FeedItem] = []

    try:
        parsed = feedparser.parse(feed_url)
    except Exception as e:
        log.warning("Failed to parse feed %s: %s", feed_url, e)
        return []

    for entry in parsed.get("entries", []):

        link = entry.get("link")
        if not link:
            continue

        entry_id = entry_id_from_link(str(link))

        st = entry.get("published_parsed") or entry.get("updated_parsed")
        published_at = struct_time_to_utc_datetime(st) if st else None

        content = _extract_content_html(entry)

        if not content:
            continue

        content_text = html_to_text(content)

        try:
            item = FeedItem(
                entry_id=entry_id,
                title=entry.get("title"),
                link=link,
                author=entry.get("author"),
                published_at=published_at,
                content_text=content_text,
            )
        except Exception as e:
            log.warning(
                "Skipping invalid entry (feed=%s, link=%s): %s", feed_url, link, e
            )
            continue

        items.append(item)

    return items
