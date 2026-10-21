from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from schemas.common import EmploymentType, Location


class LoanApplication(BaseModel):
    applicant_id: str = Field(..., description="Unique applicant identifier")
    age: int = Field(..., ge=18, le=100, description="Applicant age")
    income: float = Field(..., gt=0, description="Annual income")
    employment_type: EmploymentType = Field(..., description="Employment type")
    credit_score: int = Field(..., ge=300, le=850, description="Credit score")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    tenure: int = Field(..., gt=0, le=30, description="Loan tenure in years")
    existing_liabilities: float = Field(..., ge=0, description="Existing liabilities")
    location: Location = Field(..., description="Applicant location")
    application_timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


class LoanRequest(BaseModel):
    application: LoanApplication
