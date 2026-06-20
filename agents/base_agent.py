import logging
from abc import ABC, abstractmethod
from tools.base_tool import BaseTool

class BaseAgent(ABC):
    """Abstract Base Class for Agents."""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.tools = {}
        self.logger = logging.getLogger(f"pharma_agent.agents.{self.name.lower().replace(' ', '_')}")

    def register_tool(self, tool: BaseTool):
        """Registers a tool that the agent can use."""
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: '{tool.name}' to agent '{self.name}'.")

    def execute_tool(self, tool_name: str, query: str) -> dict:
        """Executes a registered tool by its name with a query."""
        if tool_name not in self.tools:
            self.logger.error(f"Tool '{tool_name}' is not registered with agent '{self.name}'.")
            raise ValueError(f"Tool '{tool_name}' not available.")
        
        self.logger.info(f"Agent '{self.name}' executing tool '{tool_name}' with query: '{query}'...")
        return self.tools[tool_name].run(query)

    @abstractmethod
    def run(self, query: str) -> dict:
        """Core reasoning and execution loop of the agent.

        Args:
            query (str): The task or question presented to the agent.

        Returns:
            dict: The agent's final answer/synthesis.
        """
        pass
