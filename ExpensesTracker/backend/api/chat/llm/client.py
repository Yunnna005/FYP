import os
from openai import OpenAI

client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL"),
    api_key=os.getenv("LLM_API_KEY"),
)

DEFAULT_MODEL = os.getenv("LLM_MODEL", "qwen3:1.7b")


def chat(messages: list[dict], model: str | None = None) -> str:
    response = client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
    )
    return response.choices[0].message.content