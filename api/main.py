"""FastAPI application for loan application microservice."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
from schemas.loan_application import LoanApplication
from schemas.common import Status
from orchestration.workflow import LoanAnalysisWorkflow
from orchestration.state import WorkflowState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Loan Application Analysis API",
    description="Multi-agent loan application analysis service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

application_store = {}
workflow = LoanAnalysisWorkflow()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Loan Application Analysis API",
    }


@app.post("/api/applications")
async def submit_application(application: LoanApplication):
    """Submit a new loan application for analysis."""
    try:
        state = WorkflowState(
            application_id=None,
            application_data=application,
        )

        logger.info(f"Processing application for {application.applicant_id}")
        state = workflow.execute(state)

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
async def get_application_status(application_id: str):
    """Get the status and details of a loan application."""
    if application_id not in application_store:
        raise HTTPException(
            status_code=404,
            detail={"error": "Application not found"},
        )

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
    }


@app.get("/api/applications/{application_id}/history")
async def get_application_history(application_id: str):
    """Get the complete history and audit trail of an application."""
    if application_id not in application_store:
        raise HTTPException(
            status_code=404,
            detail={"error": "Application not found"},
        )

    state = application_store[application_id]

    history = {
        "application_id": application_id,
        "applicant_id": state.application_data.applicant_id,
        "timeline": [
            {
                "step": "Application Submitted",
                "timestamp": state.created_at.isoformat(),
                "status": "completed",
            },
        ],
        "analyses": {
            "applicant_profile": state.applicant_analysis.model_dump() if state.applicant_analysis else None,
            "financial_risk": state.risk_analysis.model_dump() if state.risk_analysis else None,
            "loan_decision": state.decision.model_dump() if state.decision else None,
        },
        "final_outcome": {
            "classification": state.decision.classification.value if state.decision else None,
            "risk_score": state.decision.risk_score if state.decision else None,
            "explanation": state.decision.explanation if state.decision else None,
        },
        "compliance": state.compliance.model_dump() if state.compliance else None,
        "errors": state.error_log,
        "processing_complete": state.status == Status.COMPLETED,
    }

    return history


@app.get("/api/stats")
async def get_stats():
    """Get statistics about processed applications."""
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
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
