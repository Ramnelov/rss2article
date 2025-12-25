from __future__ import annotations

from pydantic import BaseModel, Field


class SourceInfo(BaseModel):
    name: str
    url: str
    date: str


class BuzzterNotis(BaseModel):
    title: str
    excerpt: str
    body: str
    tags: list[str] = Field(default_factory=list)
    source: SourceInfo
    support_quotes: list[str] = Field(
        default_factory=list,
        description="3–5 exact sentences/quotes copied verbatim from the source text (extractive support).",
    )
