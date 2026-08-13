import re
import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from config import BotConfig, ForumConfig
from db import ForumMessage
from forum import ForumApi, ForumPost

REPLY_PAGE_SIZE = 100

class Worker:
    def __init__(
        self,
        forum_api: ForumApi,
        config: BotConfig,
        db: Session,
    ):
        self.forum_api = forum_api
        self.config = config
        self.db = db

    @staticmethod
    def _is_bot_mention(post: ForumPost, mention: str) -> bool:
        """Return whether a post contains an exact-case, standalone mention."""
        pattern = re.compile(
            rf"(?<![A-Za-z0-9_@]){re.escape(mention)}(?![A-Za-z0-9_])"
        )
        return pattern.search(post.text) is not None

    def _fetch_posts(self, forum: ForumConfig) -> list[ForumPost]:
        posts = self.forum_api.fetch_posts(
            company_slug=forum.company_slug,
            asset_type=forum.asset_type,
        )

        for post in posts.copy():
            offset = 0
            while offset < post.total_replies:
                replies = self.forum_api.fetch_post_replies(
                    comment_id=post.id,
                    limit=min(REPLY_PAGE_SIZE, post.total_replies - offset),
                    offset=offset,
                )
                if not replies:
                    break
                posts.extend(replies)
                offset += len(replies)

        return posts

    @staticmethod
    def _to_forum_message(post: ForumPost, company_id: str) -> ForumMessage:
        return ForumMessage(
            id=post.id,
            company_id=company_id,
            user_id=post.user.user_id,
            username=post.user.shown_name,
            parent_id=(None if post.parent_id in {"", "0"} else post.parent_id),
            content=post.text,
            created_at=int(time.time()),
        )

    def _insert_messages(self, messages: list[ForumMessage]) -> None:
        if not messages:
            return

        messages_by_id = {message.id: message for message in messages}
        existing_ids = set(
            self.db.scalars(
                select(ForumMessage.id).where(
                    ForumMessage.id.in_(messages_by_id)
                )
            )
        )
        self.db.add_all(
            message
            for message_id, message in messages_by_id.items()
            if message_id not in existing_ids
        )
        self.db.commit()

    def run_iteration(self) -> int:
        total = 0
        messages: list[ForumMessage] = []

        for forum in self.config.visible_forums:
            posts = self._fetch_posts(forum)
            mentioned_posts = [
                post
                for post in posts
                if self._is_bot_mention(post, self.config.at_bot)
            ]
            messages.extend(
                self._to_forum_message(post, forum.company_id)
                for post in mentioned_posts
            )
            mentions = len(mentioned_posts)
            total += mentions
            print(
                f"{forum.company_slug} (company {forum.company_id}): "
                f"{mentions} mention(s) in {len(posts)} post(s)",
                flush=True,
            )

        self._insert_messages(messages)
        print(f"Total {self.config.at_bot} mentions: {total}", flush=True)
        return total
