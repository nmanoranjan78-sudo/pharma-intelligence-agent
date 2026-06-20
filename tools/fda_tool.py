"""
openFDA Drug Label API Search & CSV Exporter (Beginner-Friendly Version)

This script demonstrates how to:
1. Query the openFDA Drug Label API for a brand or generic drug name.
2. Retrieve up to 5 results matching the search term.
3. Extract relevant fields: drug_name, brand_name, manufacturer, product_type, route, substance_name.
4. Save the results into 'data/fda_results.csv' using Pandas.

Dependencies:
    requests (Install via: pip install requests)
    pandas (Install via: pip install pandas)

Usage:
    python tools/fda_tool.py
    python tools/fda_tool.py metformin
"""

import os
import sys
import datetime
import requests
import pandas as pd
import logging

# Ensure project root is in the system path so we can run this script directly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.base_tool import BaseTool

# API Endpoint URL for openFDA drug labels
API_URL = "https://api.fda.gov/drug/label.json"


def fetch_and_save_fda_labels(drug_query: str = "semaglutide", limit: int = 5):
    """
    Searches the openFDA API for a drug name, extracts relevant label details,
    and saves the top 5 results to data/fda_results.csv using Pandas.
    """
    clean_query = drug_query.strip().lower()
    print(f"1. Querying openFDA API for drug: '{clean_query}'...")

    # Set up search parameters. We search for the query in both brand and generic name.
    params = {
        "search": f'openfda.brand_name:"{clean_query}" OR openfda.generic_name:"{clean_query}"',
        "limit": limit
    }

    try:
        # Perform the GET request
        response = requests.get(API_URL, params=params, timeout=10)

        # Check if the request succeeded
        if response.status_code != 200:
            print(f"Error: API returned status code {response.status_code}")
            return

        # Parse JSON data
        data = response.json()
        results = data.get("results", [])

        if not results:
            print(f"No results found for drug: '{clean_query}'")
            return

        print(f"2. Parsing {len(results)} results from openFDA...")
        extracted_data = []
        retrieved_date = datetime.date.today().isoformat()

        for result in results:
            openfda = result.get("openfda", {})

            # Extract fields (handling the fact that openFDA returns fields as lists)
            brand_name = ", ".join(openfda.get("brand_name", [])) or "Unknown"
            manufacturer = ", ".join(openfda.get("manufacturer_name", [])) or "Unknown"
            product_type = ", ".join(openfda.get("product_type", [])) or "Unknown"
            route = ", ".join(openfda.get("route", [])) or "Unknown"
            substance_name = ", ".join(openfda.get("substance_name", [])) or "Unknown"

            extracted_data.append({
                "drug_name": clean_query,
                "brand_name": brand_name,
                "manufacturer": manufacturer,
                "product_type": product_type,
                "route": route,
                "substance_name": substance_name,
                "source": "openFDA API",
                "retrieved_date": retrieved_date
            })

        # 3. Create Pandas DataFrame
        df = pd.DataFrame(extracted_data)

        # 4. Save results to data/fda_results.csv
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        csv_filepath = os.path.join(data_dir, "fda_results.csv")

        print(f"3. Saving results to '{csv_filepath}' using Pandas...")
        df.to_csv(csv_filepath, index=False)

        print("\n" + "=" * 80)
        print("FDA DRUG LABEL SEARCH SUCCESSFUL!")
        print(f"Results saved to: {csv_filepath}")
        print("=" * 80)
        for idx, row in enumerate(df.to_dict(orient="records"), 1):
            print(f"\nResult #{idx}:")
            print(f"  Drug Name:      {row['drug_name']}")
            print(f"  Brand Name:     {row['brand_name']}")
            print(f"  Manufacturer:   {row['manufacturer']}")
            print(f"  Product Type:   {row['product_type']}")
            print(f"  Route:          {row['route']}")
            print(f"  Substance Name: {row['substance_name']}")
            print(f"  Retrieved Date: {row['retrieved_date']}")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"An error occurred: {e}")


# =====================================================================
# Backward Compatibility: Keep the FdaTool class for Agent Orchestration
# =====================================================================
logger = logging.getLogger("pharma_agent.tools.fda")

class FdaTool(BaseTool):
    """Tool to query drug label information from openFDA API, with a local JSON fallback."""

    def __init__(self):
        super().__init__(
            name="openFDA Drug Label Lookup",
            description="Fetches indications, usage, warnings, dosage, and active ingredients for a given drug."
        )
        self.api_url = API_URL
        self.api_key = os.getenv("OPENFDA_API_KEY", "")
        
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.getenv("DATA_DIR", "data")
        if not os.path.isabs(data_dir):
            data_dir = os.path.join(project_root, data_dir)
        self.local_db_path = os.path.join(data_dir, "sample_drugs.json")

    def run(self, query: str) -> dict:
        clean_query = query.strip().lower()
        logger.info(f"FdaTool: Querying drug '{clean_query}'...")

        try:
            params = {
                "search": f'openfda.brand_name:"{clean_query}" OR openfda.generic_name:"{clean_query}"',
                "limit": 1
            }
            if self.api_key:
                params["api_key"] = self.api_key

            response = requests.get(self.api_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                if results:
                    result = results[0]
                    openfda = result.get("openfda", {})
                    brand_names = openfda.get("brand_name", [query.capitalize()])
                    generic_names = openfda.get("generic_name", ["Unknown"])
                    active_ingredients = result.get("active_ingredient", ["Information not available"])
                    purpose = result.get("purpose", ["Information not available"])
                    indications = result.get("indications_and_usage", ["Information not available"])
                    warnings = result.get("warnings", ["Information not available"])
                    side_effects = result.get("adverse_reactions", ["Information not available"])
                    dosage = result.get("dosage_and_administration", ["Information not available"])

                    return {
                        "source": "openFDA API",
                        "brand_name": brand_names[0] if brand_names else query.capitalize(),
                        "generic_name": generic_names[0] if generic_names else "Unknown",
                        "active_ingredient": active_ingredients[0] if isinstance(active_ingredients, list) else active_ingredients,
                        "purpose": purpose[0] if isinstance(purpose, list) else purpose,
                        "indications_and_usage": indications[0] if isinstance(indications, list) else indications,
                        "warnings": warnings[0] if isinstance(warnings, list) else warnings,
                        "side_effects": side_effects[0] if isinstance(side_effects, list) else side_effects,
                        "dosage_and_administration": dosage[0] if isinstance(dosage, list) else dosage
                    }
            else:
                logger.warning(f"FdaTool: openFDA API returned status code {response.status_code}.")
        except Exception as e:
            logger.error(f"FdaTool: API request failed: {e}. Attempting local fallback.")

        return self._local_fallback(clean_query)

    def _local_fallback(self, clean_query: str) -> dict:
        if not os.path.exists(self.local_db_path):
            return self._empty_result(clean_query, "No local database found")

        try:
            import json
            with open(self.local_db_path, "r", encoding="utf-8") as f:
                db = json.load(f)
            
            drug_key = None
            for key in db.keys():
                if clean_query in key or key in clean_query:
                    drug_key = key
                    break
            
            if drug_key:
                fda_info = db[drug_key].get("fda", {})
                return {
                    "source": "Local Fallback Database",
                    "brand_name": fda_info.get("brand_name", clean_query.capitalize()),
                    "generic_name": fda_info.get("generic_name", "Unknown"),
                    "active_ingredient": fda_info.get("active_ingredient", "N/A"),
                    "purpose": fda_info.get("purpose", "N/A"),
                    "indications_and_usage": fda_info.get("indications_and_usage", "N/A"),
                    "warnings": fda_info.get("warnings", "N/A"),
                    "side_effects": fda_info.get("side_effects", "N/A"),
                    "dosage_and_administration": fda_info.get("dosage_and_administration", "N/A")
                }
        except Exception as e:
            logger.error(f"FdaTool: Failed to read local database: {e}")

        return self._empty_result(clean_query, "Drug not found in API or local database")

    def _empty_result(self, query: str, reason: str) -> dict:
        return {
            "source": "None",
            "brand_name": query.capitalize(),
            "generic_name": "Unknown",
            "active_ingredient": f"Not found ({reason})",
            "purpose": "N/A",
            "indications_and_usage": "N/A",
            "warnings": "N/A",
            "side_effects": "N/A",
            "dosage_and_administration": "N/A"
        }


if __name__ == "__main__":
    # If run as a standalone script:
    # Default to 'semaglutide' if no command-line argument is passed.
    search_term = "semaglutide"
    if len(sys.argv) > 1:
        search_term = " ".join(sys.argv[1:])

    fetch_and_save_fda_labels(search_term)
