"""
Clinical Trial Agent

This is a beginner-friendly agent that searches ClinicalTrials.gov for trials 
related to a disease query and saves the results to a CSV file. It outputs 
a summary of the results found.
"""

import os
import sys

# Add the project root to sys.path so Python can find 'agents' and 'tools' packages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import logging
from agents.base_agent import BaseAgent
from tools.clinicaltrials_tool import fetch_and_save_trials

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("pharma_agent.agents.clinical_trial_agent")


class ClinicalTrialAgent(BaseAgent):
    """
    A simple Clinical Trial Agent that uses tools/clinicaltrials_tool.py 
    to retrieve clinical trial data for a given disease name.
    """

    def __init__(self):
        super().__init__(
            name="Clinical Trial Agent",
            role="Specialist in retrieving and summarizing clinical trial data."
        )

    def run(self, disease: str) -> dict:
        """
        Runs the ClinicalTrials tool for the specified disease, saves results to data/trials.csv,
        and returns a summary dictionary containing:
        - disease searched
        - total records found
        - top study title
        - top sponsor
        - CSV output path
        """
        clean_disease = disease.strip().lower()
        logger.info(f"ClinicalTrialAgent: Querying clinical trials for disease '{clean_disease}'...")

        # 1. Call the ClinicalTrials tool function
        # This function fetches trial data and saves it to data/trials.csv
        fetch_and_save_trials(clean_disease)

        csv_path = os.path.join("data", "trials.csv")
        
        # Initialize default summary values in case no trials are found
        records_found = 0
        top_title = "N/A"
        top_sponsor = "N/A"

        # 2. Read the results from the saved CSV file to extract the summary
        if os.path.exists(csv_path):
            try:
                with open(csv_path, mode="r", encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    # Filter rows where 'disease' matches the searched disease query
                    # (The tool writes the cleaned disease name to the 'disease' column)
                    matching_rows = [row for row in reader if row.get("disease", "").lower() == clean_disease]
                    
                    records_found = len(matching_rows)
                    if records_found > 0:
                        top_title = matching_rows[0].get("study_title", "Unknown Title")
                        top_sponsor = matching_rows[0].get("sponsor", "Unknown Sponsor")
            except Exception as e:
                logger.error(f"Error reading trials CSV file: {e}")

        # 3. Build and return the simple summary dictionary
        summary = {
            "disease_searched": clean_disease,
            "total_records_found": records_found,
            "top_study_title": top_title,
            "top_sponsor": top_sponsor,
            "csv_output_path": csv_path
        }
        
        return summary


if __name__ == "__main__":
    # Check if a custom disease name is passed as command-line argument,
    # otherwise default to 'diabetes'
    disease_query = "diabetes"
    if len(sys.argv) > 1:
        disease_query = " ".join(sys.argv[1:])

    # Instantiate the agent and run the query
    agent = ClinicalTrialAgent()
    results_summary = agent.run(disease_query)
    
    # Print a clean, friendly summary output
    print("\n" + "=" * 60)
    print(" CLINICAL TRIAL AGENT SUMMARY REPORT")
    print("=" * 60)
    print(f"Disease Searched:   {results_summary['disease_searched']}")
    print(f"Total Records Found: {results_summary['total_records_found']}")
    print(f"Top Study Title:     {results_summary['top_study_title']}")
    print(f"Top Sponsor:         {results_summary['top_sponsor']}")
    print(f"CSV Output Path:     {results_summary['csv_output_path']}")
    print("=" * 60 + "\n")
