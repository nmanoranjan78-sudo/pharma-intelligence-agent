"""
Planner Agent

This agent acts as a coordinator/orchestrator. It:
1. Orchestrates the search for clinical trials for a specific disease by calling ClinicalTrialAgent.
2. Orchestrates the search for FDA approvals for a specific drug by calling FDAApprovalAgent.
3. Triggers the generation of a synthesized markdown briefing report using the report generator.
"""

import os
import sys
import logging

# Ensure project root is in the system path so Python can find tools and agents packages
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.base_agent import BaseAgent
from agents.clinical_trial_agent import ClinicalTrialAgent
from agents.fda_approval_agent import FDAApprovalAgent
from agents.evaluator_agent import EvaluatorAgent
from tools.report_generator import generate_report
from tools.dashboard_data_generator import generate_dashboard_data
from tools.simple_dashboard import generate_dashboard_chart
from tools.logger_tool import log_event
from tools.memory_tool import load_memory, save_memory
from datetime import datetime

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("pharma_agent.agents.planner_agent")


class PlannerAgent(BaseAgent):
    """
    A coordinator agent that plans and triggers the execution of sub-agents
    and report generation.
    """

    def __init__(self):
        super().__init__(
            name="Planner Agent",
            role="Orchestrator that coordinates clinical trial searches, FDA approval lookups, and report generation."
        )
        self.clinical_agent = ClinicalTrialAgent()
        self.fda_agent = FDAApprovalAgent()

    def run(self, query: str) -> dict:
        """
        Parses query for disease and drug names, runs sub-agents,
        generates reports, dashboard data, charts, and evaluates results.

        Args:
            query (str): Space-separated disease and drug (e.g. "diabetes semaglutide").

        Returns:
            dict: Summary of the planned execution and status.
        """
        # Parse query. Expects: "<disease> <drug>"
        parts = query.strip().split()
        disease_query = parts[0] if len(parts) > 0 else "diabetes"
        drug_query = parts[1] if len(parts) > 1 else "semaglutide"

        log_event(self.name, "Workflow Orchestration", "RUNNING", f"Starting workflow for disease='{disease_query}' and drug='{drug_query}'")
        logger.info(f"PlannerAgent: Starting workflow for disease='{disease_query}' and drug='{drug_query}'...")

        # 1. Execute ClinicalTrialAgent
        print("\n--- STEP 1: Running Clinical Trial Agent ---")
        log_event(self.clinical_agent.name, f"Search trials: {disease_query}", "RUNNING", "Querying ClinicalTrials.gov")
        try:
            trials_summary = self.clinical_agent.run(disease_query)
            log_event(self.clinical_agent.name, f"Search trials: {disease_query}", "SUCCESS", f"Found {trials_summary.get('total_records_found', 0)} records")
        except Exception as e:
            logger.error(f"ClinicalTrialAgent failed: {e}")
            log_event(self.clinical_agent.name, f"Search trials: {disease_query}", "FAILED", f"Error: {e}")
            trials_summary = {"total_records_found": 0, "csv_output_path": os.path.join("data", "trials.csv")}

        # 2. Execute FDAApprovalAgent
        print("\n--- STEP 2: Running FDA Approval Agent ---")
        log_event(self.fda_agent.name, f"Search drug: {drug_query}", "RUNNING", "Querying openFDA")
        try:
            fda_summary = self.fda_agent.run(drug_query)
            log_event(self.fda_agent.name, f"Search drug: {drug_query}", "SUCCESS", f"Found {fda_summary.get('total_records_found', 0)} records")
        except Exception as e:
            logger.error(f"FDAApprovalAgent failed: {e}")
            log_event(self.fda_agent.name, f"Search drug: {drug_query}", "FAILED", f"Error: {e}")
            fda_summary = {"total_records_found": 0, "csv_output_path": os.path.join("data", "fda_results.csv")}

        # Paths definition
        trials_csv = os.path.join(project_root, 'data', 'trials.csv')
        fda_csv = os.path.join(project_root, 'data', 'fda_results.csv')
        output_report = os.path.join(project_root, 'reports', 'executive_briefing.md')
        dashboard_csv = os.path.join(project_root, 'data', 'dashboard_data.csv')
        dashboard_chart = os.path.join(project_root, 'reports', 'dashboard_chart.png')
        evaluator_report = os.path.join(project_root, 'reports', 'evaluation_results.md')

        # 3. Execute Report Generator
        print("\n--- STEP 3: Running Report Generator ---")
        log_event("Report Generator", "Generate Executive Briefing", "RUNNING", "Writing report executive_briefing.md")
        try:
            generate_report(
                trials_path=trials_csv,
                fda_path=fda_csv,
                output_path=output_report
            )
            report_status = "Success"
            log_event("Report Generator", "Generate Executive Briefing", "SUCCESS", f"Report generated at {output_report}")
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            report_status = f"Failed ({e})"
            log_event("Report Generator", "Generate Executive Briefing", "FAILED", f"Error: {e}")

        # 4. Execute Dashboard Data Generator
        print("\n--- STEP 4: Running Dashboard Data Generator ---")
        log_event("Dashboard Data Generator", "Consolidate CSVs", "RUNNING", "Creating dashboard_data.csv")
        try:
            generate_dashboard_data(
                trials_path=trials_csv,
                fda_path=fda_csv,
                output_path=dashboard_csv
            )
            dashboard_data_status = "Success"
            log_event("Dashboard Data Generator", "Consolidate CSVs", "SUCCESS", f"Dashboard data consolidated at {dashboard_csv}")
        except Exception as e:
            logger.error(f"Dashboard data generation failed: {e}")
            dashboard_data_status = f"Failed ({e})"
            log_event("Dashboard Data Generator", "Consolidate CSVs", "FAILED", f"Error: {e}")

        # 5. Execute Dashboard Chart Generator
        print("\n--- STEP 5: Running Dashboard Chart Generator ---")
        log_event("Dashboard Chart Generator", "Plot Chart", "RUNNING", "Creating dashboard_chart.png")
        try:
            generate_dashboard_chart(
                data_csv_path=dashboard_csv,
                output_image_path=dashboard_chart
            )
            dashboard_chart_status = "Success"
            log_event("Dashboard Chart Generator", "Plot Chart", "SUCCESS", f"Chart saved to {dashboard_chart}")
        except Exception as e:
            logger.error(f"Dashboard chart generation failed: {e}")
            dashboard_chart_status = f"Failed ({e})"
            log_event("Dashboard Chart Generator", "Plot Chart", "FAILED", f"Error: {e}")

        # 6. Execute Evaluator Agent
        print("\n--- STEP 6: Running Evaluator Agent ---")
        log_event("Evaluator Agent", "Validate Output Quality", "RUNNING", "Validating CSVs and reports")
        try:
            evaluator = EvaluatorAgent()
            eval_results = evaluator.run()
            log_event("Evaluator Agent", "Validate Output Quality", "SUCCESS", f"Evaluation completed: {eval_results.get('evaluation_score', 0)}/100")
        except Exception as e:
            logger.error(f"EvaluatorAgent failed: {e}")
            eval_results = {"evaluation_score": 0, "status": "FAIL", "issues_found": [str(e)], "strengths_found": []}
            log_event("Evaluator Agent", "Validate Output Quality", "FAILED", f"Error: {e}")

        # Update memory/session_memory.json
        run_record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "disease_query": disease_query,
            "drug_query": drug_query,
            "trials_records_found": trials_summary.get("total_records_found", 0),
            "fda_records_found": fda_summary.get("total_records_found", 0),
            "report_generation_status": report_status,
            "dashboard_data_status": dashboard_data_status,
            "dashboard_chart_status": dashboard_chart_status,
            "evaluator_score": eval_results.get("evaluation_score", 0),
            "evaluator_status": eval_results.get("status", "FAIL")
        }

        try:
            memory_data = load_memory("session_memory.json")
            if not isinstance(memory_data, list):
                memory_data = []
            memory_data.append(run_record)
            save_memory("session_memory.json", memory_data)
            log_event("Planner Agent", "Save Memory", "SUCCESS", "Workflow details saved to session memory")
        except Exception as e:
            logger.error(f"Saving session memory failed: {e}")
            log_event("Planner Agent", "Save Memory", "FAILED", f"Error: {e}")

        # Compile final workflow summary
        workflow_summary = {
            "disease_query": disease_query,
            "drug_query": drug_query,
            "trials_records_found": trials_summary.get("total_records_found", 0),
            "fda_records_found": fda_summary.get("total_records_found", 0),
            "report_generation_status": report_status,
            "report_output_path": output_report,
            "dashboard_data_path": dashboard_csv,
            "dashboard_chart_path": dashboard_chart,
            "evaluator_score": eval_results.get("evaluation_score", 0),
            "evaluator_status": eval_results.get("status", "FAIL"),
            "evaluator_report_path": evaluator_report
        }

        log_event(self.name, "Workflow Orchestration", "SUCCESS", "Workflow executed completely")
        return workflow_summary


if __name__ == "__main__":
    # Check for CLI arguments. Default to 'diabetes' and 'semaglutide'
    disease = "diabetes"
    drug = "semaglutide"

    if len(sys.argv) > 2:
        disease = sys.argv[1]
        drug = sys.argv[2]
    elif len(sys.argv) > 1:
        disease = sys.argv[1]

    # Instantiate PlannerAgent and run the planning pipeline
    planner = PlannerAgent()
    results = planner.run(f"{disease} {drug}")

    # Print final execution report
    print("\n" + "=" * 60)
    print(" PLANNER AGENT WORKFLOW SUMMARY")
    print("=" * 60)
    print(f"Disease Searched:      {results['disease_query']}")
    print(f"Drug Searched:         {results['drug_query']}")
    print(f"Clinical Trial Count:  {results['trials_records_found']}")
    print(f"FDA Label Count:       {results['fda_records_found']}")
    print(f"Report Status:         {results['report_generation_status']}")
    print(f"Report Location:       {results['report_output_path']}")
    print("=" * 60 + "\n")
