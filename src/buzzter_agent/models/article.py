from __future__ import annotations

from pydantic import BaseModel, Field

from buzzter_agent.models.notis import BuzzterNotis


class ArticleItem(BaseModel):
    url: str
    title: str
    feed: str = ""
    published: str = ""

    # Relevance classification
    relevant: bool = False
    relevance_why: str = ""

    # Article content + generated output
    fulltext: str = ""
    notis: BuzzterNotis | None = None

    # QA notes (requirements misses, repair failures, etc.)
    qa_issues: list[str] = Field(default_factory=list)
