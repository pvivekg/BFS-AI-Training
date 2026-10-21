# Multi-Agent Loan Application System

An end-to-end automated loan application analysis system using agentic AI with a multi-agent architecture. The system provides explainable, auditable decisions through a scalable microservices architecture.

## Overview

The system automates loan application analysis by orchestrating specialized agents that collaborate through MCP (Model Context Protocol) servers to evaluate applicants and make lending decisions.

### Key Features
- **Multi-Agent Architecture**: 4 domain-specific agents handle different evaluation aspects
- **Explainable Decisions**: All decisions include reasoning and key decision factors
- **Microservices Design**: Independent, loosely-coupled components
- **Audit Trail**: Complete logging of all decisions and actions
- **Web UI**: Streamlit-based chatbot interface
- **REST API**: FastAPI backend for integration

## Architecture

```
┌─────────────────────────────────────────────────────┐
│          Streamlit Chatbot UI                       │
│       (Loan Application Submission & Status)        │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│          FastAPI Microservice                       │
│       (Request Validation & Routing)                │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│      LangGraph Orchestration Engine                 │
│     (Workflow Coordination & State Management)      │
└────────────────────┬────────────────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐  ┌────────────┐
│ Applicant│  │  Financial │  │    Loan    │  │Compliance &│
│ Profile  │  │    Risk    │  │  Decision  │  │   Action   │
│  Agent   │  │   Agent    │  │   Agent    │  │Orchestrator│
└───┬──────┘  └─────┬──────┘  └─────┬──────┘  └────┬───────┘
    │              │               │              │
┌───▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐  ┌────▼───────┐
│ApplicantDB│  │RiskRulesDB │  │DecisionSyn │  │Notification│
│MCP Server │  │MCP Server  │  │ MCP Server │  │ MCP Server │
└──────────┘  └────────────┘  └────────────┘  └────────────┘
```

## System Architecture Components

### 1. Presentation Layer
- **Streamlit UI** - Interactive chatbot for loan submission and status tracking

### 2. Microservice Layer
- **FastAPI REST API** - Endpoints for application submission and status retrieval

### 3. Orchestration Layer
- **LangGraph Engine** - Multi-step workflow coordination
- **State Management** - Workflow state tracking across agents

### 4. Agent Layer
- **Applicant Profile Agent** - Evaluates applicant background
- **Financial Risk Agent** - Analyzes financial metrics
- **Loan Decision Agent** - Synthesizes decision
- **Compliance Orchestrator** - Executes and documents decision

### 5. Communication Layer
- **MCP Servers** - Standardized tool interfaces for agent communication

## Agents

### Applicant Profile Agent
- **Purpose**: Analyze applicant profile and employment history
- **Data Source**: ApplicantDB MCP Server
- **Outputs**:
  - Income Stability Score
  - Employment Risk Assessment
  - Credit History Summary
  - Application Completeness Flags

### Financial Risk Analysis Agent
- **Purpose**: Calculate financial metrics and assess risk
- **Data Source**: RiskRulesDB MCP Server
- **Outputs**:
  - Debt-to-Income Ratio
  - Credit Score Risk Level
  - Loan Amount Risk Assessment
  - Anomaly Detection Flags

### Loan Decision Agent
- **Purpose**: Synthesize analysis into approval/rejection decision
- **Data Source**: DecisionSynthesis MCP Server
- **Outputs**:
  - Classification (Approve/Reject/Review)
  - Risk Score
  - Confidence Level
  - Key Decision Factors
  - Decision Explanation

### Compliance & Action Orchestrator Agent
- **Purpose**: Execute decision and create audit trail
- **Data Source**: NotificationSystem MCP Server
- **Outputs**:
  - Action Taken
  - Notification Status
  - Case ID
  - Timestamp
  - Summary

## Workflow Sequence

1. **User Submission** - Applicant submits loan application via Streamlit UI
2. **API Validation** - FastAPI receives and validates application data
3. **Orchestration** - LangGraph workflow initiates agent sequence
4. **Applicant Analysis** - Applicant Profile Agent evaluates background
5. **Risk Analysis** - Financial Risk Agent assesses risk metrics
6. **Decision Synthesis** - Loan Decision Agent makes determination
7. **Compliance & Action** - Compliance Orchestrator executes and logs decision
8. **Response** - Decision and reasoning returned to UI for display

## Setup

### Prerequisites
- Python 3.9+
- Anthropic API Key

### Installation

1. **Clone/Extract Project**
```bash
cd "Loan Application"
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment**
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Running the System

### Option 1: Start All Services (Recommended)
```bash
python scripts/run_all_services.py
```

This will start:
1. All 4 MCP servers
2. FastAPI backend (http://localhost:8000)
3. Streamlit UI (http://localhost:8501)

### Option 2: Start Individually
```bash
# Terminal 1: ApplicantDB MCP Server
python mcp_servers/applicant_db_server.py

# Terminal 2: RiskRulesDB MCP Server
python mcp_servers/risk_rules_server.py

# Terminal 3: DecisionSynthesis MCP Server
python mcp_servers/decision_synthesis_server.py

# Terminal 4: NotificationSystem MCP Server
python mcp_servers/notification_server.py

# Terminal 5: FastAPI Backend
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 6: Streamlit UI
streamlit run ui/streamlit_app.py
```

## API Endpoints

### Submit Loan Application
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

## Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/test_agents.py

# Run with coverage
pytest --cov=.
```

## Architecture Documentation

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## License

Proprietary - Internal Use Only

## Support

For issues or questions, contact the development team.
