#https://ollama.com/library/qwen3

from api.chat.llm.client import chat
print(chat([{'role': 'user', 'content': 'In one sentence: what is 2 plus 2?'}]))