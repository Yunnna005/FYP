#!/usr/bin/env python3
"""
Comprehensive LLM Evaluation: Local (Ollama) vs Gemini
Metrics: latency, word count, naturalness, instruction following,
         specificity, conciseness, tone/warmth, readability
12 questions across 4 intent types — run from project root:
    python backend/evaluate.py
"""
import sys, os, time, re, json, math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from api.chat.llm.client import chat, chat_gemini
from api.chat.narrator import SYSTEM_PROMPT, _pick_prompt

# ── Mock financial context ────────────────────────────────────────────────────

CONTEXT = {
    "stats": {
        "money_spent": 1243.50,
        "money_received": 2800.00,
        "top_category": "Shopping",
        "month": "2026-03",
        "transaction_count": 73,
    },
    "anomalies": [
        {"amount": 591.33, "category": "Shopping", "anomaly_score": 95.84, "date": "2026-03-15"},
        {"amount": 312.00, "category": "Dining",   "anomaly_score": 72.10, "date": "2026-03-22"},
    ],
    "recommendations": [
        {"category": "Dining",   "avg_monthly_spend": 320.0, "suggested_cap": 200.0},
        {"category": "Shopping", "avg_monthly_spend": 650.0, "suggested_cap": 400.0},
    ],
    "forecast": {
        "next_month_predicted_spend": 1100.0,
        "trend": "decreasing",
    },
}

# Numbers and terms from the context — used for specificity scoring
_CTX_NUMBERS = {1243.50, 2800.00, 591.33, 312.00, 95.84, 72.10,
                320.0, 200.0, 650.0, 400.0, 1100.0, 73.0}
_CTX_TERMS   = {"shopping", "dining", "forecast", "decreasing"}

# ── Test cases ────────────────────────────────────────────────────────────────

CASES = [
    # ── LOOKUP ──
    {
        "group": "Lookup", "label": "Lu-1",
        "question": "How much did I spend last month?",
        "intent_needs": {"stats"},
        "ideal_words": (30, 80),
        "instruction_check": lambda r: bool(re.search(r"[\$€£]?\s*\d[\d,]*\.?\d*", r)),
    },
    {
        "group": "Lookup", "label": "Lu-2",
        "question": "What is my top spending category?",
        "intent_needs": {"stats"},
        "ideal_words": (20, 70),
        "instruction_check": lambda r: any(
            w in r.lower() for w in ["shopping", "dining", "groceries", "category", "most"]
        ),
    },
    {
        "group": "Lookup", "label": "Lu-3",
        "question": "How much money did I receive this month?",
        "intent_needs": {"stats"},
        "ideal_words": (20, 70),
        "instruction_check": lambda r: bool(re.search(r"[\$€£]?\s*\d[\d,]*\.?\d*", r)),
    },

    # ── ANOMALY ──
    {
        "group": "Anomaly", "label": "An-1",
        "question": "Is there anything unusual about my transactions?",
        "intent_needs": {"anomalies", "flagged_transactions"},
        "ideal_words": (40, 110),
        "instruction_check": lambda r: bool(
            re.match(r"\s*(yes|no|not really|yeah|yep|nope)", r.strip(), re.I)
        ),
    },
    {
        "group": "Anomaly", "label": "An-2",
        "question": "Were there any suspicious transactions recently?",
        "intent_needs": {"anomalies", "flagged_transactions"},
        "ideal_words": (40, 110),
        "instruction_check": lambda r: bool(
            re.match(r"\s*(yes|no|not really|yeah|yep|nope)", r.strip(), re.I)
        ),
    },
    {
        "group": "Anomaly", "label": "An-3",
        "question": "Does my spending look normal to you?",
        "intent_needs": {"anomalies", "flagged_transactions"},
        "ideal_words": (30, 100),
        "instruction_check": lambda r: bool(
            re.match(r"\s*(yes|no|not really|mostly|kind of|sort of|yeah|nope|not quite)", r.strip(), re.I)
        ),
    },

    # ── ADVICE ──
    {
        "group": "Advice", "label": "Ad-1",
        "question": "Give me advice on how I can save money.",
        "intent_needs": {"recommendations", "stats"},
        "ideal_words": (100, 250),
        "instruction_check": lambda r: bool(
            re.search(r"(?i)step\s*\d|^\s*\d[\.\)]\s", r, re.M)
        ),
    },
    {
        "group": "Advice", "label": "Ad-2",
        "question": "How can I cut back on my shopping expenses?",
        "intent_needs": {"recommendations", "stats"},
        "ideal_words": (100, 250),
        "instruction_check": lambda r: bool(
            re.search(r"(?i)step\s*\d|^\s*\d[\.\)]\s", r, re.M)
        ),
    },
    {
        "group": "Advice", "label": "Ad-3",
        "question": "What should I do to prepare financially for next month?",
        "intent_needs": {"recommendations", "forecast"},
        "ideal_words": (100, 250),
        "instruction_check": lambda r: bool(
            re.search(r"(?i)step\s*\d|^\s*\d[\.\)]\s", r, re.M)
        ),
    },

    # ── SCENARIO ──
    {
        "group": "Scenario", "label": "Sc-1",
        "question": "I'm going to Spain in 3 months. How can I save €500 extra for the trip?",
        "intent_needs": {"recommendations", "stats"},
        "ideal_words": (120, 300),
        "instruction_check": lambda r: (
            bool(re.search(r"(?i)step\s*\d|^\s*\d[\.\)]\s", r, re.M)) and
            bool(re.search(r"[\$€£]?\s*\d[\d,]*", r))
        ),
    },
    {
        "group": "Scenario", "label": "Sc-2",
        "question": "I want to buy a laptop for €800 in 2 months. Is that realistic and how do I get there?",
        "intent_needs": {"recommendations", "stats"},
        "ideal_words": (100, 280),
        "instruction_check": lambda r: (
            bool(re.search(r"[\$€£]?\s*\d[\d,]*", r)) and
            any(w in r.lower() for w in ["realistic", "possible", "achievable", "can", "month", "per month"])
        ),
    },
    {
        "group": "Scenario", "label": "Sc-3",
        "question": "I'm moving out next month and need €1500 for a deposit. What should I cut to make that work?",
        "intent_needs": {"recommendations", "forecast"},
        "ideal_words": (120, 300),
        "instruction_check": lambda r: (
            bool(re.search(r"(?i)step\s*\d|^\s*\d[\.\)]\s", r, re.M)) or
            bool(re.search(r"[\$€£]?\s*\d[\d,]*", r))
        ),
    },

    # ── OVERVIEW ──
    {
        "group": "Overview", "label": "Ov-1",
        "question": "How am I doing overall with my finances?",
        "intent_needs": {"stats", "anomalies", "recommendations", "forecast"},
        "ideal_words": (60, 160),
        "instruction_check": lambda r: sum(
            1 for kw in ["spend", "receiv", "forecast", "unusual", "next", "anomal"]
            if kw in r.lower()
        ) >= 3,
    },
    {
        "group": "Overview", "label": "Ov-2",
        "question": "Give me a summary of my recent spending.",
        "intent_needs": {"stats", "anomalies", "recommendations", "forecast"},
        "ideal_words": (60, 160),
        "instruction_check": lambda r: sum(
            1 for kw in ["spend", "receiv", "forecast", "unusual", "next", "month"]
            if kw in r.lower()
        ) >= 2,
    },
    {
        "group": "Overview", "label": "Ov-3",
        "question": "Am I spending too much?",
        "intent_needs": {"stats", "anomalies", "recommendations", "forecast"},
        "ideal_words": (50, 140),
        "instruction_check": lambda r: bool(re.search(r"[\$€£]?\s*\d[\d,]*\.?\d*", r)),
    },
]

# ── Scoring functions ─────────────────────────────────────────────────────────

_FIELD_NAMES   = ["money_spent", "money_received", "anomaly_score", "avg_monthly_spend"]
_ROBOTIC       = ["based on the data", "according to the information", "the data shows",
                  "it appears that", "as per the", "based on your data", "it is evident"]
_CASUAL        = ["hey", "looks like", "honestly", "actually", "you've", "you're",
                  "let's", "that's", "it's", "so,", "pretty", "quite", "worth a",
                  "just", "basically", "tbh"]
_FORMAL        = ["furthermore", "moreover", "therefore", "in conclusion",
                  "it is recommended", "one should", "please note", "it should be noted"]
_WARM          = ["great", "good", "nice", "well done", "solid", "keep it up",
                  "you're doing", "that's", "awesome", "brilliant", "well"]
_FRIENDLY_OPEN = ["hey", "so,", "alright", "right,", "looks like", "okay so"]


def score_naturalness(text: str) -> float:
    score = 10.0
    t = text.lower()
    for f in _FIELD_NAMES:
        if f in t:
            score -= 2.0
    for r in _ROBOTIC:
        if r in t:
            score -= 1.5
    for c in _CASUAL:
        if c in t:
            score += 0.4
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    lengths = [len(s.split()) for s in sentences]
    if len(lengths) > 2:
        variety = np.std(lengths) / max(np.mean(lengths), 1)
        score += min(variety * 2.5, 1.5)
    return round(max(0.0, min(10.0, score)), 2)


def score_specificity(text: str) -> float:
    """How much does the response reference real numbers/terms from the context?"""
    nums_in_response = set()
    for n in re.findall(r"\d+\.?\d*", text):
        try:
            nums_in_response.add(float(n))
        except ValueError:
            pass
    matches = sum(
        1 for n in _CTX_NUMBERS
        if any(abs(n - r) < 0.5 for r in nums_in_response)
    )
    score = min(matches * 2.0, 8.0)
    t = text.lower()
    for term in _CTX_TERMS:
        if term in t:
            score += 0.5
    return round(min(10.0, score), 2)


def score_conciseness(text: str, ideal_range: tuple) -> float:
    """Is the response length appropriate for the question type?"""
    words = len(text.split())
    lo, hi = ideal_range
    if lo <= words <= hi:
        return 10.0
    elif words < lo:
        return round(max(0.0, 10.0 * (words / lo)), 2)
    else:
        excess_ratio = (words - hi) / hi
        return round(max(0.0, 10.0 - excess_ratio * 10.0), 2)


def score_tone(text: str) -> float:
    """Warmth, friendliness, and directness of the response."""
    score = 5.0
    t = text.lower()
    for w in _WARM:
        if w in t:
            score += 0.5
    second_person = len(re.findall(r"\byou\b|\byour\b|\byou're\b|\byou've\b", t))
    score += min(second_person * 0.3, 2.0)
    for f in _FRIENDLY_OPEN:
        if t.startswith(f) or f"\n{f}" in t:
            score += 0.5
    for f in _FORMAL:
        if f in t:
            score -= 1.0
    return round(max(0.0, min(10.0, score)), 2)


def score_readability(text: str) -> float:
    """
    Approximated readability — targets average sentence length of 12–18 words.
    Shorter or much longer sentences score lower.
    """
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    if not sentences:
        return 5.0
    lengths = [len(s.split()) for s in sentences]
    avg = np.mean(lengths)
    ideal_center = 15.0
    deviation = abs(avg - ideal_center)
    score = 10.0 - min(deviation / 3.0, 4.0)
    if len(lengths) > 2:
        cv = np.std(lengths) / max(avg, 1)
        score += max(0, 1.0 - cv)
    return round(max(0.0, min(10.0, score)), 2)


# ── Evaluation runner ─────────────────────────────────────────────────────────

def run_evaluation() -> list[dict]:
    records = []

    print(f"\n{'='*70}")
    print(f"   LLM Evaluation  ·  Local (Ollama)  vs  Gemini  ·  {len(CASES)} questions")
    print(f"{'='*70}")
    print("\nQuestion index:")
    for c in CASES:
        print(f"  {c['label']:6}  [{c['group']:8}]  {c['question']}")
    print()

    for i, case in enumerate(CASES):
        template = _pick_prompt(case["intent_needs"])
        prompt   = template.format(
            question=case["question"],
            context=json.dumps(CONTEXT, indent=2),
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ]

        print(f"[{i+1:02d}/{len(CASES)}] {case['label']} · {case['question'][:55]}...")

        t0 = time.time()
        try:
            r_local   = chat(messages)
            lat_local = round(time.time() - t0, 2)
        except Exception as e:
            r_local, lat_local = f"[Error: {e}]", 0.0

        t0 = time.time()
        try:
            r_gemini   = chat_gemini(messages)
            lat_gemini = round(time.time() - t0, 2)
        except Exception as e:
            r_gemini, lat_gemini = f"[Error: {e}]", 0.0

        ideal = case["ideal_words"]
        rec = {
            "label":           case["label"],
            "group":           case["group"],
            "question":        case["question"],
            "lat_local":       lat_local,
            "lat_gemini":      lat_gemini,
            "words_local":     len(r_local.split()),
            "words_gemini":    len(r_gemini.split()),
            "natural_local":   score_naturalness(r_local),
            "natural_gemini":  score_naturalness(r_gemini),
            "instruct_local":  int(case["instruction_check"](r_local)),
            "instruct_gemini": int(case["instruction_check"](r_gemini)),
            "specific_local":  score_specificity(r_local),
            "specific_gemini": score_specificity(r_gemini),
            "concise_local":   score_conciseness(r_local, ideal),
            "concise_gemini":  score_conciseness(r_gemini, ideal),
            "tone_local":      score_tone(r_local),
            "tone_gemini":     score_tone(r_gemini),
            "readable_local":  score_readability(r_local),
            "readable_gemini": score_readability(r_gemini),
            "response_local":  r_local,
            "response_gemini": r_gemini,
        }
        records.append(rec)

        print(f"  Local  → {lat_local:5.1f}s | {rec['words_local']:>4}w | "
              f"nat {rec['natural_local']:.1f} | spec {rec['specific_local']:.1f} | "
              f"conc {rec['concise_local']:.1f} | tone {rec['tone_local']:.1f} | "
              f"read {rec['readable_local']:.1f} | instr {'✓' if rec['instruct_local'] else '✗'}")
        print(f"  Gemini → {lat_gemini:5.1f}s | {rec['words_gemini']:>4}w | "
              f"nat {rec['natural_gemini']:.1f} | spec {rec['specific_gemini']:.1f} | "
              f"conc {rec['concise_gemini']:.1f} | tone {rec['tone_gemini']:.1f} | "
              f"read {rec['readable_gemini']:.1f} | instr {'✓' if rec['instruct_gemini'] else '✗'}")

    # ── summary table ──
    SUMMARY = [
        ("Avg Latency (s)",    "lat_local",     "lat_gemini",     False),
        ("Avg Word Count",     "words_local",   "words_gemini",   False),
        ("Naturalness  /10",   "natural_local", "natural_gemini", True),
        ("Specificity  /10",   "specific_local","specific_gemini",True),
        ("Conciseness  /10",   "concise_local", "concise_gemini", True),
        ("Tone/Warmth  /10",   "tone_local",    "tone_gemini",    True),
        ("Readability  /10",   "readable_local","readable_gemini",True),
        ("Instr. Follow",      "instruct_local","instruct_gemini",None),
    ]
    print(f"\n{'─'*58}")
    print(f"  {'Metric':<22} {'Local':>10}  {'Gemini':>10}  {'Winner':>6}")
    print(f"  {'─'*22} {'─'*10}  {'─'*10}  {'─'*6}")
    for label, kl, kg, higher_better in SUMMARY:
        if higher_better is None:
            vl = sum(r[kl] for r in records)
            vg = sum(r[kg] for r in records)
            winner = "Local" if vl > vg else ("Gemini" if vg > vl else "Tie")
            print(f"  {label:<22} {vl:>10}/{len(records)}  {vg:>9}/{len(records)}  {winner:>6}")
        else:
            vl = np.mean([r[kl] for r in records])
            vg = np.mean([r[kg] for r in records])
            if higher_better:
                winner = "Local" if vl > vg + 0.1 else ("Gemini" if vg > vl + 0.1 else "Tie")
            else:
                winner = "Local" if vl < vg - 0.1 else ("Gemini" if vg < vl - 0.1 else "Tie")
            print(f"  {label:<22} {vl:>10.2f}  {vg:>10.2f}  {winner:>6}")
    print(f"{'─'*58}\n")

    return records


# ── Plotting ──────────────────────────────────────────────────────────────────

def plot_results(records: list[dict]):
    labels = [r["label"] for r in records]
    x = np.arange(len(labels))
    w = 0.35
    C_LOCAL  = "#7c3aed"   # purple
    C_GEMINI = "#f59e0b"   # amber / yellow

    fig = plt.figure(figsize=(20, 15))
    gs  = gridspec.GridSpec(3, 3, figure=fig, hspace=0.55, wspace=0.38)

    fig.suptitle(
        "LLM Evaluation  ·  Local Ollama (qwen3:1.7b)  vs  Gemini 2.5 Flash Lite\n"
        f"{len(records)} test questions  ·  5 intent types: Lookup · Anomaly · Advice · Scenario · Overview",
        fontsize=13, fontweight="bold", y=1.01,
    )

    PANELS = [
        ("Latency (seconds)  ↓ lower is better",          "lat_local",     "lat_gemini",      gs[0, 0]),
        ("Response Length (words)",                         "words_local",   "words_gemini",    gs[0, 1]),
        ("Instruction Following  (0 = fail · 1 = pass)",   "instruct_local","instruct_gemini", gs[0, 2]),
        ("Naturalness  (0–10)  ↑",                         "natural_local", "natural_gemini",  gs[1, 0]),
        ("Specificity  (0–10)  ↑  uses real context data", "specific_local","specific_gemini", gs[1, 1]),
        ("Conciseness  (0–10)  ↑  vs ideal length/type",   "concise_local", "concise_gemini",  gs[1, 2]),
        ("Tone / Warmth  (0–10)  ↑",                       "tone_local",    "tone_gemini",     gs[2, 0]),
        ("Readability  (0–10)  ↑  avg sentence length",    "readable_local","readable_gemini", gs[2, 1]),
    ]

    for title, kl, kg, gspec in PANELS:
        ax = fig.add_subplot(gspec)
        vl = [r[kl] for r in records]
        vg = [r[kg] for r in records]
        bl = ax.bar(x - w / 2, vl, w, label="Local (Ollama)", color=C_LOCAL,  alpha=0.87)
        bg = ax.bar(x + w / 2, vg, w, label="Gemini",         color=C_GEMINI, alpha=0.87)
        ax.set_title(title, fontsize=9, pad=5)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8, rotation=35, ha="right")
        ax.legend(fontsize=8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax.set_axisbelow(True)
        y_max = max(max(vl + vg), 0.1)
        for bar in [*bl, *bg]:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + y_max * 0.02,
                        f"{h:.1f}", ha="center", va="bottom", fontsize=7)

    # ── Radar chart — overall quality profile ──
    ax_radar = fig.add_subplot(gs[2, 2], projection="polar")

    RADAR_LABELS = ["Naturalness", "Specificity", "Conciseness", "Tone", "Readability", "Instruction\nFollowing"]
    RADAR_KEYS_L = ["natural_local",  "specific_local",  "concise_local",  "tone_local",  "readable_local",  "instruct_local"]
    RADAR_KEYS_G = ["natural_gemini", "specific_gemini", "concise_gemini", "tone_gemini", "readable_gemini", "instruct_gemini"]

    N = len(RADAR_LABELS)
    angles = [n / N * 2 * math.pi for n in range(N)] + [0]

    def avg_norm(key):
        v = np.mean([r[key] for r in records])
        return v * 10 if "instruct" in key else v

    vals_l = [avg_norm(k) for k in RADAR_KEYS_L] + [avg_norm(RADAR_KEYS_L[0])]
    vals_g = [avg_norm(k) for k in RADAR_KEYS_G] + [avg_norm(RADAR_KEYS_G[0])]

    ax_radar.plot(angles, vals_l, "o-", lw=2, color=C_LOCAL,  label="Local")
    ax_radar.fill(angles, vals_l, alpha=0.18, color=C_LOCAL)
    ax_radar.plot(angles, vals_g, "o-", lw=2, color=C_GEMINI, label="Gemini")
    ax_radar.fill(angles, vals_g, alpha=0.18, color=C_GEMINI)
    ax_radar.set_xticks(angles[:-1])
    ax_radar.set_xticklabels(RADAR_LABELS, fontsize=8.5)
    ax_radar.set_ylim(0, 10)
    ax_radar.set_yticks([2, 4, 6, 8, 10])
    ax_radar.set_yticklabels(["2", "4", "6", "8", "10"], fontsize=7, color="grey")
    ax_radar.set_title("Overall Quality Profile\n(avg, all metrics normalised 0–10)",
                        fontsize=9, pad=14)
    ax_radar.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15), fontsize=8)

    out = Path(__file__).parent / "evaluation_results.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"[✓] Chart saved → {out}")
    plt.show()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    records = run_evaluation()
    plot_results(records)
