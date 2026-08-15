import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from config import BotConfig
from db import (
    BotInteraction,
    ForumMessage,
    InteractionStatus,
    ResponseType,
)
from forum import ForumApi
from response_generators import AIResponseGenerator, CommandResponseGenerator
from workers.base import Worker

REPLY_DELAY_SECONDS = 3


class ResponseWorker(Worker):
    def __init__(self, forum_api: ForumApi, config: BotConfig, db: Session):
        self.forum_api = forum_api
        self.config = config
        self.db = db
        self.command_response_generator = CommandResponseGenerator(config)
        self.ai_response_generator: AIResponseGenerator | None = None

    def _fetch_messages(self) -> list[ForumMessage]:
        processed_message = (
            select(BotInteraction.id)
            .where(BotInteraction.source_message_id == ForumMessage.id)
            .exists()
        )
        return list(
            self.db.scalars(
                select(ForumMessage).where(~processed_message)
            )
        )

    def _should_reply(self, message: ForumMessage) -> bool:
        return self.config.at_bot in message.content

    def _determine_response_type(self, message: ForumMessage) -> ResponseType:
        if self.config.at_bot not in message.content:
            return ResponseType.CONVERSATIONAL

        _, content_after_mention = message.content.split(
            self.config.at_bot,
            maxsplit=1,
        )
        if content_after_mention.lstrip().startswith(self.config.command_symbol):
            return ResponseType.COMMAND
        return ResponseType.CONVERSATIONAL

    def _generate_pending_interactions(self) -> int:
        interactions: list[BotInteraction] = []

        for message in self._fetch_messages():
            response_type = self._determine_response_type(message)
            now = int(time.time())
            interactions.append(
                BotInteraction(
                    source_message_id=message.id,
                    status=InteractionStatus.AWAITING_REPLY,
                    response_type=response_type,
                    created_at=now,
                    updated_at=now,
                )
            )

        self.db.add_all(interactions)
        self.db.commit()
        return len(interactions)

    def _generate_responses(self) -> int:
        statement = (
            select(BotInteraction, ForumMessage)
            .join(
                ForumMessage,
                ForumMessage.id == BotInteraction.source_message_id,
            )
            .where(
                BotInteraction.status == InteractionStatus.AWAITING_REPLY,
                BotInteraction.response_text.is_(None),
            )
        )
        pending: list[tuple[BotInteraction, ForumMessage]] = list(
            self.db.execute(statement).tuples()
        )

        response_count = 0
        for interaction, message in pending:
            now = int(time.time())
            if not self._should_reply(message):
                interaction.status = InteractionStatus.SKIPPED
                interaction.updated_at = now
                self.db.commit()
                continue

            response_text = self._generate_response(message, interaction.response_type)
            if response_count:
                time.sleep(REPLY_DELAY_SECONDS)
            self.forum_api.reply(
                company_id=message.company_id,
                parent_message_id=message.id,
                content=response_text,
            )
            interaction.response_text = response_text
            interaction.status = InteractionStatus.REPLIED
            interaction.updated_at = now
            self.db.commit()
            response_count += 1

        return response_count

    def _generate_response(
        self,
        message: ForumMessage,
        response_type: ResponseType,
    ) -> str:
        if response_type is ResponseType.COMMAND:
            return self.command_response_generator.generate(message.content)

        if self.ai_response_generator is None:
            self.ai_response_generator = AIResponseGenerator()
        return self.ai_response_generator.generate(message.content)

    def run_iteration(self) -> int:
        pending_count = self._generate_pending_interactions()
        response_count = self._generate_responses()
        print(
            f"Queued {pending_count} interaction(s); "
            f"generated {response_count} response(s)",
            flush=True,
        )
        return response_count
