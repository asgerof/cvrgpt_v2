# CVRGPT v2

A pragmatic starter kit for a **CVR/Virk-aware MCP server** plus a **Next.js chat UI**.
This is *not* just “another CVR lookup”: it’s structured to compute **derived answers with provenance**
(e.g., “compare latest two accounts, show deltas, and link to sources”), expose them as **MCP tools**,
and also ship a simple REST API that your frontend (or RPA flows) can call.

## What’s in here

- **`server/`** – Python FastAPI app *and* an MCP server (via `mcp` SDK with SSE + stdio).
  - Tools: `search_companies`, `get_company`, `list_filings`, `get_latest_accounts`, `compare_accounts`.
  - Provider abstraction: start with **fixture data**; swap in real CVR/Virk providers as you add credentials.
  - Every response carries **citations**.
- **`frontend/`** – Next.js (App Router, TS, Tailwind) with a chat-ish UI and an evidence pane.
  - Calls the REST API (same logic the MCP tools use).
- **CI** – GitHub Action to run Python tests and build the Next.js app.

> ⚠️ Note on data sources: CVR basic data is generally free under the Basic Data Programme, but most
> production endpoints require registration/credentials. This starter uses fixtures by default so it runs
> out-of-the-box; wire a real provider when you’re ready.

## Quick start (two terminals)

### 1) Python server (REST + MCP over SSE)
```bash
cd server
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn cvrgpt_server.api:app --reload --port 8000
# MCP SSE is mounted at /mcp; health is at /healthz
```

### 2) Frontend
```bash
cd frontend
npm i
npm run dev   # Next.js on :3000, expects API on :8000 (configurable via NEXT_PUBLIC_API_BASE_URL)
```

### 3) MCP (optional)
- **Stdio:** `python -m cvrgpt_server.mcp_server stdio`
- **SSE (already mounted):** point your MCP client/ChatGPT remote connector to `http://localhost:8000/mcp`
  (see `server/src/cvrgpt_server/mcp_server.py`).

## Configure providers

Copy `.env.example` to `.env` inside `server/` and fill in any API keys you have (e.g., CVR third-party).
Until then, the **FixtureProvider** serves data from `server/src/cvrgpt_server/fixtures`.

## Tests
```bash
cd server
pytest -q
```

## Project decisions

- Keep **MCP** and **REST** in the **same process** for now (SSE mount). You can split later.
- **Provider pattern** so you can add: Datafordeler CVR, Offentliggørelser index, iXBRL parsing, VIES VAT, sanctions/PEP, etc.
- **Provenance-first** responses (`citations: []`) to make compliance happy and debugging easy.
