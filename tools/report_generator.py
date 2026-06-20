import os
import pandas as pd
from datetime import datetime

def generate_report(trials_path='data/trials.csv', fda_path='data/fda_results.csv', output_path='reports/executive_briefing.md'):
    """
    Reads clinical trials and FDA drug label CSV files, aggregates key metrics,
    and writes a clean Markdown executive briefing report.
    
    Parameters:
        trials_path (str): Path to the clinical trials CSV file.
        fda_path (str): Path to the FDA results CSV file.
        output_path (str): Path where the final markdown report should be saved.
    """
    # Step 1: Read the CSV data using Pandas
    print(f"Reading clinical trials data from: {trials_path}")
    if not os.path.exists(trials_path):
        raise FileNotFoundError(f"Could not find clinical trials data at: {trials_path}")
    df_trials = pd.read_csv(trials_path)

    print(f"Reading FDA drug results data from: {fda_path}")
    if not os.path.exists(fda_path):
        raise FileNotFoundError(f"Could not find FDA data at: {fda_path}")
    df_fda = pd.read_csv(fda_path)

    # Step 2: Analyze and summarize clinical trials
    # Count the total number of trial rows
    total_trials = len(df_trials)
    
    # Calculate the frequency of each disease and get the top studied ones
    if 'disease' in df_trials.columns:
        # value_counts() counts occurrences of each unique value
        top_diseases = df_trials['disease'].value_counts()
    else:
        top_diseases = pd.Series(dtype=int)

    # Step 3: Analyze and summarize FDA results
    # Count the total number of FDA rows
    total_fda = len(df_fda)
    
    # Calculate the frequency of each drug name and get the top approved ones
    if 'drug_name' in df_fda.columns:
        top_drugs = df_fda['drug_name'].value_counts()
    else:
        top_drugs = pd.Series(dtype=int)

    # Step 4: Get current date for the report header
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Step 5: Construct the Markdown report content
    report_lines = [
        "# Pharma Intelligence Executive Briefing",
        f"**Date Generated:** {current_date}",
        "",
        "## Clinical Trials Summary",
        f"- **Total Clinical Trial Records:** {total_trials}",
        "- **Top Studied Diseases in Trials:**"
    ]
    
    if not top_diseases.empty:
        for disease, count in top_diseases.items():
            report_lines.append(f"  - **{disease.capitalize()}**: {count} trial(s)")
    else:
        report_lines.append("  - No disease data available.")
        
    report_lines.extend([
        "",
        "## FDA Drug Label Summary",
        f"- **Total FDA Drug Label Records:** {total_fda}",
        "- **Top Approved Drug Names:**"
    ])
    
    if not top_drugs.empty:
        for drug, count in top_drugs.items():
            report_lines.append(f"  - **{drug.capitalize()}**: {count} record(s)")
    else:
        report_lines.append("  - No drug name data available.")

    # Step 6: Generate a Key Business Insight
    report_lines.extend([
        "",
        "## Key Business Insight",
    ])
    
    if not top_diseases.empty and not top_drugs.empty:
        most_studied_disease = top_diseases.index[0].capitalize()
        most_approved_drug = top_drugs.index[0].capitalize()
        
        insight = (
            f"Active clinical research shows high activity focusing on **{most_studied_disease}**, "
            f"while the FDA approval data reflects corresponding focus with drugs like **{most_approved_drug}** "
            f"appearing frequently. Aligning clinical trial pipelines with FDA regulatory trends allows "
            f"organizations to identify strategic areas for development and commercialization."
        )
        report_lines.append(insight)
    else:
        report_lines.append("Insufficient data available to formulate a business insight.")

    # Step 7: Specify Data Sources
    report_lines.extend([
        "",
        "## Data Sources",
    ])
    
    # Extract unique source names if the source columns exist
    trials_sources = df_trials['source'].unique() if 'source' in df_trials.columns else ['ClinicalTrials.gov']
    fda_sources = df_fda['source'].unique() if 'source' in df_fda.columns else ['openFDA']
    
    report_lines.extend([
        f"- **Clinical Trials Data**: `{os.path.basename(trials_path)}` (Source: {', '.join(trials_sources)})",
        f"- **FDA Drug Label Data**: `{os.path.basename(fda_path)}` (Source: {', '.join(fda_sources)})"
    ])

    # Join list of lines into a single markdown string
    report_content = "\n".join(report_lines) + "\n"

    # Step 8: Write to file
    # Ensure reports/ directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created directory: {output_dir}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print(f"Report successfully generated and saved to: {output_path}")

if __name__ == '__main__':
    # Determine the directory where this script resides
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Resolve the project root (one level up from tools/)
    project_root = os.path.dirname(script_dir)

    # Set up absolute paths relative to the project root
    trials_csv = os.path.join(project_root, 'data', 'trials.csv')
    fda_csv = os.path.join(project_root, 'data', 'fda_results.csv')
    output_report = os.path.join(project_root, 'reports', 'executive_briefing.md')

    print("==================================================")
    print("Starting Pharma Intelligence Report Generation...")
    print("==================================================")
    
    try:
        generate_report(
            trials_path=trials_csv,
            fda_path=fda_csv,
            output_path=output_report
        )
        print("\nSUCCESS: Briefing report generated successfully.")
    except Exception as e:
        print(f"\nERROR: Failed to generate report: {e}")
    print("==================================================")
