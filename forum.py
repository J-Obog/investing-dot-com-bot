from dataclasses import dataclass, field

import requests

COMMENT_ENDPOINT = "https://api.investing.com/api/forum/post/comment"
BASE_FORUM_MESSAGES_API = "https://www.investing.com/_next/data/4edcd31/equities"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/151.0.0.0 Safari/537.36"
)


@dataclass
class ForumUser:
    user_id: str
    first_name: str
    last_name: str
    image: str
    profile_href: str
    shown_name: str
    nickname: str

    @classmethod
    def from_dict(cls, data: dict) -> "ForumUser":
        return cls(
            user_id=data["userID"],
            first_name=data["userFirstName"],
            last_name=data["userLastName"],
            image=data["userImage"],
            profile_href=data["memberProfileHref"],
            shown_name=data["shownName"],
            nickname=data["nickName"],
        )

@dataclass
class ForumPost:
    id: str
    more_replies: int
    total_replies: int
    parent_id: str
    text: str
    date: str
    image: str
    user: ForumUser
    is_pro_user: bool
    user_id: str
    likes: int
    dislikes: int
    replies: list["ForumPost"] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "ForumPost":
        return cls(
            id=data["id"],
            more_replies=data["moreReplies"],
            total_replies=data["totalReplies"],
            parent_id=data["parentId"],
            text=data["text"],
            date=data["date"],
            image=data["image"],
            user=ForumUser.from_dict(data["user"]),
            is_pro_user=data["isProUser"],
            user_id=data["userId"],
            likes=data["likes"],
            dislikes=data["dislikes"],
            replies=[cls.from_dict(reply) for reply in data["replies"]],
        )

class ForumApi:
    def __init__(self, session_id: str):
        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
            "Domain-Id": "www",
            "Ses-Id": session_id,
            "Origin": "https://www.investing.com",
            "Referer": "https://www.investing.com/",
        })

    def fetch_posts(self, company_slug: str, page: int = 1) -> list[ForumPost]:
        url = f"{BASE_FORUM_MESSAGES_API}/{company_slug}-commentary/{page}.json?equity={company_slug}-commentary&equity={page}"
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        posts = (
            data["pageProps"]
                ["state"]
                ["forumStore"]
                ["comments"]
                ["_collection"]
        )
        return [ForumPost.from_dict(post) for post in posts]


    def post(self, company_id: str, content: str):
        self._post_message(company_id, "", content)

    def reply(self, company_id: str, parent_message_id: str, content: str):
        self._post_message(company_id, parent_message_id, content)

    def _post_message(self, company_id: str, parent_message_id: str, content: str):
        payload = {
            "platform": "desktop",
            "typeid": "5",
            "targetId": company_id,
            "parentId": parent_message_id,
            "image": "",
            "userAgent": USER_AGENT,
            "permalink":"",
            "text": content,
        }

        response = self.session.post(
            COMMENT_ENDPOINT,
            json=payload,
            timeout=10,
        )

        response.raise_for_status()
        return response.json()
