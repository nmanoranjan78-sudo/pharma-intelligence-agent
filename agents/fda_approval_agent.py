"""
FDA Approval Agent

This is a beginner-friendly agent that searches the openFDA API for drug label information,
saves the results to a CSV file, and returns a summary.
"""

import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import logging
from agents.base_agent import BaseAgent
from tools.fda_tool import fetch_and_save_fda_labels

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("pharma_agent.agents.fda_approval_agent")


class FDAApprovalAgent(BaseAgent):
    """
    A simple FDA Approval Agent that uses tools/fda_tool.py
    to retrieve FDA drug label data for a given drug name.
    """

    def __init__(self):
        super().__init__(
            name="FDA Approval Agent",
            role="Specialist in retrieving and summarizing FDA drug label data."
        )

    def run(self, drug: str) -> dict:
        """
        Runs the FDA tool for the specified drug, saves results to data/fda_results.csv,
        and returns a summary dictionary containing:
        - drug searched
        - total records found
        - top brand name
        - top manufacturer
        - CSV output path
        """
        clean_drug = drug.strip().lower()
        logger.info(f"FDAApprovalAgent: Querying FDA labels for drug '{clean_drug}'...")

        # 1. Call the openFDA API search function from fda_tool
        # This function fetches label data and saves it to data/fda_results.csv
        fetch_and_save_fda_labels(clean_drug)

        csv_path = os.path.join("data", "fda_results.csv")

        # Initialize default summary values
        records_found = 0
        top_brand = "N/A"
        top_manufacturer = "N/A"

        # 2. Read the results from the saved CSV file to extract the summary
        if os.path.exists(csv_path):
            try:
                with open(csv_path, mode="r", encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    # Filter rows where 'drug_name' matches the searched drug query
                    matching_rows = [row for row in reader if row.get("drug_name", "").lower() == clean_drug]

                    records_found = len(matching_rows)
                    if records_found > 0:
                        top_brand = matching_rows[0].get("brand_name", "Unknown Brand")
                        top_manufacturer = matching_rows[0].get("manufacturer", "Unknown Manufacturer")
            except Exception as e:
                logger.error(f"Error reading FDA results CSV file: {e}")

        # 3. Build and return the simple summary dictionary
        summary = {
            "drug_searched": clean_drug,
            "total_records_found": records_found,
            "top_brand_name": top_brand,
            "top_manufacturer": top_manufacturer,
            "csv_output_path": csv_path
        }

        return summary


if __name__ == "__main__":
    # Check if a custom drug name is passed as command-line argument,
    # otherwise default to 'semaglutide'
    drug_query = "semaglutide"
    if len(sys.argv) > 1:
        drug_query = " ".join(sys.argv[1:])

    # Instantiate the agent and run the query
    agent = FDAApprovalAgent()
    results_summary = agent.run(drug_query)

    # Print a clean, friendly summary output
    print("\n" + "=" * 60)
    print(" FDA APPROVAL AGENT SUMMARY REPORT")
    print("=" * 60)
    print(f"Drug Searched:       {results_summary['drug_searched']}")
    print(f"Total Records Found: {results_summary['total_records_found']}")
    print(f"Top Brand Name:      {results_summary['top_brand_name']}")
    print(f"Top Manufacturer:    {results_summary['top_manufacturer']}")
    print(f"CSV Output Path:     {results_summary['csv_output_path']}")
    print("=" * 60 + "\n")
