# API Documentation - Loan Application System

## Overview

The FastAPI backend provides REST endpoints for submitting loan applications and retrieving decisions. The API is built with FastAPI and runs on `http://localhost:8000`.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication is required for the MVP. Future versions will implement API key authentication.

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check if the API is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-10-19T12:34:56.789123",
  "service": "Loan Application Analysis API"
}
```

### 2. Submit Loan Application

**Endpoint:** `POST /api/applications`

**Description:** Submit a loan application for analysis. The API processes the application through the multi-agent workflow and returns a decision.

**Request Body:**
```json
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

**Parameters:**

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| applicant_id | string | - | Unique applicant identifier |
| age | integer | 18-100 | Applicant age in years |
| income | number | > 0 | Annual income in dollars |
| employment_type | string | employed, self_employed, unemployed, retired | Employment status |
| credit_score | integer | 300-850 | Credit score |
| loan_amount | number | > 0 | Requested loan amount in dollars |
| tenure | integer | 1-30 | Loan repayment period in years |
| existing_liabilities | number | >= 0 | Current outstanding debts |
| location | string | See enum | Applicant location |

**Employment Types:**
- `employed` - Full-time employment
- `self_employed` - Self-employed/business owner
- `unemployed` - Currently unemployed
- `retired` - Retired

**Locations:**
- New York
- California
- Texas
- Florida
- Illinois
- Pennsylvania
- Ohio
- Georgia
- North Carolina
- Other

**Response (Success - 200):**
```json
{
  "application_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "applicant_id": "APP001",
  "decision": {
    "classification": "approve",
    "risk_score": 42.5,
    "confidence_level": 0.85,
    "explanation": "Decision: APPROVE. Risk Score: 43/100. Strong income stability (80%) supports approval. Stable employment status is positive. Excellent credit history supports approval. Low debt-to-income ratio (0.67%) supports approval. Loan amount risk level is low.",
    "key_factors": [
      "Strong income stability (80%) supports approval",
      "Stable employment status is positive",
      "Excellent credit history supports approval",
      "Low debt-to-income ratio (0.67%) supports approval",
      "Loan amount risk level is low"
    ]
  },
  "processing_time": 8.234,
  "timestamp": "2024-10-19T12:34:56.789123"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| application_id | string | Unique application identifier |
| status | string | Processing status (pending, processing, completed, failed) |
| applicant_id | string | The submitted applicant ID |
| decision | object | Loan decision details |
| decision.classification | string | approve, reject, or review |
| decision.risk_score | number | Overall risk score (0-100) |
| decision.confidence_level | number | Decision confidence (0-1) |
| decision.explanation | string | Detailed explanation of decision |
| decision.key_factors | array | Key factors influencing decision |
| processing_time | number | Seconds to process application |
| timestamp | string | ISO 8601 timestamp |

**Response (Error - 400):**
```json
{
  "detail": {
    "error": "Application processing failed",
    "errors": [
      "Invalid income",
      "Credit score out of range"
    ]
  }
}
```

**Response (Error - 500):**
```json
{
  "detail": {
    "error": "Internal server error",
    "message": "Detailed error message"
  }
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/applications \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "APP001",
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

### 3. Get Application Status

**Endpoint:** `GET /api/applications/{application_id}`

**Description:** Retrieve the current status and details of a loan application.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| application_id | string | Unique application identifier |

**Response (Success - 200):**
```json
{
  "application_id": "550e8400-e29b-41d4-a716-446655440000",
  "applicant_id": "APP001",
  "status": "completed",
  "applicant_analysis": {
    "applicant_id": "APP001",
    "income_stability_score": 80.0,
    "employment_risk": "low",
    "credit_history_summary": "Good payment history, minor late payment 2 years ago",
    "application_completeness_flags": [],
    "analysis_timestamp": "2024-10-19T12:34:56.789123"
  },
  "risk_analysis": {
    "applicant_id": "APP001",
    "debt_to_income_ratio": 0.0067,
    "credit_score_risk_level": "low",
    "loan_amount_risk": "low",
    "anomaly_detection_flags": [],
    "reasoning": "DTI ratio of 0.67% indicates excellent debt management. Credit score of 720 shows excellent credit profile. Loan-to-income ratio of 3.33 suggests low risk.",
    "analysis_timestamp": "2024-10-19T12:34:56.789123"
  },
  "decision": {
    "applicant_id": "APP001",
    "classification": "approve",
    "risk_score": 42.5,
    "confidence_level": 0.85,
    "key_decision_factors": [
      "Strong income stability (80%) supports approval",
      "Stable employment status is positive",
      "Excellent credit history supports approval"
    ],
    "explanation": "Decision: APPROVE...",
    "decision_timestamp": "2024-10-19T12:34:56.789123"
  },
  "compliance": {
    "applicant_id": "APP001",
    "case_id": "CASE_ABC123DEF",
    "action_taken": "APPROVE",
    "notification_sent": true,
    "timestamp": "2024-10-19T12:34:56.789123",
    "summary": "Loan application decision executed and applicant notified..."
  },
  "error_log": [],
  "created_at": "2024-10-19T12:34:48.789123",
  "updated_at": "2024-10-19T12:34:56.789123"
}
```

**Response (Error - 404):**
```json
{
  "detail": {
    "error": "Application not found"
  }
}
```

**Example (curl):**
```bash
curl http://localhost:8000/api/applications/550e8400-e29b-41d4-a716-446655440000
```

### 4. Get Application History

**Endpoint:** `GET /api/applications/{application_id}/history`

**Description:** Get complete history and audit trail of a loan application including all analysis steps.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| application_id | string | Unique application identifier |

**Response (Success - 200):**
```json
{
  "application_id": "550e8400-e29b-41d4-a716-446655440000",
  "applicant_id": "APP001",
  "timeline": [
    {
      "step": "Application Submitted",
      "timestamp": "2024-10-19T12:34:48.789123",
      "status": "completed"
    }
  ],
  "analyses": {
    "applicant_profile": {
      "applicant_id": "APP001",
      "income_stability_score": 80.0,
      "employment_risk": "low",
      "credit_history_summary": "Good payment history...",
      "application_completeness_flags": [],
      "analysis_timestamp": "2024-10-19T12:34:52.789123"
    },
    "financial_risk": {
      "applicant_id": "APP001",
      "debt_to_income_ratio": 0.0067,
      "credit_score_risk_level": "low",
      "loan_amount_risk": "low",
      "anomaly_detection_flags": [],
      "reasoning": "DTI ratio of 0.67% indicates excellent debt management...",
      "analysis_timestamp": "2024-10-19T12:34:53.789123"
    },
    "loan_decision": {
      "applicant_id": "APP001",
      "classification": "approve",
      "risk_score": 42.5,
      "confidence_level": 0.85,
      "key_decision_factors": [...],
      "explanation": "Decision: APPROVE...",
      "decision_timestamp": "2024-10-19T12:34:54.789123"
    }
  },
  "final_outcome": {
    "classification": "approve",
    "risk_score": 42.5,
    "explanation": "Decision: APPROVE..."
  },
  "compliance": {
    "applicant_id": "APP001",
    "case_id": "CASE_ABC123DEF",
    "action_taken": "APPROVE",
    "notification_sent": true,
    "timestamp": "2024-10-19T12:34:56.789123",
    "summary": "Loan application decision executed..."
  },
  "errors": [],
  "processing_complete": true
}
```

**Example (curl):**
```bash
curl http://localhost:8000/api/applications/550e8400-e29b-41d4-a716-446655440000/history
```

### 5. Get Statistics

**Endpoint:** `GET /api/stats`

**Description:** Get statistics about all processed applications in the current session.

**Response (Success - 200):**
```json
{
  "total_applications": 10,
  "approved": 6,
  "rejected": 2,
  "review": 1,
  "failed": 1,
  "approval_rate": 75.0
}
```

**Example (curl):**
```bash
curl http://localhost:8000/api/stats
```

## Error Handling

### HTTP Status Codes

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | Success | Application submitted/retrieved successfully |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Application ID doesn't exist |
| 500 | Server Error | Internal processing error |

### Error Response Format

```json
{
  "detail": {
    "error": "Error category",
    "message": "Detailed error message",
    "errors": ["List of specific errors if applicable"]
  }
}
```

## Rate Limiting

Currently no rate limiting is implemented. Future versions will implement:
- API key-based rate limiting
- Per-application rate limits
- Burst allowances

## Pagination

Not applicable for MVP. Future versions may implement pagination for history endpoints.

## Versioning

Current API version: 1.0.0

The API follows semantic versioning. Future breaking changes will increment the major version.

## CORS

The API is configured to accept requests from any origin (`*`). This can be restricted in `api/main.py` for production deployments.

## Interactive API Documentation

Swagger UI is available at: `http://localhost:8000/docs`

ReDoc is available at: `http://localhost:8000/redoc`

These provide interactive API exploration and testing.

## Python Client Example

```python
import requests
import json

# Submit application
response = requests.post(
    "http://localhost:8000/api/applications",
    json={
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
)

if response.status_code == 200:
    result = response.json()
    app_id = result["application_id"]
    print(f"Application ID: {app_id}")
    print(f"Decision: {result['decision']['classification'].upper()}")
    print(f"Explanation: {result['decision']['explanation']}")
    
    # Get detailed status
    status_response = requests.get(
        f"http://localhost:8000/api/applications/{app_id}"
    )
    status = status_response.json()
    print(f"Risk Score: {status['decision']['risk_score']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

## Testing the API

### Using curl

```bash
# Submit application
curl -X POST http://localhost:8000/api/applications \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "applicant_id": "TEST001",
  "age": 40,
  "income": 100000,
  "employment_type": "employed",
  "credit_score": 750,
  "loan_amount": 300000,
  "tenure": 25,
  "existing_liabilities": 25000,
  "location": "California"
}
EOF

# Get stats
curl http://localhost:8000/api/stats
```

### Using Python requests

```python
import requests

# Test endpoint
response = requests.get("http://localhost:8000/health")
print(response.json())
```

## Troubleshooting

### Connection Refused

The API server is not running. Start it with:
```bash
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

### Invalid Application ID

The application ID doesn't exist. Check the response from the submission endpoint for the correct ID.

### Processing Failed

Check the error details in the response. Common issues:
- Invalid input parameters (out of range)
- Missing required fields
- Server-side errors (check logs)

### Slow Response Times

The API depends on Claude API response times, which can be 5-10 seconds per application. Ensure you have a stable internet connection.
