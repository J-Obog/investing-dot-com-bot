import argparse
from dataclasses import asdict
import json
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from config import BotConfig
from forum import ForumApi
from bot_mention_ingestor import BotMentionIngestor


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage the forum API.")

    if len(sys.argv) > 1 and sys.argv[1] == "fetch":
        parser.add_argument("command", choices=["fetch"])
        parser.add_argument("company_slug", help="Company slug to fetch posts for")
        parser.add_argument("asset_type", help="Asset type query parameter")
    elif len(sys.argv) > 1 and sys.argv[1] == "replies":
        parser.add_argument("command", choices=["replies"])
        parser.add_argument("comment_id", help="ID of the comment")
        parser.add_argument("--limit", type=int, default=10)
        parser.add_argument("--offset", type=int, default=0)
    elif len(sys.argv) > 1 and sys.argv[1] == "worker":
        parser.add_argument("command", choices=["worker"])
        parser.add_argument(
            "iterations",
            type=positive_int,
            help="Number of worker iterations to run",
        )
        parser.add_argument(
            "--config",
            default="bot_config.json",
            help="Path to the bot configuration file (default: bot_config.json)",
        )
    else:
        parser.add_argument("--targetId", required=True, help="ID of the forum target")
        parser.add_argument("--content", required=True, help="Text to post")
        parser.add_argument("--replyTo", help="ID of the message to reply to")

    args = parser.parse_args()

    load_dotenv()
    session_id = os.getenv("FORUM_SESS_ID")
    if not session_id:
        parser.error("FORUM_SESS_ID is not set in the environment or .env file")

    forum = ForumApi(session_id)
    if getattr(args, "command", None) == "worker":
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            parser.error("DATABASE_URL is not set in the environment or .env file")

        engine = create_engine(
            make_url(database_url).set(drivername="postgresql+psycopg")
        )
        with Session(engine) as db:
            ingestor = BotMentionIngestor(
                forum,
                BotConfig.from_json(args.config),
                db,
            )
            for _ in range(args.iterations):
                ingestor.run_iteration()
        return

    if getattr(args, "command", None) == "fetch":
        result = forum.fetch_posts(
            company_slug=args.company_slug,
            asset_type=args.asset_type,
        )
        print(json.dumps([asdict(post) for post in result], indent=2, default=str))
        return

    if getattr(args, "command", None) == "replies":
        result = forum.fetch_post_replies(
            comment_id=args.comment_id,
            limit=args.limit,
            offset=args.offset,
        )
        print(json.dumps([asdict(reply) for reply in result], indent=2, default=str))
        return

    if args.replyTo:
        result = forum.reply(
            company_id=args.targetId,
            parent_message_id=args.replyTo,
            content=args.content,
        )
    else:
        result = forum.post(
            company_id=args.targetId,
            content=args.content,
        )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
