.PHONY: dev backend frontend test lint typecheck

dev:
	( cd server && .\.venv\Scripts\Activate.ps1 && $$env:PYTHONPATH="src" && uvicorn cvrgpt_server.api:app --reload --port 8000 ) & \
	( cd frontend && npm run dev )

backend:
	cd server && .\.venv\Scripts\Activate.ps1 && $$env:PYTHONPATH="src" && uvicorn cvrgpt_server.api:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd server && .\.venv\Scripts\Activate.ps1 && pytest -q

lint:
	cd server && .\.venv\Scripts\Activate.ps1 && ruff check . ; cd ../frontend && npm run lint

typecheck:
	cd server && .\.venv\Scripts\Activate.ps1 && mypy . ; cd ../frontend && npm run type-check
