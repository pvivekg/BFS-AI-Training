"""Unit tests for data schemas and validation."""

import pytest
from pydantic import ValidationError
from schemas.loan_application import LoanApplication
from schemas.agent_responses import (
    ApplicantProfileResponse,
    RiskAnalysisResponse,
    LoanDecisionResponse,
    ComplianceResponse,
)
from schemas.common import EmploymentType, Location, RiskLevel, Decision


class TestLoanApplicationSchema:
    """Test LoanApplication model validation."""

    def test_valid_application(self):
        """Test creating a valid application."""
        app = LoanApplication(
            applicant_id="APP001",
            age=35,
            income=75000,
            employment_type="employed",
            credit_score=720,
            loan_amount=250000,
            tenure=20,
            existing_liabilities=50000,
            location="New York"
        )
        assert app.applicant_id == "APP001"
        assert app.age == 35
        assert app.credit_score == 720

    def test_invalid_age_too_low(self):
        """Test that age < 18 is rejected."""
        with pytest.raises(ValidationError):
            LoanApplication(
                applicant_id="APP001",
                age=15,
                income=75000,
                employment_type="employed",
                credit_score=720,
                loan_amount=250000,
                tenure=20,
                existing_liabilities=50000,
                location="New York"
            )

    def test_invalid_age_too_high(self):
        """Test that age > 100 is rejected."""
        with pytest.raises(ValidationError):
            LoanApplication(
                applicant_id="APP001",
                age=150,
                income=75000,
                employment_type="employed",
                credit_score=720,
                loan_amount=250000,
                tenure=20,
                existing_liabilities=50000,
                location="New York"
            )

    def test_invalid_credit_score_too_low(self):
        """Test that credit score < 300 is rejected."""
        with pytest.raises(ValidationError):
            LoanApplication(
                applicant_id="APP001",
                age=35,
                income=75000,
                employment_type="employed",
                credit_score=250,
                loan_amount=250000,
                tenure=20,
                existing_liabilities=50000,
                location="New York"
            )

    def test_invalid_credit_score_too_high(self):
        """Test that credit score > 850 is rejected."""
        with pytest.raises(ValidationError):
            LoanApplication(
                applicant_id="APP001",
                age=35,
                income=75000,
                employment_type="employed",
                credit_score=900,
                loan_amount=250000,
                tenure=20,
                existing_liabilities=50000,
                location="New York"
            )

    def test_invalid_negative_income(self):
        """Test that negative income is rejected."""
        with pytest.raises(ValidationError):
            LoanApplication(
                applicant_id="APP001",
                age=35,
                income=-75000,
                employment_type="employed",
                credit_score=720,
                loan_amount=250000,
                tenure=20,
                existing_liabilities=50000,
                location="New York"
            )

    def test_invalid_negative_loan_amount(self):
        """Test that negative loan amount is rejected."""
        with pytest.raises(ValidationError):
            LoanApplication(
                applicant_id="APP001",
                age=35,
                income=75000,
                employment_type="employed",
                credit_score=720,
                loan_amount=-250000,
                tenure=20,
                existing_liabilities=50000,
                location="New York"
            )

    def test_invalid_zero_tenure(self):
        """Test that zero tenure is rejected."""
        with pytest.raises(ValidationError):
            LoanApplication(
                applicant_id="APP001",
                age=35,
                income=75000,
                employment_type="employed",
                credit_score=720,
                loan_amount=250000,
                tenure=0,
                existing_liabilities=50000,
                location="New York"
            )

    def test_tenure_boundary(self):
        """Test tenure boundaries (1-30 years)."""
        # Valid: 1 year
        app = LoanApplication(
            applicant_id="APP001",
            age=35,
            income=75000,
            employment_type="employed",
            credit_score=720,
            loan_amount=250000,
            tenure=1,
            existing_liabilities=50000,
            location="New York"
        )
        assert app.tenure == 1

        # Valid: 30 years
        app = LoanApplication(
            applicant_id="APP001",
            age=35,
            income=75000,
            employment_type="employed",
            credit_score=720,
            loan_amount=250000,
            tenure=30,
            existing_liabilities=50000,
            location="New York"
        )
        assert app.tenure == 30

    def test_employment_type_enum(self):
        """Test employment type enum values."""
        for emp_type in ["employed", "self_employed", "unemployed", "retired"]:
            app = LoanApplication(
                applicant_id="APP001",
                age=35,
                income=75000,
                employment_type=emp_type,
                credit_score=720,
                loan_amount=250000,
                tenure=20,
                existing_liabilities=50000,
                location="New York"
            )
            assert app.employment_type == emp_type

    def test_location_enum(self):
        """Test location enum values."""
        for location in ["New York", "California", "Texas", "Florida"]:
            app = LoanApplication(
                applicant_id="APP001",
                age=35,
                income=75000,
                employment_type="employed",
                credit_score=720,
                loan_amount=250000,
                tenure=20,
                existing_liabilities=50000,
                location=location
            )
            assert app.location == location

    def test_timestamp_auto_generated(self):
        """Test that timestamp is auto-generated."""
        app = LoanApplication(
            applicant_id="APP001",
            age=35,
            income=75000,
            employment_type="employed",
            credit_score=720,
            loan_amount=250000,
            tenure=20,
            existing_liabilities=50000,
            location="New York"
        )
        assert app.application_timestamp is not None


class TestAgentResponses:
    """Test agent response schemas."""

    def test_applicant_profile_response(self):
        """Test ApplicantProfileResponse creation."""
        response = ApplicantProfileResponse(
            applicant_id="APP001",
            income_stability_score=85,
            employment_risk="low",
            credit_history_summary="Good payment history",
            application_completeness_flags=[]
        )
        assert response.income_stability_score == 85
        assert response.employment_risk == "low"

    def test_risk_analysis_response(self):
        """Test RiskAnalysisResponse creation."""
        response = RiskAnalysisResponse(
            applicant_id="APP001",
            debt_to_income_ratio=0.667,
            credit_score_risk_level="medium",
            loan_amount_risk="medium",
            anomaly_detection_flags=[],
            reasoning="DTI indicates good debt management"
        )
        assert response.debt_to_income_ratio == 0.667
        assert response.credit_score_risk_level == "medium"

    def test_loan_decision_response(self):
        """Test LoanDecisionResponse creation."""
        response = LoanDecisionResponse(
            applicant_id="APP001",
            classification="approve",
            risk_score=25.5,
            confidence_level=0.95,
            key_decision_factors=["Good income", "Strong credit"],
            explanation="Application approved"
        )
        assert response.classification == "approve"
        assert response.risk_score == 25.5
        assert response.confidence_level == 0.95

    def test_compliance_response(self):
        """Test ComplianceResponse creation."""
        response = ComplianceResponse(
            applicant_id="APP001",
            case_id="CASE_ABC123",
            action_taken="APPROVE",
            notification_sent=True,
            summary="Application processed"
        )
        assert response.case_id == "CASE_ABC123"
        assert response.notification_sent is True


class TestEnums:
    """Test enum definitions."""

    def test_employment_type_values(self):
        """Test all EmploymentType values."""
        assert EmploymentType.EMPLOYED.value == "employed"
        assert EmploymentType.SELF_EMPLOYED.value == "self_employed"
        assert EmploymentType.UNEMPLOYED.value == "unemployed"
        assert EmploymentType.RETIRED.value == "retired"

    def test_risk_level_values(self):
        """Test all RiskLevel values."""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.VERY_HIGH.value == "very_high"

    def test_decision_values(self):
        """Test all Decision values."""
        assert Decision.APPROVE.value == "approve"
        assert Decision.REJECT.value == "reject"
        assert Decision.REVIEW.value == "review"
