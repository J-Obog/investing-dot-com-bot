import requests

COMMENT_ENDPOINT = "https://api.investing.com/api/forum/post/comment"
BASE_FORUM_MESSAGES_API = "https://www.investing.com/_next/data/4edcd31/equities"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/151.0.0.0 Safari/537.36"
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

    def fetch_posts(self, company_slug: str, page: int):
        url = f"{BASE_FORUM_MESSAGES_API}/{company_slug}-commentary/{page}.json?equity={company_slug}-commentary&equity={page}"
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        return (
            data["pageProps"]
                ["state"]
                ["forumStore"]
                ["comments"]
                ["_collection"]
        )


    def post(self, forum_id: str, content: str):
        self._post_message(forum_id, "", content)

    def reply(self, forum_id: str, parent_message_id: str, content: str):
        self._post_message(forum_id, parent_message_id, content)

    def _post_message(self, forum_id: str, parent_message_id: str, content: str):
        payload = {
            "platform": "desktop",
            "typeid": "5",
            "targetId": forum_id,
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