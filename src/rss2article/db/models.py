from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rss2article.db.base import Base


class FeedORM(Base):
    __tablename__ = "feeds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(
        String(2048), unique=True, index=True, nullable=False
    )

    items: Mapped[list["FeedItemORM"]] = relationship(
        back_populates="feed",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class FeedItemORM(Base):
    __tablename__ = "feed_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    feed_id: Mapped[int] = mapped_column(
        ForeignKey("feeds.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    feed: Mapped[FeedORM] = relationship(back_populates="items")

    entry_id: Mapped[str] = mapped_column(String(1024), nullable=False)
    link: Mapped[str] = mapped_column(String(2048), nullable=False)

    title: Mapped[str] = mapped_column(String(512), nullable=False)
    author: Mapped[str] = mapped_column(String(256), nullable=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    content_text: Mapped[str] = mapped_column(Text, nullable=False)

    relevance: Mapped["RelevanceORM | None"] = relationship(
        back_populates="feed_item",
        uselist=False,
        cascade="all, delete-orphan",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("feed_id", "entry_id", name="uq_feed_items_feed_id_entry_id"),
        UniqueConstraint("feed_id", "link", name="uq_feed_items_feed_id_link"),
        Index("ix_feed_items_feed_id_published_at", "feed_id", "published_at"),
    )


class RelevanceORM(Base):
    __tablename__ = "relevance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    feed_item_id: Mapped[int] = mapped_column(
        ForeignKey("feed_items.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    feed_item: Mapped["FeedItemORM"] = relationship(back_populates="relevance")

    relevant: Mapped[bool] = mapped_column(Boolean, nullable=False)

    why: Mapped[str] = mapped_column(String(2048), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
