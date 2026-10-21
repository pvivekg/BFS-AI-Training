"""Base agent class with common functionality."""

import json
from typing import Any, Dict
from anthropic import Anthropic


class BaseAgent:
    def __init__(self, agent_name: str, model: str = "claude-sonnet-4-20250514"):
        self.agent_name = agent_name
        self.model = model
        self.client = Anthropic()
        self.messages = []

    def add_tool_result(
        self, tool_use_id: str, tool_name: str, content: str
    ) -> None:
        """Add tool result to message history."""
        self.messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": content,
                    }
                ],
            }
        )

    def process_response(self, response: Any) -> Dict[str, Any]:
        """Process Claude response and extract tool calls or final answer."""
        result = {
            "tool_calls": [],
            "final_answer": None,
            "stop_reason": response.stop_reason,
        }

        for block in response.content:
            if block.type == "text":
                result["final_answer"] = block.text
            elif block.type == "tool_use":
                result["tool_calls"].append(
                    {
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    }
                )

        return result

    def think(self, prompt: str, tools: list = None) -> Dict[str, Any]:
        """Send a message to Claude and get response."""
        self.messages.append({"role": "user", "content": prompt})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            tools=tools or [],
            messages=self.messages,
        )

        if response.content:
            self.messages.append({"role": "assistant", "content": response.content})

        return self.process_response(response)
