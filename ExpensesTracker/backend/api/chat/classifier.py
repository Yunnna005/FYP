from dataclasses import dataclass, field
from .extractors import extract_month, extract_category
from . import collectors
from datetime import datetime


@dataclass
class QuestionIntent:
    needs: set[str] = field(default_factory=set)
    params: dict = field(default_factory=dict)


def classify(question: str, user_id: str) -> QuestionIntent:
    q = question.lower()
    intent = QuestionIntent()

    latest_str = collectors.get_latest_month(user_id)
    reference_date = None
    if latest_str:
        reference_date = datetime.strptime(f"{latest_str}-01", "%Y-%m-%d").date()

    intent.params["category"] = extract_category(q)
    intent.params["month"] = extract_month(q, reference_date=reference_date)

    if any(w in q for w in ["how much", "total", "spent", "spend on", "earned", "income", "expenses", "cost", 
                            "pay", "paid", "money in", "money out"]):
        intent.needs.add("stats")

    if any(w in q for w in ["weird", "unusual", "strange", "flagged", "anomaly", "suspicious", "unexpected", 
                            "outlier", "irregular", "abnormal"]):
        intent.needs.add("anomalies")
        intent.needs.add("flagged_transactions")

    if any(w in q for w in ["will", "predict", "forecast", "next month", "future", "projected", "estimate", 
                            "expected", "prognosis", "outlook", "prediction", "predicting"]):
        intent.needs.add("forecast")

    if any(w in q for w in ["save", "should i", "how can i", "reduce", "cut", "afford", "recommend", "advice", 
                            "suggest", "tips", "help", "guidance", "plan", "budget", "manage", "handle", "improve", 
                            "optimize", "make better"]):
        intent.needs.add("recommendations")
        intent.needs.add("stats")

    if any(w in q for w in ["travel", "trip", "vacation", "buying", "wedding", "car", "house", "big purchase", 
                            "expensive", "luxury", "holiday", "moving", "relocating", "home", "apartment", "furniture", 
                            "electronics", "gadget", "gift", "event", "celebration", "party", "dining out", "eating out"]):
        intent.needs.update({"recommendations", "forecast", "stats"})

    if not intent.needs or "how am i doing" in q or "overall" in q:
        intent.needs = {"stats", "anomalies", "recommendations", "forecast"}

    return intent