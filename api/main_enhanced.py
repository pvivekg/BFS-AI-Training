"""Enhanced FastAPI application with authentication and encryption."""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
from typing import Dict, Any

from schemas.loan_application import LoanApplication
from schemas.common import Status
from orchestration.workflow import LoanAnalysisWorkflow
from orchestration.state import WorkflowState
from auth import verify_api_token, TokenManager, rate_limiter
from encryption import encrypt_application_data, decrypt_application_data
from database import get_app_repository, get_audit_repository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Loan Application Analysis API (Enhanced)",
    description="Multi-agent loan analysis service with Auth & Encryption",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

application_store: Dict[str, WorkflowState] = {}
workflow = LoanAnalysisWorkflow()
app_repo = get_app_repository()
audit_repo = get_audit_repository()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Loan Application Analysis API (Enhanced)",
        "auth_enabled": True,
        "encryption_enabled": True,
        "database_enabled": True,
    }


@app.post("/auth/token")
async def get_token(api_key: str):
    """Get authentication token.

    Args:
        api_key: API key

    Returns:
        Access token
    """
    from auth import authenticate_api_key

    try:
        user_id = authenticate_api_key(api_key)
        token = TokenManager.create_access_token(user_id, api_key)
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 3600
        }
    except HTTPException as e:
        raise e


@app.post("/api/applications")
async def submit_application(
    application: LoanApplication,
    user_data: Dict[str, Any] = Depends(verify_api_token)
):
    """Submit a new loan application for analysis (with authentication).

    Args:
        application: Loan application data
        user_data: Authenticated user data from token

    Returns:
        Application decision and details
    """
    user_id = user_data.get("user_id")

    # Check rate limit
    if not rate_limiter.is_allowed(user_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Maximum 100 requests per hour."
        )

    try:
        # Encrypt application data before storage
        app_dict = application.model_dump()
        encrypted_app = encrypt_application_data(app_dict)

        logger.info(
            f"Application received from user {user_id}: {application.applicant_id}"
        )

        # Create workflow state
        state = WorkflowState(
            application_id=None,
            application_data=application,
        )

        # Process application
        state = workflow.execute(state)

        # Save to database
        app_repo.save_application(
            state.application_id,
            {
                "applicant_id": application.applicant_id,
                "encrypted_data": encrypted_app,
                "decision": state.decision.model_dump() if state.decision else None,
                "status": state.status.value,
                "user_id": user_id,
            }
        )

        # Audit log
        audit_repo.log_action(
            case_id=state.decision.classification if state.decision else "PENDING",
            applicant_id=application.applicant_id,
            action_type="application_submitted",
            details=f"Application processed by {user_id}",
            actor=user_id
        )

        application_store[state.application_id] = state

        if state.status == Status.FAILED:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Application processing failed",
                    "errors": state.error_log,
                },
            )

        return {
            "application_id": state.application_id,
            "status": state.status.value,
            "applicant_id": application.applicant_id,
            "decision": {
                "classification": state.decision.classification.value if state.decision else None,
                "risk_score": state.decision.risk_score if state.decision else None,
                "confidence_level": state.decision.confidence_level if state.decision else None,
                "explanation": state.decision.explanation if state.decision else None,
                "key_factors": state.decision.key_decision_factors if state.decision else [],
            },
            "processing_time": (
                (state.updated_at - state.created_at).total_seconds()
                if state.updated_at and state.created_at
                else 0
            ),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error processing application: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "message": str(e)},
        )


@app.get("/api/applications/{application_id}")
async def get_application_status(
    application_id: str,
    user_data: Dict[str, Any] = Depends(verify_api_token)
):
    """Get the status and details of a loan application.

    Args:
        application_id: Application ID
        user_data: Authenticated user data

    Returns:
        Application details
    """
    user_id = user_data.get("user_id")

    if application_id not in application_store:
        # Try to load from database
        db_app = app_repo.get_application(application_id)
        if not db_app:
            raise HTTPException(
                status_code=404,
                detail={"error": "Application not found"},
            )
        # Decrypt data for display
        encrypted_data = db_app.get("encrypted_data", {})
        decrypted_data = decrypt_application_data(encrypted_data)

        return {
            "application_id": application_id,
            "applicant_id": db_app.get("applicant_id"),
            "status": db_app.get("status"),
            "decision": db_app.get("decision"),
            "encrypted": True,
            "retrieved_by": user_id,
        }

    state = application_store[application_id]

    return {
        "application_id": application_id,
        "applicant_id": state.application_data.applicant_id,
        "status": state.status.value,
        "applicant_analysis": state.applicant_analysis.model_dump() if state.applicant_analysis else None,
        "risk_analysis": state.risk_analysis.model_dump() if state.risk_analysis else None,
        "decision": state.decision.model_dump() if state.decision else None,
        "compliance": state.compliance.model_dump() if state.compliance else None,
        "error_log": state.error_log,
        "created_at": state.created_at.isoformat(),
        "updated_at": state.updated_at.isoformat(),
        "retrieved_by": user_id,
    }


@app.get("/api/stats")
async def get_stats(user_data: Dict[str, Any] = Depends(verify_api_token)):
    """Get statistics about processed applications.

    Args:
        user_data: Authenticated user data

    Returns:
        Application statistics
    """
    total_applications = len(application_store)
    approved = sum(
        1
        for state in application_store.values()
        if state.decision and state.decision.classification.value == "approve"
    )
    rejected = sum(
        1
        for state in application_store.values()
        if state.decision and state.decision.classification.value == "reject"
    )
    review = sum(
        1
        for state in application_store.values()
        if state.decision and state.decision.classification.value == "review"
    )
    failed = sum(
        1
        for state in application_store.values()
        if state.status == Status.FAILED
    )

    return {
        "total_applications": total_applications,
        "approved": approved,
        "rejected": rejected,
        "review": review,
        "failed": failed,
        "approval_rate": (
            approved / (total_applications - failed) * 100
            if (total_applications - failed) > 0
            else 0
        ),
        "requested_by": user_data.get("user_id"),
    }


@app.get("/api/audit/logs")
async def get_audit_logs(user_data: Dict[str, Any] = Depends(verify_api_token)):
    """Get audit logs (admin only).

    Args:
        user_data: Authenticated user data

    Returns:
        Audit logs
    """
    # In production, check if user is admin
    logs = audit_repo.get_all_logs()
    return {
        "total_logs": len(logs),
        "logs": logs[-50:],  # Return last 50 logs
        "requested_by": user_data.get("user_id"),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
