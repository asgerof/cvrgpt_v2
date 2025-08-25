# Server UAT Configuration

Set the following environment variables for UAT with ERST live data and LLM NLU:

Required:
- `API_KEY`: API key required by all `/v1/*` endpoints and `/chat`.
- `DATA_PROVIDER=erst`: Select ERST provider.
- `APP_ENV=uat` (or `prod`): Enables provider reachability checks.
- `ERST_CLIENT_ID`, `ERST_CLIENT_SECRET`, `ERST_AUTH_URL`, `ERST_TOKEN_AUDIENCE`, `ERST_API_BASE_URL`.

Optional (mTLS):
- `ERST_CERT_PATH`, `ERST_KEY_PATH` (mounted inside the container if needed).

Events (live):
- `ERST_EVENTS_REAL=1` to enable live events provider.
- `ERST_API_BASE` and `ERST_API_KEY` for events endpoint access.

Chat NLU:
- `OPENAI_API_KEY`: Enables LLM-first NLU in `/v1/chat`.
- `CHAT_NLU=hybrid` (default), `CHAT_NLU_MODEL=gpt-4o-mini`.

Observability:
- `PROMETHEUS` is auto-detected. Metrics at `/metrics` when enabled.

Redis:
- `CVRGPT_REDIS_URL` should point to a reachable Redis instance.

Run using docker-compose at repository root:
```bash
docker compose up --build
```
