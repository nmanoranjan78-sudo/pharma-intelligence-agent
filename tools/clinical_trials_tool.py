import os
import logging
import requests
from tools.base_tool import BaseTool

logger = logging.getLogger("pharma_agent.tools.clinical_trials")

class ClinicalTrialsTool(BaseTool):
    """Tool to search ClinicalTrials.gov API for studies related to a disease name."""

    def __init__(self):
        super().__init__(
            name="ClinicalTrials Search Tool",
            description="Searches ClinicalTrials.gov API for a disease name and returns trial title, phase, status, and sponsor."
        )
        self.api_url = "https://clinicaltrials.gov/api/v2/studies"

    def run(self, query: str) -> dict:
        """Queries ClinicalTrials.gov API for trials matching a disease name.

        Args:
            query (str): Disease name or condition (e.g., "diabetes").

        Returns:
            dict: Dictionary containing the source and a list of matching trials.
        """
        clean_query = query.strip().lower()
        logger.info(f"ClinicalTrialsTool: Querying trials for disease '{clean_query}'...")

        try:
            # query.cond filters specifically by conditions (diseases)
            params = {
                "query.cond": clean_query,
                "pageSize": 5
            }
            logger.debug(f"ClinicalTrialsTool: Sending request to: {self.api_url} with params {params}")
            response = requests.get(self.api_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                studies = data.get("studies", [])
                
                trials = []
                for study in studies:
                    protocol = study.get("protocolSection", {})
                    
                    # 1. Trial Title
                    identification = protocol.get("identificationModule", {})
                    title = identification.get("officialTitle") or identification.get("briefTitle") or "Unknown Title"
                    
                    # 2. Phase
                    design = protocol.get("designModule", {})
                    phases = design.get("phases", [])
                    phase_str = ", ".join(phases) if phases else "N/A"
                    
                    # 3. Status
                    status = protocol.get("statusModule", {}).get("overallStatus", "Unknown")
                    
                    # 4. Sponsor
                    sponsor = protocol.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name", "Unknown Sponsor")
                    
                    trials.append({
                        "title": title,
                        "phase": phase_str,
                        "status": status,
                        "sponsor": sponsor
                    })
                
                logger.info(f"ClinicalTrialsTool: Successfully fetched {len(trials)} trials from API.")
                return {
                    "source": "ClinicalTrials.gov API",
                    "query": query,
                    "trials": trials
                }
            else:
                logger.warning(f"ClinicalTrialsTool: API returned status code {response.status_code}.")
        except Exception as e:
            logger.error(f"ClinicalTrialsTool: API request failed due to: {e}. Attempting local fallback.")

        # Local fallback if API fails or is offline
        return self._local_fallback(clean_query)

    def _local_fallback(self, clean_query: str) -> dict:
        logger.info(f"ClinicalTrialsTool: Checking local fallback for '{clean_query}'...")
        
        # Simple offline mock database for demonstration/testing fallback
        mock_db = {
            "diabetes": [
                {
                    "title": "A Study of Metformin in Patients With Type 2 Diabetes",
                    "phase": "PHASE3",
                    "status": "COMPLETED",
                    "sponsor": "National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK)"
                },
                {
                    "title": "Efficacy and Safety of a New Insulin Pump System in Type 1 Diabetes",
                    "phase": "PHASE4",
                    "status": "RECRUITING",
                    "sponsor": "Medtronic Diabetes"
                }
            ],
            "hypertension": [
                {
                    "title": "Evaluation of Blood Pressure Control in Hypertensive Patients",
                    "phase": "PHASE2",
                    "status": "ACTIVE_NOT_RECRUITING",
                    "sponsor": "Cardiovascular Research Foundation"
                }
            ],
            "malaria": [
                {
                    "title": "Efficacy Study of a Novel Antimalarial Combination Therapy",
                    "phase": "PHASE2",
                    "status": "RECRUITING",
                    "sponsor": "Medicines for Malaria Venture"
                }
            ]
        }

        # Try to find a match in our mock database
        matched_trials = []
        for key, trials in mock_db.items():
            if key in clean_query or clean_query in key:
                matched_trials = trials
                break

        if matched_trials:
            logger.info(f"ClinicalTrialsTool: Found local fallback match for '{clean_query}'.")
            return {
                "source": "Local Fallback Database",
                "query": clean_query.capitalize(),
                "trials": matched_trials
            }
        
        logger.warning(f"ClinicalTrialsTool: No clinical trials found for '{clean_query}'.")
        return {
            "source": "None",
            "query": clean_query.capitalize(),
            "trials": []
        }
