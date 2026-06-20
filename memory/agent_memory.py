import os
import json
import logging
import datetime

logger = logging.getLogger("pharma_agent.memory")

class AgentMemory:
    """Handles local storage of search history and agent interactions."""

    def __init__(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        memory_file = os.getenv("MEMORY_FILE", "memory/chat_memory.json")
        if not os.path.isabs(memory_file):
            self.memory_file = os.path.join(project_root, memory_file)
        else:
            self.memory_file = memory_file
        self.history = []
        self.load_memory()

    def load_memory(self):
        """Loads search history from JSON file."""
        if not os.path.exists(self.memory_file):
            logger.info("Memory file does not exist. Initializing empty history.")
            self.history = []
            return

        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.history = data.get("history", [])
                logger.info(f"Successfully loaded {len(self.history)} history entries from memory.")
        except Exception as e:
            logger.error(f"Failed to load memory file: {e}. Starting with empty history.")
            self.history = []

    def save_memory(self):
        """Saves search history to JSON file."""
        # Ensure parent folder exists
        parent_dir = os.path.dirname(self.memory_file)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump({"history": self.history}, f, indent=2)
            logger.info("Memory successfully saved.")
        except Exception as e:
            logger.error(f"Failed to save memory file: {e}")

    def add_query(self, query_type: str, search_term: str):
        """Adds a new query record to history.

        Args:
            query_type (str): Type of search (e.g., "FDA Lookup", "PubChem Lookup", "Report Generation").
            search_term (str): The search term entered by the user.
        """
        entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": query_type,
            "term": search_term
        }
        self.history.append(entry)
        # Keep history to last 100 queries
        if len(self.history) > 100:
            self.history.pop(0)
        self.save_memory()

    def get_history(self) -> list:
        """Returns the search history list."""
        return self.history

    def clear_memory(self):
        """Clears the saved history."""
        self.history = []
        self.save_memory()
        logger.info("Memory history cleared.")
