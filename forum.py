import requests

COMMENT_ENDPOINT = "https://api.investing.com/api/forum/post/comment"

class ForumApi:
    def __init__(self, session_id: str):
        self.session = requests.Session()
        self.session.cookies.set("ses_id",session_id)
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            ),
            "Content-Type": "application/json",
        })

    def post(
        self,
        target_id: str,
        permalink: str,
        text: str,
        parent_id: str = "",
    ):
        payload = {
            "platform": "desktop",
            "typeid": "5",
            "targetId": target_id,
            "parentId": parent_id,
            "image": "",
            "userAgent": self.session.headers["User-Agent"],
            "permalink": permalink,
            "text": text,
        }

        response = self.session.post(
            COMMENT_ENDPOINT,
            json=payload,
            timeout=10,
        )

        response.raise_for_status()
        return response.json()