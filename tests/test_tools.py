import os
import json
import pytest
from unittest.mock import patch, MagicMock

# Set environment variables for testing before imports
os.environ["DATA_DIR"] = "data"
os.environ["REPORTS_DIR"] = "reports"
os.environ["MEMORY_FILE"] = "memory/test_memory.json"

from tools.fda_tool import FdaTool
from tools.pubchem_tool import PubChemTool
from tools.clinical_trials_tool import ClinicalTrialsTool
from memory.agent_memory import AgentMemory
from agents.pharma_agent import PharmaAgent

@pytest.fixture
def clean_memory():
    # Remove test memory file if it exists
    test_file = "memory/test_memory.json"
    if os.path.exists(test_file):
        os.remove(test_file)
    memory = AgentMemory()
    yield memory
    if os.path.exists(test_file):
        os.remove(test_file)

def test_fda_tool_local_fallback():
    # Test local database query for 'aspirin' when network fails
    tool = FdaTool()
    
    with patch("requests.get", side_effect=Exception("Network failure")):
        result = tool.run("aspirin")
        
    assert result["source"] == "Local Fallback Database"
    assert result["brand_name"] == "Aspirin"
    assert "Acetylsalicylic Acid" in result["generic_name"]
    assert "Pain reliever" in result["purpose"]

def test_pubchem_tool_local_fallback():
    # Test local database query for 'ibuprofen' when network fails
    tool = PubChemTool()
    
    with patch("requests.get", side_effect=Exception("Network failure")):
        result = tool.run("ibuprofen")
        
    assert result["source"] == "Local Fallback Database"
    assert result["cid"] == 3672
    assert "C13H18O2" in result["molecular_formula"]

def test_agent_memory(clean_memory):
    memory = clean_memory
    assert len(memory.get_history()) == 0
    
    memory.add_query("FDA Lookup", "aspirin")
    history = memory.get_history()
    assert len(history) == 1
    assert history[0]["type"] == "FDA Lookup"
    assert history[0]["term"] == "aspirin"
    
    # Reload from disk
    new_memory = AgentMemory()
    assert len(new_memory.get_history()) == 1
    assert new_memory.get_history()[0]["term"] == "aspirin"
    
    # Clear memory
    new_memory.clear_memory()
    assert len(new_memory.get_history()) == 0

def test_pharma_agent_report_generation():
    agent = PharmaAgent()
    
    # Mocking tool calls to avoid network dependency in agent report generation test
    with patch.object(FdaTool, "run") as mock_fda, patch.object(PubChemTool, "run") as mock_pubchem:
        mock_fda.return_value = {
            "source": "Mock FDA",
            "brand_name": "Aspirin",
            "generic_name": "Acetylsalicylic Acid",
            "active_ingredient": "Aspirin 325 mg",
            "purpose": "Pain reliever",
            "indications_and_usage": "Use for pain.",
            "warnings": "Do not exceed dosage.",
            "side_effects": "Stomach pain.",
            "dosage_and_administration": "Take 1 tablet."
        }
        
        mock_pubchem.return_value = {
            "source": "Mock PubChem",
            "cid": 2244,
            "iupac_name": "2-acetyloxybenzoic acid",
            "molecular_formula": "C9H8O4",
            "molecular_weight": "180.16 g/mol",
            "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",
            "chemical_class": "Salicylates"
        }
        
        result = agent.run("report:aspirin")
        
        assert result["status"] == "Success"
        assert os.path.exists(result["filepath"])
        assert "aspirin_report.md" in result["filename"]
        assert "Aspirin" in result["report_content"]
        
        # Cleanup report file
        if os.path.exists(result["filepath"]):
            os.remove(result["filepath"])

def test_clinical_trials_tool_api():
    # Test successful API query for ClinicalTrialsTool
    tool = ClinicalTrialsTool()
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "studies": [
            {
                "protocolSection": {
                    "identificationModule": {
                        "officialTitle": "Official Diabetes Trial Title",
                        "briefTitle": "Brief Diabetes Trial"
                    },
                    "designModule": {
                        "phases": ["PHASE3"]
                    },
                    "statusModule": {
                        "overallStatus": "RECRUITING"
                    },
                    "sponsorCollaboratorsModule": {
                        "leadSponsor": {
                            "name": "Test University"
                        }
                    }
                }
            }
        ]
    }
    
    with patch("requests.get", return_value=mock_response) as mock_get:
        result = tool.run("diabetes")
        mock_get.assert_called_once_with(
            "https://clinicaltrials.gov/api/v2/studies",
            params={"query.cond": "diabetes", "pageSize": 5},
            timeout=10
        )
        
    assert result["source"] == "ClinicalTrials.gov API"
    assert len(result["trials"]) == 1
    assert result["trials"][0]["title"] == "Official Diabetes Trial Title"
    assert result["trials"][0]["phase"] == "PHASE3"
    assert result["trials"][0]["status"] == "RECRUITING"
    assert result["trials"][0]["sponsor"] == "Test University"

def test_clinical_trials_tool_local_fallback():
    # Test local fallback query for 'diabetes' when network fails
    tool = ClinicalTrialsTool()
    
    with patch("requests.get", side_effect=Exception("Network failure")):
        result = tool.run("diabetes")
        
    assert result["source"] == "Local Fallback Database"
    assert len(result["trials"]) > 0
    assert any("Metformin" in t["title"] for t in result["trials"])

def test_clinical_trials_tool_fallback_none():
    # Test when disease is not in API or mock fallback
    tool = ClinicalTrialsTool()
    
    with patch("requests.get", side_effect=Exception("Network failure")):
        result = tool.run("unknown_disease_xyz")
        
    assert result["source"] == "None"
    assert len(result["trials"]) == 0

def test_pharma_agent_clinical_trials_csv():
    # Test that the agent handles clinical_trials query, fetches, and saves to CSV
    agent = PharmaAgent()
    
    with patch.object(ClinicalTrialsTool, "run") as mock_trials:
        mock_trials.return_value = {
            "source": "Mock ClinicalTrials.gov API",
            "query": "diabetes",
            "trials": [
                {
                    "title": "A Mock Study on Diabetes",
                    "phase": "PHASE3",
                    "status": "RECRUITING",
                    "sponsor": "Mock Pharma Corp"
                }
            ]
        }
        
        result = agent.run("clinical_trials:diabetes")
        
        assert result["status"] == "Success"
        assert os.path.exists(result["filepath"])
        assert "clinical_trials_diabetes.csv" in result["filename"]
        
        import csv
        with open(result["filepath"], "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            
        assert len(rows) == 1
        assert rows[0]["title"] == "A Mock Study on Diabetes"
        assert rows[0]["phase"] == "PHASE3"
        assert rows[0]["status"] == "RECRUITING"
        assert rows[0]["sponsor"] == "Mock Pharma Corp"
        
        # Cleanup
        if os.path.exists(result["filepath"]):
            os.remove(result["filepath"])

def test_clinical_trial_agent():
    import csv
    from agents.clinical_trial_agent import ClinicalTrialAgent
    agent = ClinicalTrialAgent()
    
    with patch("agents.clinical_trial_agent.fetch_and_save_trials") as mock_fetch:
        def mock_fetch_impl(disease):
            os.makedirs("data", exist_ok=True)
            with open("data/trials.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["disease", "nct_id", "study_title", "status", "phase", "sponsor", "source", "retrieved_date"])
                writer.writeheader()
                writer.writerow({
                    "disease": "diabetes",
                    "nct_id": "NCT12345",
                    "study_title": "Test Title",
                    "status": "COMPLETED",
                    "phase": "PHASE3",
                    "sponsor": "Test Sponsor",
                    "source": "Mock API",
                    "retrieved_date": "2026-06-20"
                })
        mock_fetch.side_effect = mock_fetch_impl
        
        result = agent.run("diabetes")
        
        assert result["disease_searched"] == "diabetes"
        assert result["total_records_found"] == 1
        assert result["top_study_title"] == "Test Title"
        assert result["top_sponsor"] == "Test Sponsor"
        assert result["csv_output_path"] == os.path.join("data", "trials.csv")


