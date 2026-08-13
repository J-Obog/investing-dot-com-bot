from __future__ import annotations

from sqlalchemy import BigInteger, Integer, SmallInteger, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class ForumMessage(Base):
    __tablename__ = "forum_messages"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    company_id: Mapped[str] = mapped_column("companyid", String(255))
    user_id: Mapped[str] = mapped_column("userid", String(255))
    username: Mapped[str] = mapped_column(Text)
    parent_id: Mapped[str | None] = mapped_column("parentid", String(255))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[int] = mapped_column("createdat", BigInteger)


class BotInteraction(Base):
    __tablename__ = "bot_interactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source_message_id: Mapped[str] = mapped_column("sourcemessageid", String(255))
    status: Mapped[int] = mapped_column(SmallInteger)
    response_type: Mapped[str | None] = mapped_column("responsetype", Text)
    response_text: Mapped[str | None] = mapped_column("responsetext", Text)
    response_id: Mapped[str | None] = mapped_column("reponseid", String(255))
    model: Mapped[str | None] = mapped_column(Text)
    input_tokens: Mapped[int | None] = mapped_column("inputtokens", Integer)
    output_tokens: Mapped[int | None] = mapped_column("outputtokens", Integer)
    created_at: Mapped[int] = mapped_column("createdat", BigInteger)
    updated_at: Mapped[int] = mapped_column("updatedat", BigInteger)
