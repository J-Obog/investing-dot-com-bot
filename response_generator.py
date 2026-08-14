from db import ForumMessage, ResponseType


class ResponseGenerator:
    def __init__(self):
        pass

    def generate_response(
        self,
        message: ForumMessage,
        response_type: ResponseType,
    ) -> str:
        return "Hey, I've been watching this stock too!"
