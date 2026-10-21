"""LangGraph orchestration workflow for loan application processing."""

import uuid
from datetime import datetime
from typing import Dict, Any
from schemas.common import Status
from orchestration.state import WorkflowState
from agents.applicant_profile_agent import ApplicantProfileAgent
from agents.financial_risk_agent import FinancialRiskAgent
from agents.loan_decision_agent import LoanDecisionAgent
from agents.compliance_orchestrator_agent import ComplianceOrchestratorAgent


class LoanAnalysisWorkflow:
    """Orchestrates the multi-agent loan analysis workflow."""

    def __init__(self):
        self.applicant_agent = ApplicantProfileAgent()
        self.risk_agent = FinancialRiskAgent()
        self.decision_agent = LoanDecisionAgent()
        self.compliance_agent = ComplianceOrchestratorAgent()

    def validate_input(self, state: WorkflowState) -> WorkflowState:
        """Validate loan application input."""
        state.status = Status.PROCESSING
        state.updated_at = datetime.utcnow()

        if not state.application_data.applicant_id:
            state.error_log.append("Missing applicant ID")
            state.status = Status.FAILED
            return state

        if state.application_data.income <= 0:
            state.error_log.append("Invalid income")
            state.status = Status.FAILED
            return state

        if state.application_data.credit_score < 300 or state.application_data.credit_score > 850:
            state.error_log.append("Invalid credit score")
            state.status = Status.FAILED
            return state

        return state

    def analyze_applicant(self, state: WorkflowState) -> WorkflowState:
        """Analyze applicant profile."""
        try:
            state.applicant_analysis = self.applicant_agent.analyze(
                state.application_data
            )
        except Exception as e:
            state.error_log.append(f"Applicant analysis error: {str(e)}")
            state.status = Status.FAILED
        finally:
            state.updated_at = datetime.utcnow()

        return state

    def analyze_financial_risk(self, state: WorkflowState) -> WorkflowState:
        """Analyze financial risk."""
        try:
            state.risk_analysis = self.risk_agent.analyze(
                state.application_data
            )
        except Exception as e:
            state.error_log.append(f"Financial risk analysis error: {str(e)}")
            state.status = Status.FAILED
        finally:
            state.updated_at = datetime.utcnow()

        return state

    def synthesize_decision(self, state: WorkflowState) -> WorkflowState:
        """Synthesize loan decision."""
        try:
            if not state.applicant_analysis or not state.risk_analysis:
                raise ValueError("Missing applicant or risk analysis")

            state.decision = self.decision_agent.decide(
                state.application_data,
                state.applicant_analysis,
                state.risk_analysis,
            )
        except Exception as e:
            state.error_log.append(f"Decision synthesis error: {str(e)}")
            state.status = Status.FAILED
        finally:
            state.updated_at = datetime.utcnow()

        return state

    def execute_compliance(self, state: WorkflowState) -> WorkflowState:
        """Execute decision and create compliance record."""
        try:
            if not state.decision:
                raise ValueError("Missing loan decision")

            state.compliance = self.compliance_agent.execute(
                state.application_data,
                state.decision,
            )
        except Exception as e:
            state.error_log.append(f"Compliance execution error: {str(e)}")
            state.status = Status.FAILED
        finally:
            state.updated_at = datetime.utcnow()

        return state

    def finalize(self, state: WorkflowState) -> WorkflowState:
        """Finalize workflow and set status."""
        if state.status != Status.FAILED:
            state.status = Status.COMPLETED

        state.updated_at = datetime.utcnow()
        return state

    def cleanup(self) -> None:
        """Clean up agent resources."""
        self.applicant_agent.cleanup()
        self.risk_agent.cleanup()
        self.decision_agent.cleanup()
        self.compliance_agent.cleanup()

    def execute(self, state: WorkflowState) -> WorkflowState:
        """Execute complete workflow."""
        state.application_id = state.application_id or str(uuid.uuid4())

        state = self.validate_input(state)
        if state.status == Status.FAILED:
            return self.finalize(state)

        state = self.analyze_applicant(state)
        if state.status == Status.FAILED:
            return self.finalize(state)

        state = self.analyze_financial_risk(state)
        if state.status == Status.FAILED:
            return self.finalize(state)

        state = self.synthesize_decision(state)
        if state.status == Status.FAILED:
            return self.finalize(state)

        state = self.execute_compliance(state)
        if state.status == Status.FAILED:
            return self.finalize(state)

        return self.finalize(state)
