"""
Dashboard Data Generator

This beginner-friendly Python script combines outputs from:
- data/trials.csv (Clinical Trials data)
- data/fda_results.csv (FDA Drug Labels data)

It creates a single, Power BI-ready CSV file named:
- data/dashboard_data.csv

It standardizes the schema using the following fields:
1. disease
2. drug_name
3. record_type (either "Clinical Trial" or "FDA Drug Label")
4. title_or_brand
5. status_or_manufacturer
6. phase_or_route
7. source
8. retrieved_date
"""

import os
import sys
import pandas as pd

def generate_dashboard_data(trials_path: str, fda_path: str, output_path: str) -> pd.DataFrame:
    """
    Combines clinical trials and FDA results into a single Power BI-ready CSV.
    
    Parameters:
        trials_path (str): Path to the trials.csv file.
        fda_path (str): Path to the fda_results.csv file.
        output_path (str): Path where the final combined dashboard_data.csv will be saved.
        
    Returns:
        pd.DataFrame: The combined DataFrame.
    """
    print(f"Starting dashboard data generation...")
    print(f"Reading clinical trials from: {trials_path}")
    print(f"Reading FDA drug labels from: {fda_path}")

    # Standardize columns we want in the final combined dataset
    target_columns = [
        "disease",
        "drug_name",
        "record_type",
        "title_or_brand",
        "status_or_manufacturer",
        "phase_or_route",
        "source",
        "retrieved_date"
    ]

    # Initialize empty lists to hold dataframes for combination
    dfs_to_combine = []

    # 1. Process Clinical Trials Data
    if os.path.exists(trials_path):
        try:
            df_trials = pd.read_csv(trials_path)
            if not df_trials.empty:
                # Map clinical trials fields to the standardized schema
                df_trials_mapped = pd.DataFrame()
                
                # 'disease' exists in trials
                df_trials_mapped["disease"] = df_trials["disease"] if "disease" in df_trials.columns else ""
                
                # 'drug_name' is not in trials.csv, so we populate with empty string
                df_trials_mapped["drug_name"] = ""
                
                # Set hardcoded record type for trials
                df_trials_mapped["record_type"] = "Clinical Trial"
                
                # 'study_title' maps to 'title_or_brand'
                df_trials_mapped["title_or_brand"] = df_trials["study_title"] if "study_title" in df_trials.columns else ""
                
                # 'status' maps to 'status_or_manufacturer'
                df_trials_mapped["status_or_manufacturer"] = df_trials["status"] if "status" in df_trials.columns else ""
                
                # 'phase' maps to 'phase_or_route'
                df_trials_mapped["phase_or_route"] = df_trials["phase"] if "phase" in df_trials.columns else ""
                
                # 'source' maps to 'source'
                df_trials_mapped["source"] = df_trials["source"] if "source" in df_trials.columns else "ClinicalTrials.gov"
                
                # 'retrieved_date' maps to 'retrieved_date'
                df_trials_mapped["retrieved_date"] = df_trials["retrieved_date"] if "retrieved_date" in df_trials.columns else ""

                # Ensure all standardized columns are present in the correct order
                df_trials_mapped = df_trials_mapped.reindex(columns=target_columns)
                dfs_to_combine.append(df_trials_mapped)
                print(f"-> Successfully processed {len(df_trials_mapped)} clinical trial records.")
            else:
                print("-> Clinical trials CSV is empty.")
        except Exception as e:
            print(f"Error reading or processing clinical trials CSV: {e}")
    else:
        print(f"Warning: Clinical trials file not found at '{trials_path}'.")

    # 2. Process FDA Drug Labels Data
    if os.path.exists(fda_path):
        try:
            df_fda = pd.read_csv(fda_path)
            if not df_fda.empty:
                # Map FDA fields to the standardized schema
                df_fda_mapped = pd.DataFrame()
                
                # 'disease' is not in fda_results.csv, so we populate with empty string
                df_fda_mapped["disease"] = ""
                
                # 'drug_name' exists in fda_results.csv
                df_fda_mapped["drug_name"] = df_fda["drug_name"] if "drug_name" in df_fda.columns else ""
                
                # Set hardcoded record type for FDA label
                df_fda_mapped["record_type"] = "FDA Drug Label"
                
                # 'brand_name' maps to 'title_or_brand'
                df_fda_mapped["title_or_brand"] = df_fda["brand_name"] if "brand_name" in df_fda.columns else ""
                
                # 'manufacturer' maps to 'status_or_manufacturer'
                df_fda_mapped["status_or_manufacturer"] = df_fda["manufacturer"] if "manufacturer" in df_fda.columns else ""
                
                # 'route' maps to 'phase_or_route'
                df_fda_mapped["phase_or_route"] = df_fda["route"] if "route" in df_fda.columns else ""
                
                # 'source' maps to 'source'
                df_fda_mapped["source"] = df_fda["source"] if "source" in df_fda.columns else "openFDA"
                
                # 'retrieved_date' maps to 'retrieved_date'
                df_fda_mapped["retrieved_date"] = df_fda["retrieved_date"] if "retrieved_date" in df_fda.columns else ""

                # Ensure all standardized columns are present in the correct order
                df_fda_mapped = df_fda_mapped.reindex(columns=target_columns)
                dfs_to_combine.append(df_fda_mapped)
                print(f"-> Successfully processed {len(df_fda_mapped)} FDA drug label records.")
            else:
                print("-> FDA results CSV is empty.")
        except Exception as e:
            print(f"Error reading or processing FDA results CSV: {e}")
    else:
        print(f"Warning: FDA results file not found at '{fda_path}'.")

    # 3. Concatenate and save results
    if dfs_to_combine:
        # Concatenate all dataframes in the list
        combined_df = pd.concat(dfs_to_combine, ignore_index=True)
        
        # Fill any missing/NaN values with an empty string for Power BI clean-up
        combined_df = combined_df.fillna("")
        
        # Ensure the directory for output exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        # Save to CSV
        combined_df.to_csv(output_path, index=False)
        print(f"SUCCESS: Combined data saved to: {output_path}")
        print(f"Total Combined Records: {len(combined_df)}")
        return combined_df
    else:
        print("ERROR: No data was combined because both source CSV files were missing or empty.")
        # Create an empty CSV file with target headers to avoid breaking downstreams
        empty_df = pd.DataFrame(columns=target_columns)
        empty_df.to_csv(output_path, index=False)
        return empty_df

if __name__ == "__main__":
    # Resolve absolute paths based on the location of this script
    # This script resides in tools/, so project root is one level up.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    # Set up file paths
    trials_csv = os.path.join(project_root, "data", "trials.csv")
    fda_csv = os.path.join(project_root, "data", "fda_results.csv")
    output_csv = os.path.join(project_root, "data", "dashboard_data.csv")

    print("==================================================")
    print("Running Dashboard Data Generator Tool Test Block")
    print("==================================================")
    
    # Run the generator
    combined_data = generate_dashboard_data(
        trials_path=trials_csv,
        fda_path=fda_csv,
        output_path=output_csv
    )
    
    # Print sample output to confirm results
    if not combined_data.empty:
        print("\nFirst few rows of the generated dashboard data:")
        print(combined_data.head())
    
    print("==================================================")
