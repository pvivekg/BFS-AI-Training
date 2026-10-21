"""Applicant Profile Agent - Analyzes applicant background and employment."""

import json
import subprocess
from typing import Dict, Any
from agents.base_agent import BaseAgent
from schemas.agent_responses import ApplicantProfileResponse
from schemas.loan_application import LoanApplication


class ApplicantProfileAgent(BaseAgent):
    def __init__(self):
        super().__init__("ApplicantProfileAgent")
        self.mcp_process = None

    def start_mcp_server(self) -> None:
        """Start the ApplicantDB MCP server."""
        try:
            self.mcp_process = subprocess.Popen(
                ["python", "mcp_servers/applicant_db_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            print(f"Error starting MCP server: {e}")

    def call_mcp_tool(self, tool_name: str, **kwargs) -> str:
        """Directly call MCP server tool (mock implementation for now)."""
        # For MVP, we'll use direct imports instead of actual MCP calls
        from mcp_servers.applicant_db_server import (
            get_applicant_profile,
            get_employment_history,
            get_credit_history,
            generate_applicant_analysis,
        )

        if tool_name == "get_applicant_profile":
            return json.dumps(get_applicant_profile(kwargs.get("applicant_id")))
        elif tool_name == "get_employment_history":
            return json.dumps(get_employment_history(kwargs.get("applicant_id")))
        elif tool_name == "get_credit_history":
            return json.dumps(get_credit_history(kwargs.get("applicant_id")))
        elif tool_name == "generate_applicant_analysis":
            return generate_applicant_analysis(kwargs.get("applicant_id"))
        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

    def analyze(self, application: LoanApplication) -> ApplicantProfileResponse:
        """Analyze applicant profile."""

        prompt = f"""Analyze the following loan application applicant profile:

Applicant ID: {application.applicant_id}
Age: {application.age}
Income: ${application.income}
Employment Type: {application.employment_type}
Location: {application.location}

Please use the following tools to gather information:
1. get_applicant_profile - to get basic profile info
2. get_employment_history - to assess employment stability
3. get_credit_history - to review credit history
4. generate_applicant_analysis - to create comprehensive analysis

After gathering the data, provide a structured analysis of the applicant's profile."""

        tools = [
            {
                "name": "get_applicant_profile",
                "description": "Retrieve applicant profile information",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "applicant_id": {
                            "type": "string",
                            "description": "Applicant ID",
                        }
                    },
                    "required": ["applicant_id"],
                },
            },
            {
                "name": "get_employment_history",
                "description": "Retrieve employment history and stability assessment",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "applicant_id": {
                            "type": "string",
                            "description": "Applicant ID",
                        }
                    },
                    "required": ["applicant_id"],
                },
            },
            {
                "name": "get_credit_history",
                "description": "Retrieve credit history information",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "applicant_id": {
                            "type": "string",
                            "description": "Applicant ID",
                        }
                    },
                    "required": ["applicant_id"],
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
            final_response = self.think("Based on the gathered data, summarize the applicant analysis.")

        if response.get("final_answer"):
            try:
                result_data = json.loads(response["final_answer"])
                if isinstance(result_data, dict):
                    return ApplicantProfileResponse(**result_data)
            except:
                pass

        analysis_result = self.call_mcp_tool(
            "generate_applicant_analysis",
            applicant_id=application.applicant_id,
        )
        return ApplicantProfileResponse(**json.loads(analysis_result))

    def cleanup(self) -> None:
        """Stop MCP server."""
        if self.mcp_process:
            self.mcp_process.terminate()
