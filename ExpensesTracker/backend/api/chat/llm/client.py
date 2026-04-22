import os
from typing import Optional
from openai import OpenAI

client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL", "http://host.docker.internal:11434/v1"),
    api_key=os.getenv("LLM_API_KEY", "ollama"),
)

DEFAULT_MODEL = os.getenv("LLM_MODEL", "qwen3:4b")


def chat(messages: list[dict], model: Optional[str] = None) -> str:
    response = client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
        extra_body={"think": False},
    )
    return response.choices[0].message.content