from __future__ import annotations

from newspaper import Article  # type: ignore[import-untyped]

from buzzter_agent.state import State


def fetch_fulltext(state: State):
    updated = []

    for item in state.items:
        if not item.relevant:
            updated.append(item)
            continue

        try:
            art = Article(item.url)
            art.download()
            art.parse()
            item.fulltext = (art.text or "").strip()
        except Exception as e:
            item.qa_issues.append(f"fulltext_fetch_failed: {type(e).__name__}")

        # basic guard: too short to summarize safely
        if len(item.fulltext) < 800:
            item.qa_issues.append("fulltext_too_short")

        updated.append(item)

    return {"items": updated}
