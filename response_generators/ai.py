import os

from groq import Groq

DEFAULT_MODEL = "llama-3.3-70b-versatile"
SYSTEM_PROMPT = (
    "You are a helpful assistant responding to users on a stock market forum. "
    "Keep your response concise and use a single line of plain text."
)


class AIResponseGenerator:
    def __init__(
        self,
        client: Groq | None = None,
        model: str = DEFAULT_MODEL,
    ):
        self.client = client or Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = model

    def generate(self, content: str) -> str:
        completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
            model=self.model,
        )
        response_content = completion.choices[0].message.content
        if not response_content:
            raise ValueError("Groq returned an empty response")
        return " ".join(response_content.split())
