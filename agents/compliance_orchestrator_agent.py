"""Compliance & Action Orchestrator Agent - Executes decision and creates audit trail."""

import json
import subprocess
from typing import Dict, Any
from agents.base_agent import BaseAgent
from schemas.agent_responses import ComplianceResponse, LoanDecisionResponse
from schemas.loan_application import LoanApplication


class ComplianceOrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("ComplianceOrchestratorAgent")
        self.mcp_process = None

    def start_mcp_server(self) -> None:
        """Start the NotificationSystem MCP server."""
        try:
            self.mcp_process = subprocess.Popen(
                ["python", "mcp_servers/notification_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            print(f"Error starting MCP server: {e}")

    def call_mcp_tool(self, tool_name: str, **kwargs) -> str:
        """Directly call MCP server tool (mock implementation for now)."""
        from mcp_servers.notification_server import (
            create_case,
            send_notification,
            log_action,
            execute_decision,
            get_case_details,
            generate_compliance_report,
        )

        if tool_name == "create_case":
            return json.dumps(
                create_case(kwargs.get("applicant_id"), kwargs.get("decision"))
            )
        elif tool_name == "send_notification":
            return json.dumps(
                send_notification(
                    kwargs.get("applicant_id"),
                    kwargs.get("decision"),
                    kwargs.get("case_id"),
                )
            )
        elif tool_name == "log_action":
            return json.dumps(
                log_action(
                    kwargs.get("case_id"),
                    kwargs.get("applicant_id"),
                    kwargs.get("action_type"),
                    kwargs.get("details"),
                    kwargs.get("actor", "system"),
                )
            )
        elif tool_name == "execute_decision":
            return json.dumps(
                execute_decision(
                    kwargs.get("applicant_id"),
                    kwargs.get("case_id"),
                    kwargs.get("classification"),
                    kwargs.get("risk_score"),
                    kwargs.get("explanation"),
                )
            )
        elif tool_name == "get_case_details":
            return json.dumps(get_case_details(kwargs.get("case_id")))
        elif tool_name == "generate_compliance_report":
            return generate_compliance_report(
                kwargs.get("applicant_id"),
                kwargs.get("case_id"),
                kwargs.get("classification"),
            )
        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

    def execute(
        self,
        application: LoanApplication,
        decision: LoanDecisionResponse,
    ) -> ComplianceResponse:
        """Execute decision and create audit trail."""

        prompt = f"""Execute the loan decision and create audit trail:

Applicant ID: {application.applicant_id}
Decision: {decision.classification.upper()}
Risk Score: {decision.risk_score}
Confidence Level: {decision.confidence_level}

Explanation: {decision.explanation}

Please use the following tools to execute the decision:
1. create_case - to create a case record
2. execute_decision - to execute the decision
3. send_notification - to notify the applicant
4. log_action - to log the execution
5. generate_compliance_report - to create audit trail

Provide a summary of actions taken."""

        tools = [
            {
                "name": "create_case",
                "description": "Create a case record for the application",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "applicant_id": {
                            "type": "string",
                            "description": "Applicant ID",
                        },
                        "decision": {
                            "type": "string",
                            "description": "Decision type",
                        },
                    },
                    "required": ["applicant_id", "decision"],
                },
            },
            {
                "name": "send_notification",
                "description": "Send notification to applicant",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "applicant_id": {
                            "type": "string",
                            "description": "Applicant ID",
                        },
                        "decision": {
                            "type": "string",
                            "description": "Decision type",
                        },
                        "case_id": {
                            "type": "string",
                            "description": "Case ID",
                        },
                    },
                    "required": ["applicant_id", "decision", "case_id"],
                },
            },
            {
                "name": "log_action",
                "description": "Log action in audit trail",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "case_id": {
                            "type": "string",
                            "description": "Case ID",
                        },
                        "applicant_id": {
                            "type": "string",
                            "description": "Applicant ID",
                        },
                        "action_type": {
                            "type": "string",
                            "description": "Type of action",
                        },
                        "details": {
                            "type": "string",
                            "description": "Action details",
                        },
                    },
                    "required": ["case_id", "applicant_id", "action_type", "details"],
                },
            },
            {
                "name": "execute_decision",
                "description": "Execute the decision",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "applicant_id": {
                            "type": "string",
                            "description": "Applicant ID",
                        },
                        "case_id": {
                            "type": "string",
                            "description": "Case ID",
                        },
                        "classification": {
                            "type": "string",
                            "description": "Decision classification",
                        },
                        "risk_score": {
                            "type": "number",
                            "description": "Risk score",
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Decision explanation",
                        },
                    },
                    "required": [
                        "applicant_id",
                        "case_id",
                        "classification",
                        "risk_score",
                        "explanation",
                    ],
                },
            },
        ]

        response = self.think(prompt, tools)

        for tool_call in response.get("tool_calls", []):
            tool_result = self.call_mcp_tool(
                tool_call["name"], **tool_call.get("input", {})
            )
            self.add_tool_result(tool_call["id"], tool_call["name"], tool_result)

        if response.get("tool_calls"):
            final_response = self.think(
                "Based on the executed actions, provide the final compliance summary."
            )

        compliance_result = self.call_mcp_tool(
            "generate_compliance_report",
            applicant_id=application.applicant_id,
            case_id=f"CASE_{application.applicant_id}",
            classification=decision.classification,
        )
        return ComplianceResponse(**json.loads(compliance_result))

    def cleanup(self) -> None:
        """Stop MCP server."""
        if self.mcp_process:
            self.mcp_process.terminate()
