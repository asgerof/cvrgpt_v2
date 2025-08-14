.PHONY: dev backend frontend test lint typecheck

dev:
	powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd server; .\.venv\Scripts\Activate.ps1; uvicorn cvrgpt_server.api:app --reload --port 8000'"
	powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd frontend; npm run dev'"

backend:
	cd server && .\.venv\Scripts\Activate.ps1 && uvicorn cvrgpt_server.api:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd server && .\.venv\Scripts\Activate.ps1 && pytest -q

lint:
	cd server && .\.venv\Scripts\Activate.ps1 && ruff check .
	cd frontend && npm run lint

typecheck:
	cd server && .\.venv\Scripts\Activate.ps1 && mypy .
	cd frontend && npm run type-check
