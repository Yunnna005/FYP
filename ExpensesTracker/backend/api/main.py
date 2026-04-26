import os
from typing import Optional
import uuid
import tempfile
import random
from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text
from threading import Lock

from api.schemas import AskRequest, AskResponse
from api.chat.classifier import classify
from api.chat.dispatcher import collect_context
from api.chat.narrator import narrate
from api.upload.normalizers import normalize_csv
from api.upload.categorizer import categorize_transactions
from api.upload.auth import hash_password, verify_password
from models.db.dbconfig import get_engine
from pipelines.pipeline import run_pipeline  


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

def generate_user_id() -> str:
    return f"USR{uuid.uuid4().hex[:8]}"


def generate_account_id() -> str:
    return str(random.randint(10**14, 10**15 - 1))


def generate_mask() -> str:
    return f"{random.randint(0, 9999):04d}"

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
    answers = narrate(request.question, context, intent.needs)
    return AskResponse(
        answer_local=answers.get("local", ""),
        answer_gemini=answers.get("gemini", ""),
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

@app.post("/api/upload/signup")
async def upload_signup(
    bank: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    phone_number: str = Form(""),
    account_name: str = Form(...),
    file: UploadFile = File(...),
):
    if bank not in ("aib", "revolut"):
        raise HTTPException(status_code=400, detail="Unknown bank format")

    engine = get_engine()

    # Check email uniqueness
    with engine.begin() as conn:
        existing = conn.execute(
            text("SELECT 1 FROM users WHERE email = :email"),
            {"email": email},
        ).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")

    # Save upload to a temp file, parse, then delete
    user_id = generate_user_id()
    account_id = generate_account_id()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        transactions_df, account_info = normalize_csv(tmp_path, bank, account_id)
    except Exception as e:
        os.remove(tmp_path)
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    if transactions_df.empty:
        raise HTTPException(status_code=400, detail="No valid transactions found in CSV")

    # Categorize
    transactions_df = categorize_transactions(transactions_df)

    # Build account row
    mask = generate_mask()
    account_row = {
        "account_id": account_id,
        "name": account_name,
        "type": "depository",
        "mask": mask,
        "balances_current": account_info["balance"],
        "balances_available": account_info["balance"],
        "currency_code": account_info["currency"],
    }

    # Build user row
    user_row = {
        "user_id": user_id,
        "email": email,
        "password": hash_password(password),
        "full_name": full_name,
        "phone_number": phone_number or None,
        "plaid_access_token": None,
        "plaid_item_id": None,
        "is_active": True,
        "account_id": account_id,
    }

    # Insert in transaction
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO accounts (account_id, name, type, mask, balances_current, balances_available, currency_code)
                    VALUES (:account_id, :name, :type, :mask, :balances_current, :balances_available, :currency_code)
                """),
                account_row,
            )
            conn.execute(
                text("""
                    INSERT INTO users (user_id, email, password, full_name, phone_number, plaid_access_token, plaid_item_id, is_active, account_id)
                    VALUES (:user_id, :email, :password, :full_name, :phone_number, :plaid_access_token, :plaid_item_id, :is_active, :account_id)
                """),
                user_row,
            )
            transactions_df.to_sql("transactions", conn, if_exists="append", index=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database insert failed: {e}")

    # Kick off pipeline synchronously so the dashboard is ready when frontend lands
    try:
        run_pipeline(user_id=user_id)
    except Exception as e:
        print(f"[upload/signup] pipeline error for {user_id}: {e}")
        # Don't fail the request — the user is created, the dashboard will just have less data

    return {"user_id": user_id}


class CsvLoginRequest(BaseModel):
    email: str
    password: str


@app.post("/api/upload/login")
def upload_login(req: CsvLoginRequest):
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT user_id, password FROM users WHERE email = :email"),
            {"email": req.email},
        ).fetchone()

    if not row:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id, hashed = row
    if not verify_password(req.password, hashed):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"user_id": user_id}