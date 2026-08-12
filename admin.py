import argparse
import json
import os

from dotenv import load_dotenv

from forum import ForumApi


def main() -> None:
    parser = argparse.ArgumentParser(description="Post a comment to the forum API.")
    parser.add_argument("--targetId", required=True, help="ID of the forum target")
    parser.add_argument("--content", required=True, help="Text to post")
    args = parser.parse_args()

    load_dotenv()
    session_id = os.getenv("FORUM_SESS_ID")
    if not session_id:
        parser.error("FORUM_SESS_ID is not set in the environment or .env file")

    forum = ForumApi(session_id)
    result = forum.post(
        forum_id=args.targetId,
        content=args.content,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
