import os
import json
import logging
import requests
from tools.base_tool import BaseTool

logger = logging.getLogger("pharma_agent.tools.pubchem")

class PubChemTool(BaseTool):
    """Tool to query chemical compound properties from the PubChem REST API, with local JSON fallback."""

    def __init__(self):
        super().__init__(
            name="PubChem Compound Lookup",
            description="Fetches chemical properties (IUPAC Name, Molecular Formula, Molecular Weight, SMILES) for a compound."
        )
        self.api_url_base = os.getenv("PUBCHEM_API_URL", "https://pubchem.ncbi.nlm.nih.gov/rest/pug")
        # Resolve project root and data folder path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.getenv("DATA_DIR", "data")
        if not os.path.isabs(data_dir):
            data_dir = os.path.join(project_root, data_dir)
        self.local_db_path = os.path.join(data_dir, "sample_drugs.json")

    def run(self, query: str) -> dict:
        """Queries PubChem for chemical compound properties. Falls back to local database on failure.

        Args:
            query (str): Name of the compound (e.g., "Aspirin").

        Returns:
            dict: Structured chemical properties.
        """
        clean_query = query.strip().lower()
        logger.info(f"PubChemTool: Querying compound '{clean_query}'...")

        # 1. Attempt PubChem REST API request
        try:
            # We request MolecularFormula, MolecularWeight, IUPACName, and CanonicalSMILES
            url = f"{self.api_url_base}/compound/name/{clean_query}/property/MolecularFormula,MolecularWeight,IupacName,CanonicalSMILES/JSON"
            logger.debug(f"PubChemTool: Sending request to: {url}")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                properties_list = data.get("PropertyTable", {}).get("Properties", [])
                if properties_list:
                    props = properties_list[0]
                    logger.info("PubChemTool: Successfully fetched properties from PubChem API.")
                    return {
                        "source": "PubChem API",
                        "cid": props.get("CID", "Unknown"),
                        "iupac_name": props.get("IUPACName", "Unknown"),
                        "molecular_formula": props.get("MolecularFormula", "Unknown"),
                        "molecular_weight": f"{props.get('MolecularWeight', 'Unknown')} g/mol" if props.get('MolecularWeight') else "Unknown",
                        "smiles": props.get("CanonicalSMILES", "Unknown"),
                        "chemical_class": "Organic Compound"  # general default
                    }
                else:
                    logger.warning("PubChemTool: Empty properties list returned from PubChem API.")
            else:
                logger.warning(f"PubChemTool: PubChem API returned status code {response.status_code}.")
        except Exception as e:
            logger.error(f"PubChemTool: API request failed due to: {e}. Attempting local fallback.")

        # 2. Local Fallback Database
        return self._local_fallback(clean_query)

    def _local_fallback(self, clean_query: str) -> dict:
        logger.info(f"PubChemTool: Checking local database fallback at '{self.local_db_path}'...")
        if not os.path.exists(self.local_db_path):
            logger.error(f"PubChemTool: Local database file not found at '{self.local_db_path}'.")
            return self._empty_result(clean_query, "No local database found")

        try:
            with open(self.local_db_path, "r", encoding="utf-8") as f:
                db = json.load(f)
            
            # Match directly or by checking if query is in keys
            drug_key = None
            for key in db.keys():
                if clean_query in key or key in clean_query:
                    drug_key = key
                    break
            
            if drug_key:
                logger.info(f"PubChemTool: Found match in local database for '{clean_query}'.")
                pubchem_info = db[drug_key].get("pubchem", {})
                return {
                    "source": "Local Fallback Database",
                    "cid": pubchem_info.get("cid", "Unknown"),
                    "iupac_name": pubchem_info.get("iupac_name", "Unknown"),
                    "molecular_formula": pubchem_info.get("molecular_formula", "Unknown"),
                    "molecular_weight": pubchem_info.get("molecular_weight", "Unknown"),
                    "smiles": pubchem_info.get("smiles", "Unknown"),
                    "chemical_class": pubchem_info.get("chemical_class", "Unknown")
                }
            else:
                logger.warning(f"PubChemTool: Compound '{clean_query}' not found in local database.")
        except Exception as e:
            logger.error(f"PubChemTool: Failed to read local database: {e}")

        return self._empty_result(clean_query, "Compound not found in API or local database")

    def _empty_result(self, query: str, reason: str) -> dict:
        return {
            "source": "None",
            "cid": "Unknown",
            "iupac_name": f"Not found ({reason})",
            "molecular_formula": "Unknown",
            "molecular_weight": "Unknown",
            "smiles": "Unknown",
            "chemical_class": "Unknown"
        }
