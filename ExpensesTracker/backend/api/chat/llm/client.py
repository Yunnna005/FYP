import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from openai import OpenAI

# Load .env from the chat folder
chat_dir = Path(__file__).parent.parent
load_dotenv(chat_dir / ".env")


# Ollama Qwen3
client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL", "http://host.docker.internal:11434/v1"),
    api_key=os.getenv("LLM_API_KEY", "ollama"),
)

DEFAULT_MODEL = os.getenv("LLM_MODEL", "qwen3:1.7b")


def chat(messages: list[dict], model: Optional[str] = None) -> str:
    response = client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
    )
    return response.choices[0].message.content


# Gemini
_GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
GEMINI_MAX_TOKENS = int(os.getenv("GEMINI_MAX_TOKENS", "300"))


def gemini_chat(messages: list[dict], model: Optional[str] = None) -> str:
    if not _GEMINI_API_KEY:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. Add it to your .env file."
        )

    gemini_client = genai.Client(api_key=_GEMINI_API_KEY)

    system_parts, contents = [], []
    for msg in messages:
        if msg["role"] == "system":
            system_parts.append(msg["content"])
        elif msg["role"] == "user":
            contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
        elif msg["role"] == "assistant":
            contents.append({"role": "model", "parts": [{"text": msg["content"]}]})

    if not contents or contents[-1]["role"] != "user":
        raise ValueError("Last message must be from the user.")

    config = types.GenerateContentConfig(
        max_output_tokens=GEMINI_MAX_TOKENS,
        system_instruction="\n\n".join(system_parts) if system_parts else None,
    )

    response = gemini_client.models.generate_content(
        model=model or DEFAULT_GEMINI_MODEL,
        contents=contents,
        config=config,
    )
    return response.text
