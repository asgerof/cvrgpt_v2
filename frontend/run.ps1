# frontend/run.ps1
param(
  [string]$ApiBase = "http://localhost:8000"
)

Set-Location -Path "$PSScriptRoot"
$env:NEXT_PUBLIC_API_BASE_URL = $ApiBase
if (-not (Test-Path node_modules)) { npm install }
npm run dev