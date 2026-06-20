# Capstone Gap Analysis: Pharma Intelligence Agent

This report evaluates the current codebase of the **Pharma Intelligence Agent** project against the target capstone architecture. It identifies fully implemented, partially implemented, and missing components, highlights logic/file duplication, and outlines steps required to achieve production readiness, Agent Development Kit (ADK) alignment, and Model Context Protocol (MCP) compatibility.

---

## 1. Executive Summary

The current implementation of the Pharma Intelligence Agent is a functional CLI application that integrates openFDA, PubChem, and ClinicalTrials.gov search capabilities. However, there is a significant divergence between two parallel orchestration structures in the codebase:
1. **Single-Agent/Tool Model**: `PharmaAgent` in [pharma_agent.py](file:///c:/Users/nmano/pharma-intelligence-agent/agents/pharma_agent.py) registering and running tools directly via `app.py`.
2. **Multi-Agent Orchestrator Model**: `PlannerAgent` in [planner_agent.py](file:///c:/Users/nmano/pharma-intelligence-agent/agents/planner_agent.py) orchestrating sub-agents (`ClinicalTrialAgent` and `FDAApprovalAgent`).

This architectural split has led to logic duplication, inconsistent schemas, and unused modules. The app also lacks integration for evaluation reports, interactive dashboards, dynamic memory, and standard ADK/MCP protocols.

---

## 2. Implementation Status Dashboard

The table below summarizes the status of the key capstone architectural components:

| Component / Feature | Current File(s) | Status | Key Architectural Gaps |
| :--- | :--- | :---: | :--- |
| **Planner Agent** | [agents/planner_agent.py](file:///c:/Users/nmano/pharma-intelligence-agent/agents/planner_agent.py) | **Partially Implemented** | Not integrated into main `app.py` CLI; tight coupling of sub-agents; fragile text-splitting query parser. |
| **Clinical Trial Agent** | [agents/clinical_trial_agent.py](file:///c:/Users/nmano/pharma-intelligence-agent/agents/clinical_trial_agent.py) | **Partially Implemented** | Duplicated logic between `clinicaltrials_tool.py` and `clinical_trials_tool.py`; does not register/use tools via the `BaseAgent` framework. |
| **FDA Approval Agent** | [agents/fda_approval_agent.py](file:///c:/Users/nmano/pharma-intelligence-agent/agents/fda_approval_agent.py) | **Partially Implemented** | Duplicated logic with `FdaTool` class; directly imports helper functions instead of using registered tools. |
| **Evaluator Agent** | [agents/evaluator_agent.py](file:///c:/Users/nmano/pharma-intelligence-agent/agents/evaluator_agent.py) | **Partially Implemented** | Standalone script; not integrated into the main `app.py` CLI menu; relies on hardcoded static CSV paths. |
| **Memory** | [memory/agent_memory.py](file:///c:/Users/nmano/pharma-intelligence-agent/memory/agent_memory.py)<br>[tools/memory_tool.py](file:///c:/Users/nmano/pharma-intelligence-agent/tools/memory_tool.py) | **Partially Implemented** | Used only at CLI menu level; agents are stateless; `tools/memory_tool.py` is completely unused. |
| **Logging** | [logs/agent.log](file:///c:/Users/nmano/pharma-intelligence-agent/logs/agent.log)<br>[tools/logger_tool.py](file:///c:/Users/nmano/pharma-intelligence-agent/tools/logger_tool.py) | **Partially Implemented** | Custom `logger_tool.py` is unused; standard Python logging lacks execution tracing and structured JSON formatting. |
| **Dashboard** | [tools/dashboard_data_generator.py](file:///c:/Users/nmano/pharma-intelligence-agent/tools/dashboard_data_generator.py)<br>[tools/simple_dashboard.py](file:///c:/Users/nmano/pharma-intelligence-agent/tools/simple_dashboard.py) | **Partially Implemented** | Not integrated into `app.py` or planner runs; dashboard is a static matplotlib PNG; no interactive web app (Vite/Streamlit). |
| **Multi-agent Orchestration** | [agents/planner_agent.py](file:///c:/Users/nmano/pharma-intelligence-agent/agents/planner_agent.py) | **Partially Implemented** | Runs synchronously and sequentially; lacks async/parallel execution, message-passing, or unified orchestration models. |
| **ADK Compatibility** | [agents/base_agent.py](file:///c:/Users/nmano/pharma-intelligence-agent/agents/base_agent.py)<br>[tools/base_tool.py](file:///c:/Users/nmano/pharma-intelligence-agent/tools/base_tool.py) | **Missing / Mocked** | Uses custom classes written from scratch; doesn't import or extend official Antigravity/ADK library primitives. |
| **MCP Readiness** | None | **Missing** | No Model Context Protocol server or client implementation; tools/agents are not exposed as MCP endpoints. |

---

## 3. Detailed Component Review & Gap Analysis

### 3.1 Planner Agent
The `PlannerAgent` coordinates the clinical trial search, FDA approvals lookup, and executive report generation.
* **Intended Architecture**: Acts as the master orchestrator, resolving user queries dynamically, delegating tasks to specialist agents, and generating synthesized briefs.
* **Current Implementation**:
  - Resides in [agents/planner_agent.py](file:///c:/Users/nmano/pharma-intelligence-agent/agents/planner_agent.py).
  - Sequentially runs `ClinicalTrialAgent` and `FDAApprovalAgent`, then calls `generate_report()`.
* **Gaps Identified**:
  - **CLI Disconnection**: The main CLI `app.py` completely bypasses `PlannerAgent` and relies on `PharmaAgent` instead.
  - **Fragile Parsing**: Query parsing is restricted to a space-separated string `"<disease> <drug>"`. Multi-word names (e.g., "type 2 diabetes", "metformin hcl") cause index errors or incorrect queries.
  - **Tool Bypass**: It instantiates agents directly and calls `.run()` instead of using the inherited `register_tool` or an agent-registry paradigm.

### 3.2 Clinical Trial Agent
Queries ClinicalTrials.gov for research studies.
* **Intended Architecture**: A specialized agent wrapping a clinical trials search tool to return standardized study listings.
* **Current Implementation**:
  - Resides in [agents/clinical_trial_agent.py](file:///c:/Users/nmano/pharma-intelligence-agent/agents/clinical_trial_agent.py).
  - Directly runs `fetch_and_save_trials()` from [tools/clinicaltrials_tool.py](file:///c:/Users/nmano/pharma-intelligence-agent/tools/clinicaltrials_tool.py).
* **Gaps Identified**:
  - **Logic & File Duplication**: 
    - `PharmaAgent` registers `ClinicalTrialsTool` ([tools/clinical_trials_tool.py](file:///c:/Users/nmano/pharma-intelligence-agent/tools/clinical_trials_tool.py)) which saves search-specific files to `clinical_trials_{disease}.csv`.
    - `ClinicalTrialAgent` calls `fetch_and_save_trials` ([tools/clinicaltrials_tool.py](file:///c:/Users/nmano/pharma-intelligence-agent/tools/clinicaltrials_tool.py)) which saves to `trials.csv`.
    This creates file-naming conflicts, data overwriting issues, and separate columns (`title` vs. `study_title`).

### 3.3 FDA Approval Agent
Retrieves drug label and indications data from openFDA.
* **Intended Architecture**: A specialist agent mapping FDA label API results to a standardized schema.
* **Current Implementation**:
  - Resides in [agents/fda_approval_agent.py](file:///c:/Users/nmano/pharma-intelligence-agent/agents/fda_approval_agent.py).
  - Runs `fetch_and_save_fda_labels()` from [tools/fda_tool.py](file:///c:/Users/nmano/pharma-intelligence-agent/tools/fda_tool.py).
* **Gaps Identified**:
  - **Orchestration Duplication**: Dual implementation where `PharmaAgent` uses `FdaTool` class (returning JSON dictionaries) and `FDAApprovalAgent` uses `fetch_and_save_fda_labels` (writing to `fda_results.csv`).
  - **Static Schema**: It hardcodes extraction logic rather than allowing dynamic schema mapping depending on the query context.

### 3.4 Evaluator Agent
Validates outputs and checks data quality.
* **Intended Architecture**: Assesses the generated data files for columns, record presence, citations, and duplicates, producing an automated data quality scorecard.
* **Current Implementation**:
  - Resides in [agents/evaluator_agent.py](file:///c:/Users/nmano/pharma-intelligence-agent/agents/evaluator_agent.py).
  - Rates data quality out of 100 and outputs a markdown report at `reports/evaluation_results.md`.
* **Gaps Identified**:
  - **No CLI Integration**: Entirely absent from the CLI menu in `app.py`. A user cannot evaluate run outputs interactively.
  - **Rigid File Binding**: Bypasses memory or agent messaging, looking specifically for hardcoded static file paths `trials.csv` and `fda_results.csv`.

### 3.5 Memory
Persists query context and history.
* **Intended Architecture**: Agents retrieve previous steps, maintain session variables, and store cross-agent state.
* **Current Implementation**:
  - CLI `app.py` logs query history to `memory/chat_memory.json` using `AgentMemory`.
  - [tools/memory_tool.py](file:///c:/Users/nmano/pharma-intelligence-agent/tools/memory_tool.py) defines functions for `session_memory.json`.
* **Gaps Identified**:
  - **Agent Statelessness**: Agents do not have access to or reference the memory file. They process each run in isolation.
  - **Dead Code**: `tools/memory_tool.py` is not imported or used anywhere except in its own unit tests.

### 3.6 Logging
Captures execution runs and errors.
* **Intended Architecture**: Detailed agent trace logging with correlation IDs tracking orchestration pipeline flows.
* **Current Implementation**:
  - Standard python `logging` writes to `logs/agent.log`.
  - [tools/logger_tool.py](file:///c:/Users/nmano/pharma-intelligence-agent/tools/logger_tool.py) writes pipe-delimited strings to `logs/agent_logs.txt`.
* **Gaps Identified**:
  - **Dead Code**: `tools/logger_tool.py` is entirely unused by any agent or CLI script.
  - **No Traceability**: Logs do not trace execution flow between the orchestrator and sub-agents.

### 3.7 Dashboard
Summarizes data metrics visually.
* **Intended Architecture**: An interactive dashboard showing metrics, drug comparisons, and study timelines.
* **Current Implementation**:
  - [tools/dashboard_data_generator.py](file:///c:/Users/nmano/pharma-intelligence-agent/tools/dashboard_data_generator.py) aggregates CSV data.
  - [tools/simple_dashboard.py](file:///c:/Users/nmano/pharma-intelligence-agent/tools/simple_dashboard.py) draws a matplotlib bar chart at `reports/dashboard_chart.png`.
* **Gaps Identified**:
  - **Unintegrated Dashboard**: Neither tool is referenced or triggered by `app.py` or `PlannerAgent`.
  - **Static PNG**: Not an interactive web dashboard (no Streamlit or Vite app), violating requirements for a dynamic frontend dashboard experience.

### 3.8 Multi-agent Orchestration
Coordinates concurrent agent workflows.
* **Intended Architecture**: Asynchronous/parallel execution of child tasks, unified agent registries, and state/message passing.
* **Current Implementation**:
  - Synchronous procedurally called execution block in `PlannerAgent`.
* **Gaps Identified**:
  - **Sequential Block**: FDA lookup and Clinical trials query run sequentially, even though they are completely independent and could run in parallel.
  - **Conflict of Orchestrators**: Dual models (`PharmaAgent` acting as tool orchestrator vs. `PlannerAgent` acting as agent orchestrator) fragment the code's design.

### 3.9 ADK Compatibility
Integrates Google Antigravity Agent Development Kit standards.
* **Intended Architecture**: Extends formal ADK primitives (`Agent`, `Tool`, `Runner`, `Context`) to manage runtime cycles.
* **Current Implementation**:
  - Custom classes `BaseAgent` and `BaseTool` defined from scratch.
* **Gaps Identified**:
  - **ADK Divergence**: The custom base classes do not use standard ADK decorator interfaces or configuration schemas, limiting compatibility.

### 3.10 MCP Readiness
Model Context Protocol integration.
* **Intended Architecture**: Exposes lookup tools and report generation services as MCP endpoints to enable discovery by LLM clients.
* **Current Implementation**:
  - None.
* **Gaps Identified**:
  - **Lack of Protocol Interface**: No MCP server is defined, meaning tools cannot be dynamically bound or discovered.

---

## 4. Remediation & Action Plan

To resolve these architectural issues, the following refactoring roadmap is recommended:

1. **Unify Orchestration**: Update `app.py` to use `PlannerAgent` for orchestrating clinical trial search, FDA lookup, and report generation rather than calling tools via `PharmaAgent` directly.
2. **Eliminate Duplication**: Merge `clinicaltrials_tool.py` and `clinical_trials_tool.py` to have a single, unified clinical trials search class. Standardize on the columns (`disease`, `nct_id`, `study_title`, `status`, `phase`, `sponsor`, `source`, `retrieved_date`).
3. **Integrate Evaluator and Dashboard**: Add menu options in the CLI interface to run data validation and generate/display dashboard analytics.
4. **Connect Memory and Logging**: Import and use `tools/memory_tool.py` and `tools/logger_tool.py` across all agents to maintain persistent states and structured pipeline tracking.
5. **Interactive Dashboard**: Transition from a static matplotlib PNG to a lightweight, dynamic web application (e.g. Streamlit or React+Vite app) that interfaces with `data/dashboard_data.csv`.
6. **ADK and MCP Compliance**: Refactor custom base classes to extend standard Antigravity primitives, and prepare an MCP server layer to expose tools.
