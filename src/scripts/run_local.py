from dotenv import load_dotenv

load_dotenv()

import hashlib
import json
import logging
from pathlib import Path

from buzzter_agent.graph import build_graph
from buzzter_agent.state import State

logger = logging.getLogger(__name__)


def main():
    rss_urls = [
        "https://techradar.com/rss",
        "http://www.reddit.com/r/MachineLearning/.rss",
    ]
    doc_limit = 50

    graph = build_graph()

    initial_state = State(rss_urls=rss_urls, doc_limit=doc_limit)
    out = graph.invoke(initial_state.model_dump())
    final_state = State.model_validate(out)

    generated = [item for item in final_state.items if item.notis is not None]
    if not generated:
        print("No generated notis found. (No relevant items or generation failed.)")
        print(f"Total items: {len(final_state.items)}")
        print(f"Relevant items: {sum(1 for i in final_state.items if i.relevant)}")
        return

    out_dir = Path("out")
    out_dir.mkdir(parents=True, exist_ok=True)

    for item in generated:
        notis = item.notis
        if notis is None:
            continue

        url = item.url or ""
        file_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()
        out_path = out_dir / f"{file_hash}.json"

        payload = {
            "url": item.url,
            "title": item.title,
            "published": item.published,
            "relevant": item.relevant,
            "relevance_why": item.relevance_why,
            "qa_issues": item.qa_issues,
            "notis": {
                "title": notis.title,
                "excerpt": notis.excerpt,
                "body": notis.body,
                "tags": notis.tags,
                "source": {
                    "name": notis.source.name,
                    "url": notis.source.url,
                    "date": notis.source.date,
                },
                "support_quotes": notis.support_quotes,
            },
        }

        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

    print(f"Wrote {len(generated)} generated items to {out_dir.resolve()}")


if __name__ == "__main__":
    main()
