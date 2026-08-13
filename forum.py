from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import re

import requests

COMMENT_ENDPOINT = "https://api.investing.com/api/forum/post/comment"
BASE_FORUM_MESSAGES_API = "https://www.investing.com/_next/data/4edcd31/equities"
REPLIES_ENDPOINT = "https://api.investing.com/api/forum/replies"

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
    #image: str
    profile_href: str
    shown_name: str
    nickname: str

    @classmethod
    def from_dict(cls, data: dict) -> "ForumUser":
        return cls(
            user_id=data["userID"],
            first_name=data["userFirstName"],
            last_name=data["userLastName"],
            #image=data["userImage"],
            profile_href=data["memberProfileHref"],
            shown_name=data["shownName"],
            nickname=data["nickName"],
        )

@dataclass
class ForumPost:
    id: str
    total_replies: int
    parent_id: str
    text: str
    date: datetime
    #image: str
    user: ForumUser
    likes: int
    dislikes: int
    #replies: list["ForumPost"] = field(default_factory=list)

    @classmethod
    def from_dict(
        cls,
        data: dict,
        reference_time: datetime | None = None,
    ) -> "ForumPost":
        reference_time = reference_time or datetime.now()
        return cls(
            id=data["id"],
            parent_id=data["parentId"],
            text=data["text"],
            date=cls._parse_date(data["date"], reference_time),
            #image=data["image"],
            user=ForumUser.from_dict(data["user"]),
            total_replies=data["totalReplies"],
            likes=data["likes"],
            dislikes=data["dislikes"],
            #replies=[
            #    cls.from_dict(reply, reference_time) for reply in data["replies"]
            #],
        )

    @staticmethod
    def _parse_date(value: str, reference_time: datetime) -> datetime:
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass

        if value.lower() == "just now":
            return reference_time

        relative_date = re.fullmatch(
            r"(\d+)\s+(minute|hour|day)s?\s+ago",
            value,
            flags=re.IGNORECASE,
        )
        if relative_date:
            amount = int(relative_date.group(1))
            unit = relative_date.group(2).lower()
            return reference_time - timedelta(**{f"{unit}s": amount})

        raise ValueError(f"Unsupported forum date format: {value!r}")


@dataclass
class ForumReplyUser:
    user_id: int
    first_name: str
    last_name: str
    shown_name: str
    nickname: str
    company_profile_logo: str
    local_id: int
    user_type: str
    user_status: str
    user_gender: str
    image: str
    profile_href: str
    company_country_id: int

    @classmethod
    def from_dict(cls, data: dict) -> "ForumReplyUser":
        return cls(
            user_id=data["user_ID"],
            first_name=data["user_firstname"],
            last_name=data["user_lastname"],
            shown_name=data["shownName"],
            nickname=data["nick_name"],
            company_profile_logo=data["company_profile_logo"],
            local_id=data["local_ID"],
            user_type=data["user_type"],
            user_status=data["user_status"],
            user_gender=data["user_gender"],
            image=data["user_image"],
            profile_href=data["member_profile_href"],
            company_country_id=data["company_country_ID"],
        )


@dataclass
class ForumReply:
    id: int
    more_replies: int
    parent_id: int
    position: int
    user_id: int
    text: str
    date: datetime
    date_formatted: str
    image: str
    image_alt: str
    likes: int
    dislikes: int
    href: str
    title: str
    tooltip: str
    user: ForumReplyUser
    user_image: str
    is_pro_user: bool

    @classmethod
    def from_dict(cls, data: dict) -> "ForumReply":
        return cls(
            id=data["id"],
            more_replies=data["more_replies"],
            parent_id=data["parent_id"],
            position=data["position"],
            user_id=data["user_id"],
            text=data["text"],
            date=datetime.fromtimestamp(data["date"], tz=timezone.utc),
            date_formatted=data["date_formatted"],
            image=data["image"],
            image_alt=data["image_alt"],
            likes=data["likes"],
            dislikes=data["dislikes"],
            href=data["href"],
            title=data["title"],
            tooltip=data["tooltip"],
            user=ForumReplyUser.from_dict(data["user"]),
            user_image=data["user_image"],
            is_pro_user=data["is_pro_user"],
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


    def fetch_post_replies(
        self,
        comment_id: str,
        limit: int,
        offset: int,
    ) -> list[ForumReply]:
        params = {"commentid": comment_id, "limit": limit, "offset": offset}
        response = self.session.get(
            REPLIES_ENDPOINT,
            params,
            timeout=10,
        )
        response.raise_for_status()
        return [
            ForumReply.from_dict(reply)
            for reply in response.json()["replies"]
        ]

    def fetch_posts(
        self,
        company_slug: str,
        asset_type: str,
        page: int = 1,
    ) -> list[ForumPost]:
        url = f"{BASE_FORUM_MESSAGES_API}/{company_slug}-commentary/{page}.json"
        response = self.session.get(
            url,
            params=[
                (asset_type, f"{company_slug}-commentary"),
                (asset_type, str(page)),
            ],
            timeout=10,
        )
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
