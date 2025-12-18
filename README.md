# Spike AI Backend

## Architecture Overview

A production-ready AI backend for natural language queries about web analytics and SEO data. The system uses a **multi-agent architecture** with an intelligent orchestrator that routes requests to specialized agents.

**See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture diagrams including system flow, agent interactions, and orchestrator routing.**

### Project Structure

```
.
├── app/
│   ├── agents/
│   │   ├── analytics.py    # Tier 1: GA4 Agent with allowlist validation
│   │   └── seo.py          # Tier 2: SEO Agent (Google Sheets + Pandas)
│   ├── llm/
│   │   ├── client.py       # LiteLLM Client with retry logic & structured outputs
│   │   └── schemas.py      # Pydantic schemas for type-safe LLM responses
│   ├── models.py           # API request/response models
│   └── orchestrator.py     # Intent detection & multi-agent routing
├── main.py                 # FastAPI application entry point
├── deploy.sh               # Setup and run script
├── requirements.txt        # Python dependencies
├── credentials.json        # Google Service Account key (not in repo)
├── spreadsheets.json       # Google Sheets configuration
└── .env                    # Environment variables (not in repo)
```

### Key Features

| Feature | Description |
|---------|-------------|
| **Structured LLM Outputs** | Pydantic schemas ensure type-safe, validated responses from the LLM |
| **Intent Classification** | LLM-based routing determines which agent(s) should handle a query |
| **Multi-Agent Fusion** | Tier 3 queries can combine data from both Analytics and SEO agents |
| **Metric/Dimension Allowlist** | GA4 queries are validated against safe allowlists before execution |
| **Multiple Spreadsheets** | SEO agent supports loading from multiple Google Sheets |

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- Google Service Account with access to:
  - Google Analytics Data API
  - Google Sheets API
- LiteLLM API key

### 1. Clone and Configure

```bash
# Clone the repository
git clone https://github.com/raghavagarwal701/spike_ai
cd spike_ai

# Copy environment template
cp .env.example .env
```

### 2. Environment Variables

Edit `.env` with your configuration:

```bash
# LiteLLM Configuration
LITELLM_API_KEY=your_litellm_api_key_here
LITELLM_BASE_URL=http://3.110.18.218

# Google Service Account Credentials file path
GOOGLE_CREDENTIALS_FILE=credentials.json

# Spreadsheets configuration file path
SPREADSHEETS_CONFIG_FILE=spreadsheets.json
```

### 3. Google Service Account Credentials

Place your `credentials.json` (Google Service Account key) in the project root. This file must have:
- Google Analytics Data API enabled
- Google Sheets API enabled
- Access to the GA4 properties you want to query
- Spreadsheet shared with the service account email

### 4. Configure Spreadsheets

Edit `spreadsheets.json` to specify your SEO data sources:

```json
{
  "spreadsheets": [
    {
      "name": "my_seo_data",
      "source": "SPREADSHEET_ID_OR_FULL_URL",
      "description": "Optional description"
    }
  ]
}
```

The `source` field accepts either:
- Direct spreadsheet ID: `1zzf4ax_H2WiTBVrJigGjF2Q3Yz-qy2qMCbAMKvl6VEE`
- Full Google Sheets URL: `https://docs.google.com/spreadsheets/d/1zzf4ax.../edit`

### 5. Install and Run

```bash
bash deploy.sh
```

This script will:
1. Create a virtual environment (if not exists)
2. Install dependencies via `uv` or `pip`
3. Start the server on `http://localhost:8080`

---

## Data Source Integrations

### Google Analytics 4 (Tier 1)

**Connection**: GA4 Data API via Google Service Account

**Capabilities**:
- Live data queries for users, sessions, page views, conversions
- Support for 30+ metrics including `activeUsers`, `sessions`, `screenPageViews`, `bounceRate`, etc.
- Support for 40+ dimensions including `date`, `pagePath`, `country`, `deviceCategory`, etc.
- Automatic allowlist validation to prevent invalid API calls

**Example Query**:
```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "propertyId": "516747840",
    "query": "Give me a daily breakdown of users for the last 7 days"
  }'
```

### Google Sheets / Screaming Frog SEO Data (Tier 2)

**Connection**: Google Sheets API via Service Account + gspread

**Capabilities**:
- Load multiple spreadsheets with multiple worksheets
- Automatic schema detection and DataFrame creation
- LLM-generated Pandas code for complex analysis
- Support for URL/link format or direct spreadsheet IDs

**Example Query**:
```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which URLs do not use HTTPS?"
  }'
```

### Multi-Agent Fusion (Tier 3)

**Connection**: Combines data from both GA4 and Google Sheets

**Capabilities**:
- LLM-based intent detection to route multi-source queries
- Automatic query decomposition into agent-specific sub-queries
- URL normalization for cross-agent data matching
- JSON or natural language output formats

**Example Query**:
```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "propertyId": "516747840",
    "query": "Show me top pages by views along with their SEO title tags as JSON"
  }'
```

---

## API Reference

### POST /query

**Request Body**:
```json
{
  "query": "string (required) - Natural language question",
  "propertyId": "string (optional) - GA4 property ID for analytics queries"
}
```

**Response**:
```json
{
  "answer": "string - Natural language or JSON answer"
}
```

### GET /health

Health check endpoint.

**Response**: `{"status": "ok"}`

---

## Testing

Run the operational test script to verify both agents:

```bash
python3 test_system.py
```

---

## Assumptions and Limitations

### Assumptions

| Assumption | Details |
|------------|---------|
| **Single Credentials File** | `credentials.json` provides access to both GA4 Data API and Google Sheets API |
| **Shared Spreadsheets** | Google Sheets are shared with the service account email address |
| **LiteLLM Proxy** | LiteLLM API is accessible at the configured base URL |
| **Gemini 2.5 Flash** | Default LLM model is `gemini-2.5-flash` for all inference tasks |

### Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Code Execution via `exec()`** | SEO Agent executes LLM-generated Python code using `exec()` | Sandboxed with limited local variables (`dfs`, `pd` only) |
| **No Persistent Cache** | Google Sheets data is fetched on server startup | Call `seo_agent.refresh_data()` or restart server for updates |
| **Rate Limiting** | LLM API has rate limits | Built-in exponential backoff retry logic (max 5 retries) |
| **Basic Multi-Agent Fusion** | Cross-agent URL matching relies on path normalization | Best effort matching between GA4 paths and full URLs |
| **No Authentication** | API endpoints are not authenticated | Add authentication middleware for production deployment |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework for API |
| `uvicorn` | ASGI server |
| `pandas` | Data manipulation for SEO analysis |
| `google-analytics-data` | GA4 Data API client |
| `openai` | OpenAI-compatible client for LiteLLM |
| `python-dotenv` | Environment variable management |
| `gspread` | Google Sheets access |
| `oauth2client` | Google OAuth2 credentials |
| `openpyxl` | Excel file support |
