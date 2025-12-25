from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from langchain_community.document_loaders import RSSFeedLoader
from langchain_core.documents import Document

from buzzter_agent.state import State


def canonical_url(url: str) -> str:
    try:
        parts = urlsplit(url)
        q = [
            (k, v)
            for (k, v) in parse_qsl(parts.query, keep_blank_values=True)
            if not k.lower().startswith("utm_")
        ]
        query = urlencode(q, doseq=True)
        return urlunsplit(
            (parts.scheme, parts.netloc, parts.path, query, parts.fragment)
        )
    except Exception:
        return url


def load_rss(state: State):
    loader = RSSFeedLoader(urls=state.rss_urls)
    docs: list[Document] = loader.load()

    seen: set[str] = set()
    deduped: list[Document] = []
    for d in docs:
        url = str(d.metadata.get("link") or d.metadata.get("source") or "")
        key = canonical_url(url)
        if not key or key in seen:
            continue
        seen.add(key)
        d.metadata["canonical_url"] = key
        deduped.append(d)

    if state.doc_limit is not None:
        deduped = deduped[: state.doc_limit]

    return {"docs": deduped}
