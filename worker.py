import re
import time

from config import BotConfig
from forum import ForumApi, ForumPost


def count_mentions(posts: list[ForumPost], mention: str) -> int:
    """Count exact-case, standalone mentions."""
    pattern = re.compile(
        rf"(?<![A-Za-z0-9_@]){re.escape(mention)}(?![A-Za-z0-9_])"
    )
    return sum(len(pattern.findall(post.text)) for post in posts)


class Worker:
    def __init__(self, forum_api: ForumApi, config: BotConfig):
        self.forum_api = forum_api
        self.config = config

    def run_iteration(self) -> int:
        total = 0

        for forum in self.config.visible_forums:
            posts = self.forum_api.fetch_posts(
                company_slug=forum.company_slug,
                asset_type=forum.asset_type,
            )
            mentions = count_mentions(posts, self.config.at_bot)
            total += mentions
            print(
                f"{forum.company_slug} (company {forum.company_id}): "
                f"{mentions} mention(s) in {len(posts)} post(s)",
                flush=True,
            )

        print(f"Total {self.config.at_bot} mentions: {total}", flush=True)
        return total

    def run(self, iterations: int | None = None, interval: float = 60) -> None:
        iteration = 0
        while iterations is None or iteration < iterations:
            iteration += 1
            print(f"Polling iteration {iteration}", flush=True)
            self.run_iteration()

            if iterations is None or iteration < iterations:
                time.sleep(interval)
