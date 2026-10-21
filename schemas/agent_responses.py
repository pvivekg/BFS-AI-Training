from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from schemas.common import RiskLevel, Decision


class ApplicantProfileResponse(BaseModel):
    applicant_id: str
    income_stability_score: float = Field(ge=0, le=100, description="Score 0-100")
    employment_risk: RiskLevel
    credit_history_summary: str
    application_completeness_flags: List[str] = Field(default_factory=list)
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


class RiskAnalysisResponse(BaseModel):
    applicant_id: str
    debt_to_income_ratio: float = Field(ge=0, description="DTI ratio")
    credit_score_risk_level: RiskLevel
    loan_amount_risk: RiskLevel
    anomaly_detection_flags: List[str] = Field(default_factory=list)
    reasoning: str
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


class LoanDecisionResponse(BaseModel):
    applicant_id: str
    classification: Decision
    risk_score: float = Field(ge=0, le=100, description="Overall risk score 0-100")
    confidence_level: float = Field(ge=0, le=1, description="Confidence 0-1")
    key_decision_factors: List[str]
    explanation: str
    decision_timestamp: datetime = Field(default_factory=datetime.utcnow)


class ComplianceResponse(BaseModel):
    applicant_id: str
    case_id: str
    action_taken: str
    notification_sent: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    summary: str
