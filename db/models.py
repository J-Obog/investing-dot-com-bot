from __future__ import annotations

from enum import StrEnum

from sqlalchemy import BigInteger, Enum, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class InteractionStatus(StrEnum):
    AWAITING_REPLY = "awaiting_reply"
    REPLIED = "replied"
    SKIPPED = "skipped"


class ResponseType(StrEnum):
    COMMAND = "command"
    CONVERSATIONAL = "conversational"


def enum_values(enum_class: type[StrEnum]) -> list[str]:
    return [member.value for member in enum_class]


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
    source_message_id: Mapped[str] = mapped_column(
        "sourcemessageid",
        String(255),
        unique=True,
    )
    status: Mapped[InteractionStatus] = mapped_column(
        Enum(
            InteractionStatus,
            native_enum=False,
            create_constraint=False,
            values_callable=enum_values,
        )
    )
    response_type: Mapped[ResponseType] = mapped_column(
        "responsetype",
        Enum(
            ResponseType,
            native_enum=False,
            create_constraint=False,
            values_callable=enum_values,
        ),
    )
    response_text: Mapped[str | None] = mapped_column("responsetext", Text)
    response_message_id: Mapped[str | None] = mapped_column(
        "responsemessageid",
        String(255),
    )
    model: Mapped[str | None] = mapped_column(Text)
    input_tokens: Mapped[int | None] = mapped_column("inputtokens", Integer)
    output_tokens: Mapped[int | None] = mapped_column("outputtokens", Integer)
    created_at: Mapped[int] = mapped_column("createdat", BigInteger)
    updated_at: Mapped[int] = mapped_column("updatedat", BigInteger)
