# server/run.ps1
param(
  [int]$Port = 8000
)

Set-Location -Path "$PSScriptRoot"
if (-not (Test-Path .venv)) { python -m venv .venv }
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
uvicorn cvrgpt_server.api:app --reload --port $Port
