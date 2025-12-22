from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from buzzter_agent.models import ArticleItem
from buzzter_agent.state import State


class RelevanceResult(BaseModel):
    relevant: bool
    why: str = Field(description="Short rationale in Swedish (1–2 sentences).")


def classify_relevance(state: State):
    llm = ChatOpenAI(model=state.model, temperature=0)
    llm_structured = llm.with_structured_output(RelevanceResult)

    items: list[ArticleItem] = []

    for doc in state.docs:
        url = str(
            doc.metadata.get("canonical_url")
            or doc.metadata.get("link")
            or doc.metadata.get("source")
            or ""
        )
        title = str(doc.metadata.get("title") or "")
        feed = str(doc.metadata.get("feed") or doc.metadata.get("feed_url") or "")
        published = str(
            doc.metadata.get("publish_date") or doc.metadata.get("published") or ""
        )

        text = (doc.page_content or "")[:4000]

        prompt = (
            "Decide whether this article is relevant for Buzzter.se.\n\n"
            "Target audience: Swedish B2B readers interested in market intelligence, trends, and foresight.\n"
            "Relevance signals: PEST (policy/economy/society/technology), regulation, macro/business impact.\n\n"
            "Return strictly according to the schema:\n"
            "- relevant: boolean\n"
            "- why: a short, neutral rationale IN SWEDISH (1–2 sentences)\n\n"
            f"Title: {title}\n"
            f"URL: {url}\n"
            f"Source (feed): {feed}\n"
            f"Date: {published}\n\n"
            "Article text:\n"
            f"{text}"
        )

        result_data = llm_structured.invoke(prompt)
        rr = RelevanceResult.model_validate(result_data)

        items.append(
            ArticleItem(
                url=url,
                title=title,
                feed=feed,
                published=published,
                relevant=bool(rr.relevant),
                relevance_why=rr.why.strip(),
            )
        )

    return {"items": items}
