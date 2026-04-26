import os
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).parent.parent.parent / ".env")

client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL", "http://host.docker.internal:11434/v1"),
    api_key=os.getenv("LLM_API_KEY", "ollama"),
)

DEFAULT_MODEL = os.getenv("LLM_MODEL", "qwen3:1.7b")

gemini_client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY"),
)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
GEMINI_MAX_TOKENS = int(os.getenv("GEMINI_MAX_TOKENS", "300"))


def chat(messages: list[dict], model: Optional[str] = None) -> str:
    response = client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
    )
    return response.choices[0].message.content


def chat_gemini(messages: list[dict], model: Optional[str] = None, max_tokens: Optional[int] = None) -> str:
    response = gemini_client.chat.completions.create(
        model=model or GEMINI_MODEL,
        messages=messages,
        max_tokens=max_tokens or GEMINI_MAX_TOKENS,
    )
    return response.choices[0].message.content


def chat_both(messages: list[dict]) -> dict[str, str]:
    """Run both local and Gemini models in parallel with the same messages."""
    results = {}
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(chat, messages): "local",
            executor.submit(chat_gemini, messages): "gemini",
        }
        for future in as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as e:
                results[key] = f"[Error: {e}]"
    return results