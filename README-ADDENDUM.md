# README – Addendum (contracts, errors, timeouts, runbook)

## Contracts
See `server/src/cvrgpt_server/models.py` for Pydantic models that mirror the REST/MCP responses.

## Error model
Canonical JSON for errors:

```json
{ "code": "BAD_REQUEST", "detail": "Explanation..." }
```

Suggested mappings:
- 400 → `BAD_REQUEST`
- 401 → `UNAUTHORIZED`
- 404 → `NOT_FOUND`
- 429 → `RATE_LIMITED`
- 502 → `UPSTREAM_ERROR` (upstream provider failed)
- 504 → `TIMEOUT`

## Timeouts & retries
Use `httpx.AsyncClient(timeout=5.0)` plus one retry for idempotent GETs. Log the elapsed time and include a user-friendly message in 502/504.

## Observability
Log keys: `event, route, provider, duration_ms, request_id, cache`.
Echo `X-Request-ID` on responses if present.
Expose `/metrics` (JSON) with per-endpoint counters (requests, errors, cache hits).

## Runbook
- **CORS 403/blocked** → set `CVRGPT_ALLOWED_ORIGINS` or update `config.py`.
- **ModuleNotFoundError: cvrgpt_server** → set `PYTHONPATH=src` before `uvicorn`/`pytest`.
- **Compare is null** → check `/v1/accounts/latest/{cvr}`; missing previous period or parse failed; verify fact citations.
- **Slow response** → enable caching; inspect logs for `duration_ms` and `cache`=miss; confirm provider timeouts.
