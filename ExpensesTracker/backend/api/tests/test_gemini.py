import logging
from api.chat.classifier import classify
from api.chat.dispatcher import collect_context
from api.chat.narrator import build_prompt
from api.chat.llm.client import chat as gemini_chat

logging.basicConfig(level=logging.INFO)

USER_ID = "USR342cz"

QUESTIONS = [
    "How much did I spend last month?",
    "Anything weird in my spending?",
    "How can I save more money?",
    "How am I doing overall?",
]

for question in QUESTIONS:
    print("=" * 70)
    print(f"Q: {question}")
    print("-" * 70)

    intent = classify(question, USER_ID)
    print(f"Classified needs: {intent.needs}")
    print(f"Extracted params: {intent.params}")

    context = collect_context(USER_ID, intent)
    print(f"Context keys: {list(context.keys())}")

    messages = build_prompt(question, context, intent.needs)
    answer = gemini_chat(messages)

    print(f"\nA: {answer}\n")