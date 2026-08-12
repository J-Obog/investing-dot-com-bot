import requests

COMMENT_ENDPOINT = "https://api.investing.com/api/forum/post/comment"

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

    def post(self, forum_id: str, content: str, parent_id: str = ""):
        payload = {
            "platform": "desktop",
            "typeid": "5",
            "targetId": forum_id,
            "parentId": parent_id,
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

        print("STATUS:", response.status_code)
        print("BODY:", response.text)

        response.raise_for_status()

        return response.json()