from abc import ABC, abstractmethod

class BaseTool(ABC):
    """Abstract base class for all Agent tools."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def run(self, query: str) -> dict:
        """Execute the tool's core logic with the given query.

        Args:
            query (str): The search query or input parameters for the tool.

        Returns:
            dict: The tool's output structured as a dictionary.
        """
        pass
