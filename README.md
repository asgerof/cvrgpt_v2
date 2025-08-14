# CVRGPT v2 — Live Danish Company Data with Citations

**Production-ready MVP for chat-like exploration of Danish company data (CVR) with live data sources, citations, and export functionality.**

## Quick Start (5 minutes)

### Prerequisites
- Python 3.12+
- Node.js 20+
- CVR API credentials (or use fixtures for demo)

### Backend Setup

```powershell
# Clone and setup
cd server
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configure environment (copy your credentials)
cp .env.example .env.local
# Edit .env.local with your CVR credentials

# Start API server
$env:PYTHONPATH = "src"
uvicorn cvrgpt_server.api:app --reload --port 8000
```

### Frontend Setup

```powershell
# In a new terminal
cd frontend
$env:NEXT_PUBLIC_API_BASE_URL = "http://localhost:8000"
npm install
npm run dev
```

### Smoke Test

```powershell
cd server
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "src"
python scripts/smoke.py
```

## What Works Today

✅ **Live CVR Data**: Search and company profiles via CVR Indeks  
✅ **Citations**: Every data point links back to source with timestamps  
✅ **Financial Comparison**: Key metrics with percentage changes and narrative  
✅ **CSV Export**: One-click download of comparison data  
✅ **MCP Tools**: Same functionality available to LLM agents via `/mcp`  
✅ **Error Handling**: Standardized error codes and graceful fallbacks  
✅ **Caching**: TTL cache for API responses with cache hit/miss headers  

## API Endpoints

| Endpoint | Description | Response |
|----------|-------------|----------|
| `GET /v1/search?q={query}` | Search companies | Companies with CVR, name, status |
| `GET /v1/company/{cvr}` | Company profile | Full company details + citations |
| `GET /v1/filings/{cvr}` | Recent filings | Filing list (scaffolded) |
| `GET /v1/accounts/latest/{cvr}` | Latest accounts | Financial data (scaffolded) |
| `GET /v1/compare/{cvr}` | Compare accounts | Key changes + narrative + sources |
| `GET /v1/compare/{cvr}/export` | Export comparison | CSV download |

## Environment Variables

```bash
# Provider selection
CVRGPT_PROVIDER=cvr_api              # or "fixtures" for demo

# CVR API access
CVRGPT_API_BASE_URL=http://distribution.virk.dk/cvr-permanent
CVRGPT_API_USER=your_username
CVRGPT_API_PASSWORD=your_password

# Optional: OpenAI for future LLM features
OPENAI_API_KEY=sk-...

# CORS (for frontend)
CVRGPT_ALLOWED_ORIGINS=http://localhost:3000
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Next.js UI   │────│   FastAPI REST   │────│ CompositeProvider│
│                 │    │                  │    │                 │
│ • Search        │    │ • /v1/search     │    │ • CVRApiProvider│
│ • Profile       │    │ • /v1/company    │    │ • RegnskabProvider│
│ • Compare       │    │ • /v1/compare    │    │ • Citations     │
│ • Export CSV    │    │ • /mcp (tools)   │    │ • Error handling│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

**Provider Architecture**: Clean separation between CVR core data (search/profiles) and regnskab data (filings/accounts). Easy to extend with additional data sources.

**Citations Pipeline**: Every response includes `sources[]` with URLs, labels, and access timestamps for full traceability.

## Development

### Run Tests
```powershell
cd server
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "src"
pytest
```

### MCP Tools (for LLM agents)
```bash
# Stdio mode
python -m cvrgpt_server.mcp_server stdio

# SSE mode (mounted at /mcp in main app)
curl http://localhost:8000/mcp/tools
```

### Error Codes
- `NOT_FOUND`: Company/data not found
- `UPSTREAM_ERROR`: CVR API unavailable  
- `RATE_LIMIT`: API rate limit exceeded
- `PROVIDER_DOWN`: Service unavailable
- `INSUFFICIENT_DATA`: Not enough data for comparison

## Next Steps

**Week 1 Priority**:
- [ ] Implement real filings from Offentliggørelser
- [ ] Parse 6 key financial facts from iXBRL/PDF
- [ ] Add watchlist + basic alerts
- [ ] OpenAPI spec for Power Automate

**Backlog**:
- Deep iXBRL parsing with line-item drill-downs
- Excel add-in and Teams bot integration  
- Multi-provider federation and failover
- Usage metrics and pricing toggle

## Support

- **Issues**: Create GitHub issue with error logs
- **API Docs**: Visit `/docs` when server is running
- **MCP Tools**: Visit `/mcp` for tool definitions

---

Built with FastAPI, Next.js, and modern Python typing. Production-ready with proper error handling, caching, and observability.