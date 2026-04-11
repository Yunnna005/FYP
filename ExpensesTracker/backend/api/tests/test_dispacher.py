from api.chat.classifier import classify
from api.chat.dispatcher import collect_context
import json



print("\n\nUSR601Ie: How much did I spend on food this month?")

intent = classify('How much did I spend on food this month?', 'USR601Ie')
context = collect_context('USR601Ie', intent)
print(json.dumps(context, indent=2, default=str))
