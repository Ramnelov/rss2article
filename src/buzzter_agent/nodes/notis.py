from __future__ import annotations

import json
import re

from langchain_openai import ChatOpenAI

from buzzter_agent.models import BuzzterNotis, SourceInfo
from buzzter_agent.state import State

FULLTEXT_MAX_CHARS = 12_000
MIN_SUPPORT_QUOTES = 3
MAX_SUPPORT_QUOTES = 5

_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def _date_only(value: str) -> str:
    m = _DATE_RE.search(value or "")
    return m.group(0) if m else (value or "")


def _split_sentences(text: str) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []

    parts = re.split(r"(?<=[.!?])\s+", text)
    sentences: list[str] = []

    for part in parts:
        raw = (part or "").strip()
        if not raw:
            continue

        # Reject chunks that look like multiple paragraphs/bullets
        if "\n" in raw or "\r" in raw:
            continue

        # Collapse weird spacing
        s = re.sub(r"\s+", " ", raw).strip()

        # Basic shape filters
        if len(s) < 40 or len(s) > 320:
            continue
        # Reject bullet-like lines.
        if s.startswith(("- ", "• ", "* ")):
            continue
        # Avoid quotes that start with a quote character.
        if s.lstrip().startswith(('"', "“", "”")):
            continue
        if not re.search(r"[.!?]$", s):
            continue

        sentences.append(s)

    return sentences


def _select_support_quotes(
    fulltext: str, *, min_quotes: int = 3, max_quotes: int = 5
) -> list[str]:
    sentences = _split_sentences(fulltext)
    if not sentences:
        return []

    with_numbers = [s for s in sentences if re.search(r"\d", s)]
    picked = with_numbers[:max_quotes]

    if len(picked) < min_quotes:
        for s in sentences:
            if s in picked:
                continue
            picked.append(s)
            if len(picked) >= min_quotes:
                break

    return picked[:max_quotes]


def generate_notis(state: State):
    # Lower temperature reduces drift (word count + quote fidelity).
    llm = ChatOpenAI(model=state.model, temperature=0)
    llm_structured = llm.with_structured_output(BuzzterNotis)

    updated = []
    for item in state.items:
        if not item.relevant:
            updated.append(item)
            continue

        if not item.fulltext:
            item.qa_issues.append("missing_fulltext")
            updated.append(item)
            continue

        publisher = item.feed or "Okänd källa"
        published_date = _date_only(item.published or "") or "Okänt datum"
        source_tail = f"Källa: {item.url} - {published_date}."

        selected_quotes = _select_support_quotes(
            item.fulltext, min_quotes=MIN_SUPPORT_QUOTES, max_quotes=MAX_SUPPORT_QUOTES
        )
        if len(selected_quotes) < MIN_SUPPORT_QUOTES:
            item.qa_issues.append("support_quotes_too_few")
            updated.append(item)
            continue

        prompt = (
            "You are an editor for Buzzter.se.\n\n"
            "Write a neutral Swedish news brief (nyhetsnotis) based ONLY on the provided source text.\n\n"
            "Requirements:\n"
            "- Output language: Swedish (title/excerpt/body must be Swedish)\n"
            "- body length: 130–170 words\n"
            "- Start with what happened (concrete, no preamble)\n"
            "- Include 1–2 key figures / concrete facts if present in the source text\n"
            "- No opinions, no analysis; keep a neutral tone\n"
            "- Hallucination guard: you MUST use the provided support quotes below.\n"
            "  * Do not modify them. Do not add/remove quotes.\n"
            "  * Write the notis so every claim is supported by these quotes (no invented facts).\n\n"
            "Return STRICT JSON according to the schema: title, excerpt, body, tags, source, support_quotes.\n"
            "Set source to:\n"
            f'name="{publisher}", url="{item.url}", date="{published_date}"\n\n'
            "Support quotes you MUST use (JSON array of strings):\n"
            f"{json.dumps(selected_quotes, ensure_ascii=False)}\n\n"
            "Source text (fulltext):\n"
            f"{item.fulltext[:FULLTEXT_MAX_CHARS]}"
        )

        data = llm_structured.invoke(prompt)
        notis = BuzzterNotis.model_validate(data)

        # Enforce source fields (don’t trust model fully)
        notis.source = SourceInfo(name=publisher, url=item.url, date=published_date)

        # Enforce support quotes (we provide them deterministically from fulltext).
        notis.support_quotes = selected_quotes

        # Append source line deterministically (never authored by the model).
        main_body = (notis.body or "").strip()
        notis.body = f"{main_body}\n{source_tail}" if main_body else source_tail

        item.notis = notis
        updated.append(item)

    return {"items": updated}
