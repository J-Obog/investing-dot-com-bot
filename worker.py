import re

from config import BotConfig
from forum import ForumApi, ForumPost

REPLY_PAGE_SIZE = 100

class Worker:
    def __init__(self, forum_api: ForumApi, config: BotConfig):
        self.forum_api = forum_api
        self.config = config

    @staticmethod
    def _count_mentions(items: list[ForumPost], mention: str) -> int:
        """Count exact-case, standalone mentions."""
        pattern = re.compile(
            rf"(?<![A-Za-z0-9_@]){re.escape(mention)}(?![A-Za-z0-9_])"
        )
        return sum(len(pattern.findall(item.text)) for item in items)

    def _fetch_all_replies(self, post: ForumPost) -> list[ForumPost]:
        replies: list[ForumPost] = []

        while len(replies) < post.total_replies:
            page = self.forum_api.fetch_post_replies(
                comment_id=post.id,
                limit=min(REPLY_PAGE_SIZE, post.total_replies - len(replies)),
                offset=len(replies),
            )
            if not page:
                break
            replies.extend(page)

        return replies

    def run_iteration(self) -> int:
        total = 0

        for forum in self.config.visible_forums:
            posts = self.forum_api.fetch_posts(
                company_slug=forum.company_slug,
                asset_type=forum.asset_type,
            )
            mentions = self._count_mentions(posts, self.config.at_bot)
            reply_count = 0
            for post in posts:
                if post.total_replies <= 0:
                    continue

                replies = self._fetch_all_replies(post)
                reply_count += len(replies)
                mentions += self._count_mentions(replies, self.config.at_bot)

            total += mentions
            print(
                f"{forum.company_slug} (company {forum.company_id}): "
                f"{mentions} mention(s) in {len(posts)} post(s) "
                f"and {reply_count} reply/replies",
                flush=True,
            )

        print(f"Total {self.config.at_bot} mentions: {total}", flush=True)
        return total
