# Setup Guide - Multi-Agent Loan Application System

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Anthropic API Key

## Installation Steps

### 1. Clone/Extract Project

```bash
cd "Loan Application"
```

### 2. Create Virtual Environment

```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

## Running the System

### Option 1: Automated Start (Recommended)

```bash
python scripts/run_all_services.py
```

This starts all services:
- 4 MCP Servers (ApplicantDB, RiskRulesDB, DecisionSynthesis, NotificationSystem)
- FastAPI Backend
- Streamlit UI

### Option 2: Manual Start in Separate Terminals

**Terminal 1: ApplicantDB MCP Server**
```bash
python mcp_servers/applicant_db_server.py
```

**Terminal 2: RiskRulesDB MCP Server**
```bash
python mcp_servers/risk_rules_server.py
```

**Terminal 3: DecisionSynthesis MCP Server**
```bash
python mcp_servers/decision_synthesis_server.py
```

**Terminal 4: NotificationSystem MCP Server**
```bash
python mcp_servers/notification_server.py
```

**Terminal 5: FastAPI Backend**
```bash
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 6: Streamlit UI**
```bash
streamlit run ui/streamlit_app.py
```

## Accessing the System

Once all services are running:

1. **Streamlit UI** (User Interface)
   - URL: http://localhost:8501
   - Submit applications and view decisions

2. **FastAPI Documentation**
   - URL: http://localhost:8000/docs
   - Swagger UI for API testing

3. **Health Check**
   - URL: http://localhost:8000/health
   - JSON response indicating API status

## API Endpoints

### Submit Application
```
POST /api/applications
Content-Type: application/json

{
  "applicant_id": "APP001",
  "age": 35,
  "income": 75000,
  "employment_type": "employed",
  "credit_score": 720,
  "loan_amount": 250000,
  "tenure": 20,
  "existing_liabilities": 50000,
  "location": "New York"
}
```

### Get Application Status
```
GET /api/applications/{application_id}
```

### Get Application History
```
GET /api/applications/{application_id}/history
```

### Get Statistics
```
GET /api/stats
```

## Testing the System

### 1. Via Streamlit UI

1. Open http://localhost:8501
2. Enter sample application data
3. Click "Submit Application"
4. View the decision and explanation

### 2. Via API (curl)

```bash
curl -X POST http://localhost:8000/api/applications \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "TEST001",
    "age": 35,
    "income": 75000,
    "employment_type": "employed",
    "credit_score": 720,
    "loan_amount": 250000,
    "tenure": 20,
    "existing_liabilities": 50000,
    "location": "New York"
  }'
```

### 3. Via Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/applications",
    json={
        "applicant_id": "TEST001",
        "age": 35,
        "income": 75000,
        "employment_type": "employed",
        "credit_score": 720,
        "loan_amount": 250000,
        "tenure": 20,
        "existing_liabilities": 50000,
        "location": "New York"
    }
)

print(response.json())
```

## Troubleshooting

### Port Already in Use

If you see "Address already in use" errors:

1. Find the process using the port:
   ```bash
   lsof -i :8000  # macOS/Linux
   netstat -ano | findstr :8000  # Windows
   ```

2. Kill the process or use different ports in `.env`

### API Connection Error in Streamlit

If Streamlit can't connect to FastAPI:

1. Ensure FastAPI is running on http://localhost:8000
2. Check `.env` configuration
3. Verify CORS settings in `api/main.py`

### Missing Dependencies

If you get import errors:

```bash
pip install -r requirements.txt --upgrade
```

### Anthropic API Key Issues

- Verify the API key is correct in `.env`
- Ensure the key has not expired
- Check Anthropic dashboard for API usage limits

## Project Structure

```
Loan Application/
├── requirements.txt           # Python dependencies
├── config.py                  # Configuration management
├── .env.example              # Environment template
├── README.md                 # Project overview
├── SETUP.md                  # This file
│
├── schemas/                  # Data models
│   ├── common.py            # Enums and constants
│   ├── loan_application.py  # Application schema
│   └── agent_responses.py   # Agent response schemas
│
├── mcp_servers/             # MCP server implementations
│   ├── applicant_db_server.py
│   ├── risk_rules_server.py
│   ├── decision_synthesis_server.py
│   └── notification_server.py
│
├── agents/                   # Domain-specific agents
│   ├── base_agent.py
│   ├── applicant_profile_agent.py
│   ├── financial_risk_agent.py
│   ├── loan_decision_agent.py
│   └── compliance_orchestrator_agent.py
│
├── orchestration/            # Workflow orchestration
│   ├── state.py             # Workflow state definition
│   └── workflow.py          # LangGraph workflow
│
├── api/                      # FastAPI application
│   └── main.py              # API endpoints
│
├── ui/                       # Streamlit interface
│   └── streamlit_app.py     # Chatbot UI
│
└── scripts/                  # Utility scripts
    └── run_all_services.py  # Service startup script
```

## Next Steps

1. Review [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design
2. Check [API.md](API.md) for API documentation
3. Explore [DEPLOYMENT.md](DEPLOYMENT.md) for production setup

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error logs in the terminal output
3. Ensure all services are running (`http://localhost:8000/health`)
4. Verify environment configuration in `.env`
