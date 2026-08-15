import os
from pathlib import Path

from groq import Groq

DEFAULT_MODEL = "llama-3.3-70b-versatile"


class AIResponseGenerator:
    def __init__(
        self,
        client: Groq | None = None,
        model: str = DEFAULT_MODEL,
    ):
        self.client = client or Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = model
        self.system_prompt = Path(__file__).with_name(
            "system_prompt.txt"
        ).read_text(encoding="utf-8")

    def generate(self, content: str) -> str:
        completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": content},
            ],
            model=self.model,
        )
        response_content = completion.choices[0].message.content
        if not response_content:
            raise ValueError("Groq returned an empty response")
        return " ".join(response_content.split())
