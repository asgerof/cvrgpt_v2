# PowerShell script to run the CVR GPT server
# Usage: .\run_server.ps1

Write-Host "🚀 Starting CVR GPT Server..." -ForegroundColor Green
Write-Host "📁 Working directory: $(Get-Location)" -ForegroundColor Gray

# Set Python path to include src directory
$env:PYTHONPATH = "src"

# Start the server with reload for development
Write-Host "🐍 Python path: $env:PYTHONPATH" -ForegroundColor Gray
Write-Host "🌐 Server will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API docs will be available at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🔄 Auto-reload enabled for development" -ForegroundColor Yellow
Write-Host ""

try {
    C:\Users\asger\AppData\Local\Programs\Python\Python311\python.exe -m uvicorn cvrgpt_server.api:app --port 8000 --reload --host 0.0.0.0
} catch {
    Write-Host "❌ Failed to start server: $_" -ForegroundColor Red
    Write-Host "💡 Make sure you're in the server directory and Redis is running" -ForegroundColor Yellow
    Write-Host "🔧 Try: docker-compose up -d redis" -ForegroundColor Yellow
}
