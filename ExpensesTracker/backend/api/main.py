from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import AskRequest, AskResponse
from api.chat.classifier import classify
from api.chat.dispatcher import collect_context
from api.chat.narrator import narrate

app = FastAPI(title="Finance Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
    answer = narrate(request.question, context)
    return AskResponse(
        answer=answer,
        intent={"needs": list(intent.needs), "params": intent.params},
        context_keys=list(context.keys()),
    )