"""Workflow state definitions."""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from schemas.loan_application import LoanApplication
from schemas.agent_responses import (
    ApplicantProfileResponse,
    RiskAnalysisResponse,
    LoanDecisionResponse,
    ComplianceResponse,
)
from schemas.common import Status


@dataclass
class WorkflowState:
    """Complete workflow state for loan application processing."""

    application_id: str
    application_data: LoanApplication
    applicant_analysis: Optional[ApplicantProfileResponse] = None
    risk_analysis: Optional[RiskAnalysisResponse] = None
    decision: Optional[LoanDecisionResponse] = None
    compliance: Optional[ComplianceResponse] = None
    status: Status = Status.PENDING
    error_log: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "application_id": self.application_id,
            "application_data": self.application_data.model_dump(),
            "applicant_analysis": self.applicant_analysis.model_dump() if self.applicant_analysis else None,
            "risk_analysis": self.risk_analysis.model_dump() if self.risk_analysis else None,
            "decision": self.decision.model_dump() if self.decision else None,
            "compliance": self.compliance.model_dump() if self.compliance else None,
            "status": self.status.value,
            "error_log": self.error_log,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowState":
        """Create state from dictionary."""
        state = cls(
            application_id=data.get("application_id"),
            application_data=LoanApplication(**data.get("application_data", {})),
            status=Status(data.get("status", Status.PENDING.value)),
            error_log=data.get("error_log", []),
        )

        if data.get("applicant_analysis"):
            state.applicant_analysis = ApplicantProfileResponse(**data["applicant_analysis"])
        if data.get("risk_analysis"):
            state.risk_analysis = RiskAnalysisResponse(**data["risk_analysis"])
        if data.get("decision"):
            state.decision = LoanDecisionResponse(**data["decision"])
        if data.get("compliance"):
            state.compliance = ComplianceResponse(**data["compliance"])

        return state
