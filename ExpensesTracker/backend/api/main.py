from typing import Optional

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from threading import Lock

from api.schemas import AskRequest, AskResponse
from api.chat.classifier import classify
from api.chat.dispatcher import collect_context
from api.chat.narrator import narrate
from pipelines import pipeline  
from fastapi import FastAPI, BackgroundTasks
from threading import Lock

app = FastAPI(title="Finance Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000",
                   "http://localhost:5173", "http://127.0.0.1:5173",
                   "http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline_status: dict[str, dict] = {}
status_lock = Lock()

def set_status(user_id: str, status: str, detail: Optional[dict] = None):
    with status_lock:
        pipeline_status[user_id] = {"status": status, "detail": detail or {}}

def run_pipeline_bg(user_id: str):
    from pipelines.pipeline import run_pipeline
    try:
        with status_lock:
            pipeline_status[user_id] = "running"
        results = run_pipeline(user_id=user_id)
        failed = any("FAIL" in v for v in results.values())
        with status_lock:
            pipeline_status[user_id] = "failed" if failed else "done"
    except Exception:
        with status_lock:
            pipeline_status[user_id] = "failed"


def start_pipeline(user_id: str, background_tasks: BackgroundTasks):
    with status_lock:
        if pipeline_status.get(user_id) == "running":
            return {"status": "running"}
        pipeline_status[user_id] = "running"
    background_tasks.add_task(run_pipeline_bg, user_id)
    return {"status": "started"}

@app.get("/api/pipeline/status")
def get_pipeline_status(user_id: str):
    with status_lock:
        return {"status": pipeline_status.get(user_id, "idle")}


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

@app.post("/api/pipeline/run")
def start_pipeline(user_id: str, background_tasks: BackgroundTasks):
    with status_lock:
        if pipeline_status.get(user_id) == "running":
            return {"status": "running"}
        pipeline_status[user_id] = "running"
    background_tasks.add_task(run_pipeline_bg, user_id)
    return {"status": "started"}