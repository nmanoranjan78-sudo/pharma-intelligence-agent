import os
import csv
import datetime
import logging
from agents.base_agent import BaseAgent
from tools.fda_tool import FdaTool
from tools.pubchem_tool import PubChemTool
from tools.clinical_trials_tool import ClinicalTrialsTool

logger = logging.getLogger("pharma_agent.agents.pharma_agent")

class PharmaAgent(BaseAgent):
    """Orchestrator Agent for Pharmaceutical and Chemical Intelligence."""

    def __init__(self):
        super().__init__(
            name="Pharma Intelligence Agent",
            role="Specialist in synthesising drug labels, active ingredients, and chemical properties."
        )
        # Instantiate and register tools
        self.register_tool(FdaTool())
        self.register_tool(PubChemTool())
        self.register_tool(ClinicalTrialsTool())

    def run(self, query: str) -> dict:
        """Process a query by routing it to the appropriate analysis flow.

        Query formats expected:
        - "report:<drug_name>" -> Generate full report.
        - "fda:<drug_name>" -> Fetch only drug label.
        - "pubchem:<compound_name>" -> Fetch only chemical properties.
        """
        self.logger.info(f"PharmaAgent received query: '{query}'")
        
        if query.startswith("report:"):
            target = query.replace("report:", "", 1).strip()
            return self.generate_report(target)
        elif query.startswith("fda:"):
            target = query.replace("fda:", "", 1).strip()
            return self.execute_tool("openFDA Drug Label Lookup", target)
        elif query.startswith("pubchem:"):
            target = query.replace("pubchem:", "", 1).strip()
            return self.execute_tool("PubChem Compound Lookup", target)
        elif query.startswith("clinical_trials:"):
            target = query.replace("clinical_trials:", "", 1).strip()
            return self.save_clinical_trials(target)
        else:
            # Default fallback: try to run both and return combined dictionary
            fda_res = self.execute_tool("openFDA Drug Label Lookup", query)
            pub_res = self.execute_tool("PubChem Compound Lookup", query)
            return {
                "drug_info": fda_res,
                "chemical_info": pub_res
            }

    def save_clinical_trials(self, disease: str) -> dict:
        """Queries ClinicalTrials.gov API for studies and saves them to a CSV file.

        Args:
            disease (str): Disease name or condition (e.g., "diabetes").

        Returns:
            dict: Status, filepath, filename, and list of trials.
        """
        logger.info(f"PharmaAgent: Searching clinical trials and saving to CSV for '{disease}'...")
        
        # 1. Fetch trials data
        result = self.execute_tool("ClinicalTrials Search Tool", disease)
        trials = result.get("trials", [])
        source = result.get("source", "Unknown")

        # 2. Setup path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.getenv("DATA_DIR", "data")
        if not os.path.isabs(data_dir):
            data_dir = os.path.join(project_root, data_dir)
        os.makedirs(data_dir, exist_ok=True)

        filename = f"clinical_trials_{disease.lower().replace(' ', '_')}.csv"
        filepath = os.path.join(data_dir, filename)

        # 3. Write CSV file
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["title", "phase", "status", "sponsor"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for trial in trials:
                    writer.writerow({
                        "title": trial.get("title", ""),
                        "phase": trial.get("phase", ""),
                        "status": trial.get("status", ""),
                        "sponsor": trial.get("sponsor", "")
                    })
            logger.info(f"PharmaAgent: Successfully wrote clinical trials to '{filepath}'.")
            status = "Success"
        except Exception as e:
            logger.error(f"PharmaAgent: Failed to write CSV file: {e}")
            status = f"Failed ({e})"

        return {
            "status": status,
            "source": source,
            "filepath": filepath,
            "filename": filename,
            "trials": trials
        }

    def generate_report(self, drug_name: str) -> dict:
        """Executes both FDA and PubChem tools, synthesizes the results, and writes a Markdown report.

        Args:
            drug_name (str): The name of the drug.

        Returns:
            dict: Status, report file path, and report contents.
        """
        logger.info(f"PharmaAgent: Generating comprehensive report for '{drug_name}'...")
        
        # 1. Fetch data from both tools
        fda_info = self.execute_tool("openFDA Drug Label Lookup", drug_name)
        pub_info = self.execute_tool("PubChem Compound Lookup", drug_name)

        # 2. Synthesize Markdown
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_md = f"""# Pharma Intelligence Report: {fda_info.get('brand_name', drug_name.capitalize())}

**Generated on:** {timestamp}
**Data Sources:** {fda_info.get('source', 'Unknown')} & {pub_info.get('source', 'Unknown')}

---

## 1. Clinical & FDA Label Information

- **Brand Name:** {fda_info.get('brand_name')}
- **Generic Name:** {fda_info.get('generic_name')}
- **Active Ingredient:** {fda_info.get('active_ingredient')}
- **Therapeutic Purpose:** {fda_info.get('purpose')}

### Indications & Usage
{fda_info.get('indications_and_usage')}

### Warnings & Contraindications
> [!WARNING]
> {fda_info.get('warnings')}

### Common Side Effects
{fda_info.get('side_effects')}

### Dosage & Administration
{fda_info.get('dosage_and_administration')}

---

## 2. Chemical & Molecular Properties

- **Chemical IUPAC Name:** {pub_info.get('iupac_name')}
- **Molecular Formula:** {pub_info.get('molecular_formula')}
- **Molecular Weight:** {pub_info.get('molecular_weight')}
- **PubChem CID:** {pub_info.get('cid')}
- **Chemical Class:** {pub_info.get('chemical_class')}

### SMILES Structure
```text
{pub_info.get('smiles')}
```

---

## 3. Agent Synthesis & Summary

The active pharmaceutical ingredient **{fda_info.get('generic_name')}** (Molecular Formula: `{pub_info.get('molecular_formula')}`) is formulated as **{fda_info.get('brand_name')}**. It functions primarily as a **{fda_info.get('purpose')}**. 

*This report was automatically synthesized by the Pharma Intelligence Agent.*
"""

        # 3. Save report to folder
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        reports_dir = os.getenv("REPORTS_DIR", "reports")
        if not os.path.isabs(reports_dir):
            reports_dir = os.path.join(project_root, reports_dir)
        os.makedirs(reports_dir, exist_ok=True)
        
        filename = f"{drug_name.lower().replace(' ', '_')}_report.md"
        filepath = os.path.join(reports_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report_md)
            logger.info(f"PharmaAgent: Successfully wrote report to '{filepath}'.")
            status = "Success"
        except Exception as e:
            logger.error(f"PharmaAgent: Failed to write report file: {e}")
            status = f"Failed ({e})"

        return {
            "status": status,
            "filepath": filepath,
            "filename": filename,
            "report_content": report_md
        }
