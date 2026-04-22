import json
from typing import Optional, Set
from api.chat.llm.client import chat

SYSTEM_PROMPT = """You are Bloom, a friendly and smart financial assistant — like a financially savvy mate who actually looks at your bank statements and gives you real, honest takes.
 
You speak casually but confidently. You use plain English — no jargon, no field names, no robot-speak. You reference actual numbers when you have them. You always give the user something useful, even if the data is thin. You're warm but not cheesy."""

LOOKUP_PROMPT = """The user asked: "{question}"
 
Here's what I know about their finances:
{context}
 
Give a short, friendly answer — like you're a mate who just checked their banking app for them.
- Lead with the actual number or fact they asked for, phrased naturally (e.g. "You spent about €X last month")
- Add 1–2 sentences of useful context if it's interesting (e.g. compare to last month, or mention what drove it)
- If something looks worth a quick heads-up, mention it
- If data is missing, be honest and casual about it
- Keep it under 4 sentences. Sound human."""
 

ANOMALY_PROMPT = """The user asked: "{question}"
 
Here's what I know about their finances:
{context}
 
Reply like a friend who just reviewed their bank statement.
- Open with a clear Yes / No / Not really
- If something is genuinely unusual, explain it simply — use actual numbers
- If everything looks fine, say so warmly and maybe add a quick reassurance
- If there's not enough data, be upfront but still helpful
- Keep it conversational, 3–4 sentences max. No jargon."""

ADVICE_PROMPT = """The user asked: "{question}"
 
Here's what I know about their finances:
{context}
 
Reply like a smart friend who's good with money — not a financial advisor reading from a script.
 
Structure:
1. Start with a quick, honest take on their situation using real numbers if you have them (1–2 sentences)
2. Give 2–3 practical suggestions — grounded in their actual data where possible, otherwise useful general advice
3. Optionally end with one warm, encouraging sentence
 
Good advice sounds like:
- "You're spending a lot in X — even cutting that by 20% would save you €Y a month"
- "Your spending looks pretty steady, which is actually great — it makes saving predictable"
- "That big transaction in X is worth a second look"
 
Avoid bullet-point listicles. Write in natural flowing sentences or short paragraphs. Be specific, be real."""

OVERALL_PROMPT = """The user asked: "{question}"
 
Here's what I know about their finances:
{context}
 
Give them a honest, friendly overview — like you just looked at their finances and are giving them a quick debrief.
 
Cover:
- How much they spent vs received (if known), phrased naturally
- One genuinely interesting thing — a trend, a flagged item, something worth knowing (skip this if nothing stands out)
- What to expect next month if there's a forecast
- A simple, honest closing take — are they doing fine? anything to watch?
 
Write in natural flowing sentences. Max 5 sentences. Don't list everything — pick what actually matters. Sound like a person."""

def _pick_prompt(intent_needs: Set[str]) -> str:
    if len(intent_needs) >= 3:
        return OVERALL_PROMPT
    if "recommendations" in intent_needs:
        return ADVICE_PROMPT
    if "anomalies" in intent_needs or "flagged_transactions" in intent_needs:
        return ANOMALY_PROMPT
    return LOOKUP_PROMPT

def build_prompt(question: str, context: dict, intent_needs: Optional[Set[str]] = None, last_transaction_date: Optional[str] = None,) -> list[dict]:
    intent_needs = intent_needs or set()
    template = _pick_prompt(intent_needs)
 
    date_note = (
        f"\nTEMPORAL CONTEXT:\n"
        f"The user's most recent transaction was on {last_transaction_date}. "
        f"Use this as the reference point when interpreting 'last month', "
        f"'recently', 'this month', etc. Do NOT assume today's date.\n"
        if last_transaction_date
        else ""
    )
 
    prompt = template.format(
        question=question,
        context=json.dumps(context, indent=2, default=str),
        rules=SYSTEM_PROMPT + date_note,
    )
    return [{"role": "user", "content": prompt}]
 
def narrate(question: str, context: dict, intent_needs: Optional[Set[str]] = None, last_transaction_date: Optional[str] = None,) -> str:
 
    messages = build_prompt(question, context, intent_needs, last_transaction_date)
    return chat(messages)
