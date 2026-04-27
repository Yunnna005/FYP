# Expenses Tracker — Bloom

A full-stack personal finance application with AI-powered chat, anomaly detection, forecasting, and spending recommendations.

---

## Architecture

| Service | Technology | Port |
|---|---|---|
| Frontend | React + TypeScript + Vite | 3000 |
| Express API | Node.js | 8000 |
| FastAPI / ML | Python + uvicorn | 8001 |
| PostgreSQL | Docker container | 5432 |
| Ollama (local LLM) | Native binary | 11434 |

The frontend proxies all requests through Vite — `/api/ask`, `/api/pipeline`, `/api/upload` go to FastAPI; everything else goes to Express.

---

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Node.js | 18+ | https://nodejs.org |
| Python | 3.9 – 3.11 | 3.12+ has Prophet issues |
| Docker Desktop | any | https://docker.com — required for `host.docker.internal` |
| Git | any | |
| Ollama | any | https://ollama.com |

---

## Step 1 — Clone and install Node dependencies

```bash
git clone <your-repo-url>
cd ExpensesTracker
npm install
```

---

## Step 2 — Set up the Python environment

```bash
# Create a virtual environment
python -m venv bloom-env

# Activate it
# Windows:
bloom-env\Scripts\activate
# macOS / Linux:
source bloom-env/bin/activate

# Install all Python dependencies
pip install -r backend/requirements.txt
```

> **Windows note:** `prophet` requires a C++ compiler. Install [Build Tools for Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/) before running pip install.
> **macOS note:** Run `xcode-select --install` first.

---

## Step 3 — Run PostgreSQL in Docker

```bash
docker run -d \
  --name expenses-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=<your_password> \
  -e POSTGRES_DB=ExpensesTracker \
  -p 5432:5432 \
  postgres:15
```

Verify it is running:

```bash
docker ps
```

> **Linux users:** `host.docker.internal` does not resolve automatically. Either replace it with `localhost` in all `.env` files, or add `--add-host=host.docker.internal:host-gateway` to the `docker run` command above.

---

## Step 4 — Restore the database from the exported file

**Plain SQL dump (`.sql`):**

```bash
psql -h localhost -U postgres -d ExpensesTracker < path/to/dump.sql
```

**Custom pg_dump format (`.dump` / `.backup`):**

```bash
pg_restore -h localhost -U postgres -d ExpensesTracker --no-owner path/to/dump.dump
```

If `psql` is not installed locally, restore through the container:

```bash
docker cp path/to/dump.sql expenses-postgres:/dump.sql
docker exec -it expenses-postgres psql -U postgres -d ExpensesTracker -f /dump.sql
```

---

## Step 5 — Install and start Ollama

Download and install from https://ollama.com, then pull the model:

```bash
ollama pull qwen3:1.7b
```

Ollama starts automatically after installation. Verify:

```bash
curl http://localhost:11434
# Expected: Ollama is running
```

---

## Step 6 — Configure environment files

Create the three `.env` files below. Do **not** commit them to git.

### `backend/.env` — Express server (Plaid + DB)

```
PLAID_CLIENT_ID=
PLAID_SECRET=
PLAID_ENV=sandbox
PORT=8000
DB_USER=
DB_HOST=host.docker.internal
DB_NAME=ExpensesTracker
DB_PASSWORD=
DB_PORT=5432
DB_SSL=false
```

### `backend/api/.env` — FastAPI server (LLM + Gemini)

```
LLM_BASE_URL=http://host.docker.internal:11434/v1
LLM_API_KEY=ollama

GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash-lite
GEMINI_MAX_TOKENS=300
```

### `backend/models/db/.env` — Python DB connection

```
DB_HOST=host.docker.internal
DB_PORT=5432
DB_NAME=ExpensesTracker
DB_USER=
DB_PASSWORD=
```

> Get a free Gemini API key at https://aistudio.google.com/apikey
> Get Plaid sandbox credentials at https://dashboard.plaid.com

---

## Step 7 — Run the project

Make sure the Python virtual environment is **active**, then:

```bash
npm run dev
```

This starts all three servers concurrently:

```
[0] Vite      → http://127.0.0.1:3000
[1] Express   → http://127.0.0.1:8000
[2] FastAPI   → http://127.0.0.1:8001
```

Open **http://127.0.0.1:3000** in your browser.

---

## Optional — Run the ML pipeline manually

If the pipeline has not run yet for the restored users:

```bash
# All users
cd backend
python -m pipelines.pipeline --full

# Specific user
python -m pipelines.pipeline --user <user_id>
```

---

## Optional — Run the model evaluation

Compares Local LLM vs Gemini across 15 test questions and 8 metrics. Requires the dev servers to be running.

```bash
python backend/evaluate.py
```

Saves a chart to `backend/evaluation_results.png`.

---

## Project structure

```
ExpensesTracker/
├── src/                        # React frontend
│   ├── pages/                  # Login, Dashboard, Chat, UploadAuth
│   ├── components/
│   └── hooks/
│
├── backend/
│   ├── server.js               # Express API (port 8000)
│   ├── .env                    # Plaid + DB credentials
│   ├── requirements.txt        # Python dependencies
│   ├── evaluate.py             # LLM evaluation script
│   │
│   ├── db/
│   │   ├── db_connection.js    # PostgreSQL pool
│   │   └── db_utils.js         # Query helpers
│   │
│   ├── api/                    # FastAPI app (port 8001)
│   │   ├── main.py
│   │   ├── .env                # LLM + Gemini credentials
│   │   ├── schemas.py
│   │   ├── chat/               # Classifier, narrator, LLM client
│   │   └── upload/             # CSV normaliser, categoriser, auth
│   │
│   ├── models/
│   │   ├── db/
│   │   │   ├── dbconfig.py     # SQLAlchemy config
│   │   │   └── .env            # Python DB credentials
│   │   └── python/             # ML model implementations
│   │
│   ├── pipelines/
│   │   └── pipeline.py         # ML pipeline orchestrator
│   │
│   └── analytics/
│       └── user_stats.py
│
├── vite.config.ts              # Proxy config (3000 → 8000/8001)
└── package.json                # npm scripts
```

---

## npm scripts

| Command | What it does |
|---|---|
| `npm run dev` | Start all three servers concurrently |
| `npm run dev:web` | Vite only (port 3000) |
| `npm run dev:express` | Express only (port 8000) |
| `npm run dev:fastapi` | FastAPI only (port 8001) |
| `npm run build` | Production build |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `host.docker.internal` not resolving | Linux: replace with `localhost` in all `.env` files |
| `openai.OpenAIError: api_key must be set` | `backend/api/.env` not loading — restart uvicorn |
| Ollama returns 404 | Ensure `LLM_BASE_URL` ends with `/v1` |
| `prophet` install fails | C++ compiler missing — see Step 2 |
| `psycopg2` connection refused | Docker container stopped — `docker start expenses-postgres` |
| FastAPI import errors | Virtual environment not active when running `npm run dev` |
| Pipeline produces no output | Run `python -m pipelines.pipeline --full` manually after DB restore |
