import concurrent
from pyexpat.errors import messages
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from matplotlib.style import context

from api.schemas import AskRequest, AskResponse
from api.chat.classifier import classify
from api.chat.dispatcher import collect_context
from api.chat.narrator import narrate, build_prompt
from api.chat import collectors
from api.chat.llm.client import chat, gemini_chat

app = FastAPI(title="Finance Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/ask", response_model=AskResponse)
def ask(request: AskRequest):
    intent = classify(request.question, request.user_id)
    context = collect_context(request.user_id, intent)

    #build prompt for both models to compare
    last_date = collectors.get_latest_month(request.user_id)
    messages = build_prompt(
        request.question,
        context,
        intent_needs=intent.needs,
        last_transaction_date=last_date,
    )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        ollama_future = pool.submit(chat, messages)
        gemini_future = pool.submit(gemini_chat, messages)
 
        ollama_answer = ollama_future.result()
        gemini_answer = gemini_future.result()
 
    return AskResponse(
        ollama_answer=ollama_answer,
        gemini_answer=gemini_answer,
        answer=ollama_answer,
        intent={"needs": list(intent.needs), "params": intent.params},
        context_keys=list(context.keys()),
    )