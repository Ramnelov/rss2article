from __future__ import annotations

from langchain_core.documents import Document
from pydantic import BaseModel, Field

from buzzter_agent.models import ArticleItem


class State(BaseModel):
    rss_urls: list[str] = Field(default_factory=list)
    docs: list[Document] = Field(default_factory=list)

    items: list[ArticleItem] = Field(default_factory=list)

    doc_limit: int | None = None
    model: str = "gpt-4o-mini"
