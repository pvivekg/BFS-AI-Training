#!/usr/bin/env python3
"""NotificationSystem MCP Server - Handles notifications and action logging."""

import json
import uuid
from datetime import datetime
from fastmcp import Server
from schemas.agent_responses import ComplianceResponse

app = Server("notification_server")

# In-memory audit log
AUDIT_LOG = {}
NOTIFICATIONS_SENT = {}


@app.tool()
def create_case(applicant_id: str, decision: str) -> dict:
    """Create a case record for the application."""
    case_id = f"CASE_{uuid.uuid4().hex[:8].upper()}"

    case_record = {
        "case_id": case_id,
        "applicant_id": applicant_id,
        "decision": decision,
        "created_at": datetime.utcnow().isoformat(),
        "status": "created",
    }

    AUDIT_LOG[case_id] = case_record
    return case_record


@app.tool()
def send_notification(applicant_id: str, decision: str, case_id: str) -> dict:
    """Send notification to applicant about the decision."""

    notification = {
        "notification_id": str(uuid.uuid4()),
        "applicant_id": applicant_id,
        "case_id": case_id,
        "decision": decision,
        "message": f"Your loan application has been {decision}. Case ID: {case_id}",
        "sent_at": datetime.utcnow().isoformat(),
        "channel": "email",
        "status": "sent",
    }

    NOTIFICATIONS_SENT[notification["notification_id"]] = notification
    return notification


@app.tool()
def log_action(
    case_id: str,
    applicant_id: str,
    action_type: str,
    details: str,
    actor: str = "system",
) -> dict:
    """Log an action in the audit trail."""

    action_record = {
        "action_id": str(uuid.uuid4()),
        "case_id": case_id,
        "applicant_id": applicant_id,
        "action_type": action_type,
        "details": details,
        "actor": actor,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if case_id not in AUDIT_LOG:
        AUDIT_LOG[case_id] = []

    if isinstance(AUDIT_LOG[case_id], dict):
        AUDIT_LOG[case_id] = [AUDIT_LOG[case_id]]

    if isinstance(AUDIT_LOG[case_id], list):
        AUDIT_LOG[case_id].append(action_record)
    else:
        AUDIT_LOG[case_id] = action_record

    return action_record


@app.tool()
def execute_decision(
    applicant_id: str,
    case_id: str,
    classification: str,
    risk_score: float,
    explanation: str,
) -> dict:
    """Execute the loan decision and create audit trail."""

    decision_execution = {
        "execution_id": str(uuid.uuid4()),
        "case_id": case_id,
        "applicant_id": applicant_id,
        "classification": classification,
        "risk_score": risk_score,
        "explanation": explanation,
        "executed_at": datetime.utcnow().isoformat(),
        "status": "executed",
    }

    log_action(
        case_id,
        applicant_id,
        "decision_executed",
        f"Loan decision executed: {classification}",
    )

    return decision_execution


@app.tool()
def get_case_details(case_id: str) -> dict:
    """Retrieve case details and audit trail."""
    if case_id not in AUDIT_LOG:
        return {"error": f"Case {case_id} not found"}

    return {
        "case_id": case_id,
        "details": AUDIT_LOG[case_id],
        "record_count": 1 if isinstance(AUDIT_LOG[case_id], dict) else len(AUDIT_LOG[case_id]),
    }


@app.tool()
def generate_compliance_report(
    applicant_id: str,
    case_id: str,
    classification: str,
) -> str:
    """Generate compliance report for the loan decision."""

    execution_result = execute_decision(
        applicant_id, case_id, classification, 0.0, "Compliance report generated"
    )

    send_notification(applicant_id, classification, case_id)

    response = ComplianceResponse(
        applicant_id=applicant_id,
        case_id=case_id,
        action_taken=classification.upper(),
        notification_sent=True,
        summary=f"Loan application decision executed and applicant notified. Decision: {classification}",
    )

    return response.model_dump_json()


if __name__ == "__main__":
    app.run()
