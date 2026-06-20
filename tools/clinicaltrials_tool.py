"""
ClinicalTrials.gov API Search & CSV Exporter (Pandas Version)

This beginner-friendly script queries the ClinicalTrials.gov v2 API to search for
clinical trials related to a given condition/disease, and exports the results to a CSV file.

Requirements:
- Uses requests library
- Uses pandas library
- Queries https://clinicaltrials.gov/api/v2/studies
- Returns up to 5 studies
- Defaults to 'diabetes' if no condition is provided
- Sorts results by disease/search term in A-Z ascending order before saving
- Saves to data/trials.csv with specified columns

Run options:
    python tools/clinicaltrials_tool.py
    python tools/clinicaltrials_tool.py cancer
"""

import os
import sys
import datetime
import requests
import pandas as pd

# API Endpoint URL for ClinicalTrials.gov API v2
API_URL = "https://clinicaltrials.gov/api/v2/studies"


def fetch_and_save_trials(disease_query: str = "diabetes"):
    """
    Searches the ClinicalTrials.gov API for a disease/condition, extracts relevant fields,
    sorts them using Pandas, and saves the top 5 results to data/trials.csv.
    """
    # Clean the input query (lowercase for consistency)
    clean_query = disease_query.strip().lower()
    print(f"1. Querying ClinicalTrials.gov API for disease/condition: '{clean_query}'...")

    # API parameters: query condition and page size (limit to 5)
    params = {
        "query.cond": clean_query,
        "pageSize": 5
    }

    try:
        # Fetch the studies from the ClinicalTrials.gov API
        response = requests.get(API_URL, params=params, timeout=10)

        # Check if response is successful
        if response.status_code != 200:
            print(f"Error: API returned status code {response.status_code}")
            return

        # Parse JSON data
        data = response.json()
        studies = data.get("studies", [])

        if not studies:
            print(f"No trials found for disease: '{clean_query}'")
            return

        print(f"2. Parsing {len(studies)} studies...")
        trials_list = []
        retrieved_date = datetime.date.today().isoformat()

        for study in studies:
            protocol = study.get("protocolSection", {})

            # Extract NCT ID
            identification = protocol.get("identificationModule", {})
            nct_id = identification.get("nctId", "Unknown NCT ID")

            # Extract Study Title (Official Title fallback to Brief Title)
            study_title = (
                identification.get("officialTitle")
                or identification.get("briefTitle")
                or "Unknown Title"
            )

            # Extract Status
            status = protocol.get("statusModule", {}).get("overallStatus", "Unknown")

            # Extract Phase
            design = protocol.get("designModule", {})
            phases = design.get("phases", [])
            phase = ", ".join(phases) if phases else "N/A"

            # Extract Sponsor
            sponsor = (
                protocol.get("sponsorCollaboratorsModule", {})
                .get("leadSponsor", {})
                .get("name", "Unknown Sponsor")
            )

            # Build trial row dictionary matching the required CSV columns
            trials_list.append({
                "disease": clean_query,
                "nct_id": nct_id,
                "study_title": study_title,
                "status": status,
                "phase": phase,
                "sponsor": sponsor,
                "source": "ClinicalTrials.gov API",
                "retrieved_date": retrieved_date
            })

        # 3. Load results into a Pandas DataFrame
        df = pd.DataFrame(trials_list)

        # 4. Sort results by disease/search term in A-Z ascending order.
        # Since 'disease' is the same for a single query, we also sort by 'study_title'
        # to ensure a consistent, clean alphabetical list.
        print(f"3. Sorting results alphabetically by disease/search term...")
        df_sorted = df.sort_values(by=["disease", "study_title"], ascending=True)

        # 5. Save results into data/trials.csv
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        csv_filepath = os.path.join(data_dir, "trials.csv")

        # Save to CSV using Pandas (index=False prevents writing the row index)
        print(f"4. Saving results to '{csv_filepath}' using Pandas...")
        df_sorted.to_csv(csv_filepath, index=False)

        print("\n" + "=" * 80)
        print("CLINICAL TRIALS SEARCH SUCCESSFUL!")
        print(f"Results saved to: {csv_filepath}")
        print("=" * 80)
        
        # Display the sorted DataFrame in a neat way
        for idx, row in enumerate(df_sorted.to_dict(orient="records"), 1):
            print(f"\nTrial #{idx}:")
            print(f"  Disease:        {row['disease']}")
            print(f"  NCT ID:         {row['nct_id']}")
            print(f"  Title:          {row['study_title']}")
            print(f"  Status:         {row['status']}")
            print(f"  Phase:          {row['phase']}")
            print(f"  Sponsor:        {row['sponsor']}")
            print(f"  Retrieved Date: {row['retrieved_date']}")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Check if a custom disease/condition name is passed as command-line argument
    # Otherwise default search term to "diabetes"
    query_condition = "diabetes"
    if len(sys.argv) > 1:
        query_condition = " ".join(sys.argv[1:])

    fetch_and_save_trials(query_condition)
