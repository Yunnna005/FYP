import logging
from api.chat.classifier import classify
from api.chat.dispatcher import collect_context
from api.chat.narrator import narrate

logging.basicConfig(level=logging.INFO)

USER_ID = "USR342cz" 

QUESTIONS = [
    "How much did I spend last month?",
    "Anything weird in my spending?",
    "How can I save more money?",
    "How am I doing overall?",
    "I am going to a concert next month, how much should I budget for it?",
    "Im goint on a 3 days trip to Paris next month, how much should I budget for it?",
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

    answer = narrate(question, context)
    print(f"\nA: {answer}\n")