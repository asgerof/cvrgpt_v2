# 🚀 CVR GPT v2 - Quick Startup Guide

## Prerequisites
- Python 3.11+ installed
- Node.js 20+ installed
- Docker Desktop running (for Redis)

## 🏃‍♂️ Quick Start

### 1. Start Redis
```bash
docker-compose up -d redis
```

### 2. Start Backend Server
```bash
cd server
.\run_server.ps1
```
*Or manually:*
```bash
cd server
$env:PYTHONPATH="src"
python -m uvicorn cvrgpt_server.api:app --port 8000 --reload
```

### 3. Start Frontend (New Terminal)
```bash
cd frontend
npm run dev
```

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/healthz
- **Readiness Check**: http://localhost:8000/readyz

## 🔑 API Key

The development API key is: `dev-key-change-me`

For API testing, include the header:
```
x-api-key: dev-key-change-me
```

## 🧪 Running Tests

### Backend Tests
```bash
cd server
$env:PYTHONPATH="src"
pytest -v
```

### Frontend Tests
```bash
cd frontend
npm run type-check
npm run build
```

## 🛠️ Development Tools

### Linting & Formatting
```bash
# Backend
cd server
ruff check .
ruff format .
mypy src/

# Frontend
cd frontend
npm run lint
npm run type-check
```

### Generate TypeScript Types
```bash
cd frontend
npm run gen:types
```

## 🐛 Troubleshooting

### Server won't start
- Make sure you're in the `server/` directory
- Verify Redis is running: `docker-compose ps`
- Check Python path is set: `$env:PYTHONPATH="src"`

### Module not found errors
- Ensure you're in the correct directory
- Verify PYTHONPATH is set to `src`
- Try: `pip install -r requirements.txt`

### Frontend build issues
- Run: `npm ci` to reinstall dependencies
- Clear build cache: `rm -rf .next`
- Regenerate types: `npm run gen:types`

## 📊 Monitoring

The application includes comprehensive monitoring:
- ✅ Health probes (`/healthz`, `/readyz`)
- 📊 Structured JSON logging
- 🔄 Request correlation IDs
- ⚡ Redis-backed caching
- 🛡️ Rate limiting protection
- 🔐 API key authentication

All requests include `x-request-id` headers for tracing.

---
🎯 **The application is now production-ready with enterprise-grade hardening!**
