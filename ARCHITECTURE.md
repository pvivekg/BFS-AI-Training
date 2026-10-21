# System Architecture - Multi-Agent Loan Application System

## Overview

The Loan Application System is a distributed microservices architecture using agentic AI to automate loan decision-making. The system leverages Claude Sonnet 4.6 with specialized agents coordinated through LangGraph to provide explainable, auditable lending decisions.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│              Streamlit Chatbot Interface (8501)             │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP
┌────────────────────────▼────────────────────────────────────┐
│                   Microservice Layer                        │
│         FastAPI REST API Server (8000)                      │
│  • Application Submission                                   │
│  • Status Tracking                                          │
│  • Statistics                                               │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                 Orchestration Layer                         │
│            LangGraph Workflow Engine                        │
│  • Application Validation                                   │
│  • Agent Coordination                                       │
│  • State Management                                         │
│  • Error Handling                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌────▼───────┐ ┌──────▼────────┐ ┌───────────┐
│  Applicant     │ │ Financial  │ │    Loan      │ │Compliance │
│  Profile       │ │   Risk     │ │  Decision    │ │Orchestr.  │
│  Agent         │ │   Agent    │ │   Agent      │ │  Agent    │
│  (Claude)      │ │ (Claude)   │ │ (Claude)     │ │(Claude)   │
└───────┬────────┘ └────┬───────┘ └──────┬───────┘ └─────┬─────┘
        │                │               │              │
        │ MCP Tools      │ MCP Tools     │ MCP Tools    │ MCP Tools
        │                │               │              │
┌───────▼────────┐ ┌────▼───────┐ ┌──────▼────────┐ ┌───────────┐
│ ApplicantDB    │ │RiskRulesDB │ │DecisionSynth  │ │Notification
│ MCP Server     │ │ MCP Server │ │ MCP Server    │ │ MCP Server
│ (8001)         │ │ (8002)     │ │ (8003)        │ │ (8004)
└────────────────┘ └────────────┘ └───────────────┘ └───────────┘
```

## Component Details

### 1. Presentation Layer

**Streamlit UI** (`ui/streamlit_app.py`)

- User interface for loan application submission
- Real-time application status tracking
- Decision visualization with explanations
- Application history and statistics
- Session state management

**Key Features:**
- Form validation with Streamlit widgets
- Real-time processing status indicator
- Decision card with risk score visualization
- Audit trail display
- System statistics dashboard

### 2. Microservice Layer

**FastAPI Backend** (`api/main.py`)

REST API endpoints:
- `POST /api/applications` - Submit loan application
- `GET /api/applications/{application_id}` - Get application status
- `GET /api/applications/{application_id}/history` - Get decision history
- `GET /api/stats` - Get system statistics
- `GET /health` - Health check endpoint

**Features:**
- Request validation using Pydantic models
- CORS support for cross-origin requests
- In-memory application storage
- Error handling and logging
- Workflow invocation

### 3. Orchestration Layer

**LangGraph Workflow** (`orchestration/workflow.py`)

Multi-step workflow that:
1. Validates input data
2. Invokes Applicant Profile Agent
3. Invokes Financial Risk Agent
4. Invokes Loan Decision Agent
5. Invokes Compliance Orchestrator
6. Returns final decision

**State Management** (`orchestration/state.py`)
- `WorkflowState` dataclass tracking:
  - Application data
  - Intermediate analysis results
  - Final decision
  - Compliance records
  - Processing status
  - Error log

### 4. Agent Layer

#### Applicant Profile Agent (`agents/applicant_profile_agent.py`)

**Purpose:** Analyze applicant background and employment history

**MCP Tools Used:**
- `get_applicant_profile()` - Basic profile info
- `get_employment_history()` - Employment tenure and stability
- `get_credit_history()` - Credit history summary
- `generate_applicant_analysis()` - Comprehensive analysis

**Output:** `ApplicantProfileResponse`
- Income Stability Score (0-100)
- Employment Risk Level
- Credit History Summary
- Application Completeness Flags

#### Financial Risk Agent (`agents/financial_risk_agent.py`)

**Purpose:** Analyze financial metrics and assess risk

**MCP Tools Used:**
- `calculate_dti_ratio()` - Debt-to-Income ratio
- `assess_credit_risk()` - Credit score risk level
- `assess_loan_risk()` - Loan amount risk assessment
- `detect_anomalies()` - Financial anomaly detection
- `generate_risk_analysis()` - Comprehensive risk analysis

**Output:** `RiskAnalysisResponse`
- Debt-to-Income Ratio
- Credit Score Risk Level
- Loan Amount Risk Level
- Anomaly Detection Flags
- Reasoning

#### Loan Decision Agent (`agents/loan_decision_agent.py`)

**Purpose:** Synthesize analysis into approval/rejection decision

**MCP Tools Used:**
- `synthesize_decision()` - Make decision based on factors
- `calculate_risk_score()` - Compute overall risk score
- `explain_decision()` - Generate decision reasoning
- `generate_decision_report()` - Comprehensive report

**Output:** `LoanDecisionResponse`
- Classification (Approve/Reject/Review)
- Risk Score (0-100)
- Confidence Level (0-1)
- Key Decision Factors
- Explanation

#### Compliance Orchestrator Agent (`agents/compliance_orchestrator_agent.py`)

**Purpose:** Execute decision and create audit trail

**MCP Tools Used:**
- `create_case()` - Create case record
- `send_notification()` - Send applicant notification
- `log_action()` - Log to audit trail
- `execute_decision()` - Execute decision
- `generate_compliance_report()` - Create compliance record

**Output:** `ComplianceResponse`
- Action Taken
- Notification Sent Status
- Case ID
- Timestamp
- Summary

### 5. Communication Layer

**MCP Servers** - Implement Model Context Protocol

Each server:
- Exposes tools for agents to invoke
- Uses FastMCP for protocol implementation
- Provides mock data for MVP
- Returns structured responses

**Servers:**
1. **ApplicantDB** (8001) - Applicant profile data
2. **RiskRulesDB** (8002) - Financial rules and calculations
3. **DecisionSynthesis** (8003) - Decision logic
4. **NotificationSystem** (8004) - Notifications and audit

## Data Models

### Schemas

**`schemas/common.py`** - Enums
- `EmploymentType` - Employment status
- `Location` - Geographic location
- `RiskLevel` - Risk assessment levels
- `Decision` - Approval/Rejection/Review
- `Status` - Processing status

**`schemas/loan_application.py`** - Input
- `LoanApplication` - Complete application data

**`schemas/agent_responses.py`** - Outputs
- `ApplicantProfileResponse`
- `RiskAnalysisResponse`
- `LoanDecisionResponse`
- `ComplianceResponse`

## Workflow Sequence

```
1. User Submission
   └─> Streamlit UI captures application data
   └─> Sends to FastAPI backend

2. API Processing
   └─> FastAPI validates input
   └─> Creates WorkflowState
   └─> Invokes LangGraph workflow

3. Applicant Analysis
   └─> Applicant Profile Agent receives state
   └─> Calls ApplicantDB MCP tools
   └─> Returns ApplicantProfileResponse
   └─> Updates state

4. Risk Analysis
   └─> Financial Risk Agent receives state
   └─> Calls RiskRulesDB MCP tools
   └─> Returns RiskAnalysisResponse
   └─> Updates state

5. Decision Synthesis
   └─> Loan Decision Agent receives state
   └─> Calls DecisionSynthesis MCP tools
   └─> Returns LoanDecisionResponse
   └─> Updates state

6. Compliance Execution
   └─> Compliance Agent receives state
   └─> Calls NotificationSystem MCP tools
   └─> Returns ComplianceResponse
   └─> Updates state

7. Response Generation
   └─> Workflow finalizes state
   └─> FastAPI formats response
   └─> Returns to Streamlit UI

8. Display
   └─> Streamlit shows decision
   └─> Displays explanation and factors
   └─> Allows history view
```

## Decision Logic

### Risk Score Calculation

The Loan Decision Agent calculates a risk score (0-100) based on:

```
Base Score: 50

Income Stability: -25% of score
Employment Risk: -10 (low) to +20 (very high)
DTI Ratio: -15 (< 0.3) to +15 (> 0.7)
Credit Risk: -15 (low) to +20 (very high)
Loan Amount Risk: -10 (low) to +25 (very high)
Anomalies: +10 per anomaly detected

Final Score: Clamped to 0-100 range
```

### Decision Classification

```
Risk Score < 30: APPROVE (Confidence: 95%)
Risk Score 30-50: APPROVE (Confidence: 75%)
Risk Score 50-65: REVIEW (Confidence: 80%)
Risk Score 65-80: REJECT (Confidence: 75%)
Risk Score > 80: REJECT (Confidence: 95%)
```

## Error Handling

1. **Input Validation**
   - Missing applicant ID
   - Invalid income/credit score
   - Out-of-range values

2. **Agent Errors**
   - Logged to error_log
   - Workflow stops and returns FAILED status
   - No partial decisions propagated

3. **MCP Tool Errors**
   - Caught and logged
   - Graceful degradation
   - Returns error response

4. **Compliance Failures**
   - Decision still executes
   - Error logged in audit trail
   - Status marked as FAILED

## State Persistence

Currently: In-memory storage via Python dictionary

Future enhancements:
- PostgreSQL for persistent storage
- Redis for caching
- Event streaming (Kafka)
- Document store (MongoDB)

## Security Considerations

1. **API Security**
   - Input validation via Pydantic
   - CORS configured
   - No authentication required for MVP

2. **Data Protection**
   - PII handled per application data
   - Audit trail immutable
   - No sensitive data in logs

3. **Audit Trail**
   - Complete decision history
   - All agent reasoning captured
   - Case ID for tracking

## Scalability

Current MVP: Single instance, in-memory

Future scaling:
- Containerize with Docker
- Deploy with Kubernetes
- Use API gateway (Kong)
- Implement message queue (RabbitMQ)
- Database replication
- Agent load balancing

## Technology Choices

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| LLM | Claude Sonnet 4.6 | Balance of speed, cost, quality |
| Orchestration | LangGraph | Native multi-agent support |
| API | FastAPI | High performance, async support |
| UI | Streamlit | Rapid development, great UX |
| Validation | Pydantic | Type safety, automatic validation |
| MCP Protocol | FastMCP | Standardized tool interface |

## Performance Characteristics

- **Latency**: ~5-10 seconds per application (depends on Claude API)
- **Throughput**: Limited by Claude API rate limits (MVP)
- **Scalability**: Horizontal via containerization and load balancing
- **Storage**: Unlimited with persistent database backend

## Monitoring & Observability

Currently implemented:
- Logging to console
- Error tracking in state
- Statistics endpoint
- Health check endpoint

Future enhancements:
- Prometheus metrics
- Grafana dashboards
- Distributed tracing (Jaeger)
- ELK stack for logs
- Alert system
