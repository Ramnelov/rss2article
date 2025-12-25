from __future__ import annotations

import re

from buzzter_agent.models import ArticleItem
from buzzter_agent.state import State

_WORD_RE = re.compile(r"\b\w+\b", re.UNICODE)


def _word_count(text: str) -> int:
    return len(_WORD_RE.findall(text or ""))


def qa_check(state: State):
    updated: list[ArticleItem] = []

    for item in state.items:
        if not item.relevant:
            updated.append(item)
            continue

        if not item.fulltext:
            item.qa_issues.append("precheck:missing_fulltext")
            updated.append(item)
            continue

        if item.notis is None:
            item.qa_issues.append("precheck:missing_notis")
            updated.append(item)
            continue

        body = (item.notis.body or "").strip()

        expected_tail = f"Källa: {item.notis.source.url} - {item.notis.source.date}."
        has_tail = body.endswith(expected_tail)
        if not has_tail:
            item.qa_issues.append("precheck:missing_or_wrong_source_line")

        main_body = body
        if has_tail:
            main_body = body[: -len(expected_tail)].rstrip()

        wc = _word_count(main_body)
        if wc < 130 or wc > 170:
            item.qa_issues.append(f"precheck:word_count_out_of_range:{wc}")

        quotes = item.notis.support_quotes or []
        if len(quotes) < 3 or len(quotes) > 5:
            item.qa_issues.append("precheck:support_quotes_count_invalid")

        for i, q in enumerate(quotes):
            q = (q or "").strip()
            if not q:
                item.qa_issues.append(f"precheck:empty_quote:{i}")
                continue
            if q not in item.fulltext:
                item.qa_issues.append(f"precheck:quote_not_in_source:{i}")

        updated.append(item)

    return {"items": updated}
