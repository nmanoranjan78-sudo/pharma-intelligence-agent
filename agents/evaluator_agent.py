"""
Evaluator Agent

This is a beginner-friendly agent that evaluates the generated CSV files
(trials.csv, fda_results.csv) and the executive briefing report (executive_briefing.md).
It checks:
- File existence and record counts
- Schema compliance (required columns)
- Citation check (source links/citations)
- Data integrity (duplicate rows)

It outputs an evaluation report to reports/evaluation_results.md.
"""

import os
import sys
import logging
import pandas as pd
from datetime import datetime

# Ensure project root is in the system path so Python can find base agent and other packages
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.base_agent import BaseAgent

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("pharma_agent.agents.evaluator_agent")


class EvaluatorAgent(BaseAgent):
    """
    An agent that reads CSV data and Markdown briefings to evaluate quality,
    calculates a score out of 100, lists strengths/issues, and outputs reports.
    """

    def __init__(self):
        super().__init__(
            name="Evaluator Agent",
            role="Specialist in validating data schema, source citation, and report completeness."
        )

    def run(self, query: str = "") -> dict:
        """
        Runs the evaluation pipeline. Checks availability of trials.csv, fda_results.csv,
        and executive_briefing.md, validates schemas, verifies source citations, and checks
        for duplicate rows. Generates an evaluation report saved to reports/evaluation_results.md.
        """
        logger.info("EvaluatorAgent: Starting evaluation process...")

        # Resolve paths to project files
        trials_path = os.path.join(project_root, "data", "trials.csv")
        fda_path = os.path.join(project_root, "data", "fda_results.csv")
        briefing_path = os.path.join(project_root, "reports", "executive_briefing.md")
        output_report_path = os.path.join(project_root, "reports", "evaluation_results.md")

        # Required columns definition
        trials_required_cols = [
            "disease", "nct_id", "study_title", "status", "phase", "sponsor", "source", "retrieved_date"
        ]
        fda_required_cols = [
            "drug_name", "brand_name", "manufacturer", "product_type", "route", "substance_name", "source", "retrieved_date"
        ]

        # Scoring tracker
        scores = {
            "trials_avail": 0,       # Max 15
            "fda_avail": 0,          # Max 15
            "briefing_avail": 0,     # Max 15
            "schema_check": 0,       # Max 20
            "source_check": 0,       # Max 20
            "duplicate_check": 0     # Max 15
        }
        
        issues = []
        strengths = []

        # Data placeholders
        df_trials = None
        df_fda = None
        briefing_content = ""

        # --- 1. Clinical Trials CSV Availability & Records (Max 15 points) ---
        if os.path.exists(trials_path):
            scores["trials_avail"] += 10
            try:
                df_trials = pd.read_csv(trials_path)
                num_records = len(df_trials)
                if num_records > 0:
                    scores["trials_avail"] += 5
                    strengths.append(f"Clinical trial records are available in trials.csv (found {num_records} record(s)).")
                else:
                    issues.append("Clinical trial dataset trials.csv is empty (contains no records).")
            except Exception as e:
                issues.append(f"Failed to read clinical trial dataset trials.csv: {e}")
        else:
            issues.append("Clinical trial dataset trials.csv is missing.")

        # --- 2. FDA Results CSV Availability & Records (Max 15 points) ---
        if os.path.exists(fda_path):
            scores["fda_avail"] += 10
            try:
                df_fda = pd.read_csv(fda_path)
                num_records = len(df_fda)
                if num_records > 0:
                    scores["fda_avail"] += 5
                    strengths.append(f"FDA drug label records are available in fda_results.csv (found {num_records} record(s)).")
                else:
                    issues.append("FDA results dataset fda_results.csv is empty (contains no records).")
            except Exception as e:
                issues.append(f"Failed to read FDA results dataset fda_results.csv: {e}")
        else:
            issues.append("FDA results dataset fda_results.csv is missing.")

        # --- 3. Executive Briefing Availability & Non-empty (Max 15 points) ---
        if os.path.exists(briefing_path):
            scores["briefing_avail"] += 10
            try:
                with open(briefing_path, "r", encoding="utf-8") as f:
                    briefing_content = f.read()
                
                if len(briefing_content.strip()) > 0:
                    scores["briefing_avail"] += 5
                    strengths.append("Executive briefing report executive_briefing.md is generated and is not empty.")
                else:
                    issues.append("Executive briefing report executive_briefing.md is empty.")
            except Exception as e:
                issues.append(f"Failed to read executive briefing report executive_briefing.md: {e}")
        else:
            issues.append("Executive briefing report executive_briefing.md is missing.")

        # --- 4. Required Columns Present (Max 20 points, 10 points per file) ---
        # A. Clinical Trials Schema Check
        if df_trials is not None:
            missing_trials_cols = [col for col in trials_required_cols if col not in df_trials.columns]
            if not missing_trials_cols:
                scores["schema_check"] += 10
                strengths.append("All required columns are present in trials.csv.")
            else:
                issues.append(f"trials.csv is missing required columns: {', '.join(missing_trials_cols)}")
        else:
            issues.append("Schema check skipped for trials.csv due to missing file.")

        # B. FDA Results Schema Check
        if df_fda is not None:
            missing_fda_cols = [col for col in fda_required_cols if col not in df_fda.columns]
            if not missing_fda_cols:
                scores["schema_check"] += 10
                strengths.append("All required columns are present in fda_results.csv.")
            else:
                issues.append(f"fda_results.csv is missing required columns: {', '.join(missing_fda_cols)}")
        else:
            issues.append("Schema check skipped for fda_results.csv due to missing file.")

        # --- 5. Source Links / Citations Present (Max 20 points) ---
        # A. Report Citation Check (10 points)
        if briefing_content:
            has_trials_citation = "clinicaltrials" in briefing_content.lower()
            has_fda_citation = "openfda" in briefing_content.lower()
            
            citations_score = 0
            if has_trials_citation:
                citations_score += 5
            else:
                issues.append("Briefing report executive_briefing.md does not cite ClinicalTrials.gov as a source.")
                
            if has_fda_citation:
                citations_score += 5
            else:
                issues.append("Briefing report executive_briefing.md does not cite openFDA as a source.")
                
            scores["source_check"] += citations_score
            if has_trials_citation and has_fda_citation:
                strengths.append("Briefing report correctly cites both ClinicalTrials.gov and openFDA data sources.")
        else:
            issues.append("Briefing report citation check skipped due to missing briefing file.")

        # B. CSV Source Field Population Check (10 points)
        csv_source_score = 0
        trials_source_valid = False
        fda_source_valid = False

        if df_trials is not None:
            if "source" in df_trials.columns:
                empty_sources = df_trials["source"].isna().sum() + (df_trials["source"] == "").sum()
                if empty_sources == 0:
                    csv_source_score += 5
                    trials_source_valid = True
                else:
                    issues.append(f"trials.csv contains {empty_sources} record(s) with missing or empty source field.")
            else:
                issues.append("trials.csv is missing the source column for records check.")
        
        if df_fda is not None:
            if "source" in df_fda.columns:
                empty_sources = df_fda["source"].isna().sum() + (df_fda["source"] == "").sum()
                if empty_sources == 0:
                    csv_source_score += 5
                    fda_source_valid = True
                else:
                    issues.append(f"fda_results.csv contains {empty_sources} record(s) with missing or empty source field.")
            else:
                issues.append("fda_results.csv is missing the source column for records check.")

        scores["source_check"] += csv_source_score
        if trials_source_valid and fda_source_valid:
            strengths.append("All CSV records in trials.csv and fda_results.csv have populated source fields.")

        # --- 6. Duplicate Rows Check (Max 15 points) ---
        # A. Clinical Trials Duplicates (7 points)
        if df_trials is not None:
            duplicate_trials = df_trials.duplicated().sum()
            if duplicate_trials == 0:
                scores["duplicate_check"] += 7
                strengths.append("No duplicate rows found in trials.csv.")
            else:
                issues.append(f"trials.csv contains {duplicate_trials} duplicate row(s).")
        else:
            issues.append("Duplicate check skipped for trials.csv due to missing file.")

        # B. FDA Results Duplicates (8 points)
        if df_fda is not None:
            duplicate_fda = df_fda.duplicated().sum()
            if duplicate_fda == 0:
                scores["duplicate_check"] += 8
                strengths.append("No duplicate rows found in fda_results.csv.")
            else:
                issues.append(f"fda_results.csv contains {duplicate_fda} duplicate row(s).")
        else:
            issues.append("Duplicate check skipped for fda_results.csv due to missing file.")

        # Calculate Final Score
        evaluation_score = sum(scores.values())
        status = "PASS" if evaluation_score >= 80 else "FAIL"

        # Construct final evaluation markdown content
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Build score details status strings
        briefing_status = "✓ PASS" if scores["briefing_avail"] == 15 else "✗ FAIL"
        trials_avail_status = "✓ PASS" if scores["trials_avail"] == 15 else "✗ FAIL"
        fda_avail_status = "✓ PASS" if scores["fda_avail"] == 15 else "✗ FAIL"
        schema_status = "✓ PASS" if scores["schema_check"] == 20 else "✗ FAIL"
        source_status = "✓ PASS" if scores["source_check"] == 20 else "✗ FAIL"
        duplicate_status = "✓ PASS" if scores["duplicate_check"] == 15 else "✗ FAIL"

        report_lines = [
            "# Pharma Intelligence Data & Report Evaluation",
            f"**Date Evaluated:** {timestamp_str}",
            f"**Overall Evaluation Score:** `{evaluation_score}/100`",
            f"**Status:** **{status}**",
            "",
            "## Executive Summary",
            "This report evaluates the availability, schema conformity, source citation validity, and data integrity of clinical trial records, FDA drug labels, and generated executive briefing reports.",
            "",
            "### Detailed Scorecard",
            "| Evaluation Criteria | Max Score | Score Awarded | Status |",
            "| :--- | :---: | :---: | :---: |",
            f"| **Clinical Trial CSV Availability** | 15 | {scores['trials_avail']} | {trials_avail_status} |",
            f"| **FDA Results CSV Availability** | 15 | {scores['fda_avail']} | {fda_avail_status} |",
            f"| **Executive Briefing Report Availability** | 15 | {scores['briefing_avail']} | {briefing_status} |",
            f"| **CSV Schema Conformity (Required Columns)** | 20 | {scores['schema_check']} | {schema_status} |",
            f"| **Source Citation & API Checks** | 20 | {scores['source_check']} | {source_status} |",
            f"| **Data Integrity Check (Duplicate Rows)** | 15 | {scores['duplicate_check']} | {duplicate_status} |",
            f"| **Total Evaluation Score** | **100** | **{evaluation_score}** | **{status}** |",
            "",
            "## Strengths Found"
        ]

        if strengths:
            for strength in strengths:
                report_lines.append(f"- ✓ {strength}")
        else:
            report_lines.append("- None identified.")

        report_lines.append("")
        report_lines.append("## Issues Found")
        if issues:
            for issue in issues:
                report_lines.append(f"- ✗ {issue}")
        else:
            report_lines.append("- None identified. All systems meet the required quality metrics.")

        report_content = "\n".join(report_lines) + "\n"

        # Ensure reports directory exists
        reports_dir = os.path.dirname(output_report_path)
        if reports_dir and not os.path.exists(reports_dir):
            os.makedirs(reports_dir, exist_ok=True)

        # Save evaluation report
        try:
            with open(output_report_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            logger.info(f"EvaluatorAgent: Successfully saved evaluation results to '{output_report_path}'.")
        except Exception as e:
            logger.error(f"EvaluatorAgent: Failed to write evaluation report: {e}")

        # Return results summary dictionary
        return {
            "evaluation_score": evaluation_score,
            "status": status,
            "issues_found": issues,
            "strengths_found": strengths,
            "results_filepath": output_report_path
        }


if __name__ == "__main__":
    # Instantiate the agent and run the evaluation
    agent = EvaluatorAgent()
    results = agent.run()

    # Print a clean, beginner-friendly execution summary
    print("\n" + "=" * 60)
    print(" EVALUATOR AGENT SUMMARY REPORT")
    print("=" * 60)
    print(f"Evaluation Score: {results['evaluation_score']}/100")
    print(f"Status:           {results['status']}")
    print(f"Issues Found:     {len(results['issues_found'])}")
    print(f"Strengths Found:  {len(results['strengths_found'])}")
    print(f"Results Saved To: {results['results_filepath']}")
    print("=" * 60)
    if results['issues_found']:
        print("\nIssues:")
        for issue in results['issues_found']:
            print(f"  - {issue}")
    if results['strengths_found']:
        print("\nStrengths:")
        for strength in results['strengths_found']:
            print(f"  - {strength}")
    print("=" * 60 + "\n")
