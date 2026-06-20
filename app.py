import os
import sys
import logging
from dotenv import load_dotenv

# Load env variables before other imports
load_dotenv()

# Setup logging
log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/agent.log", encoding="utf-8"),
    ]
)

# Rich imports
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown
from rich.prompt import Prompt

# Project imports
from agents.planner_agent import PlannerAgent

console = Console()

def print_welcome():
    title = Text("PHARMA INTELLIGENCE AGENT", style="bold cyan")
    subtitle = Text("Advanced Pharmaceutical & Chemical Research Engine", style="italic green")
    welcome_panel = Panel(
        Text.assemble(title, "\n", subtitle),
        subtitle="v1.0.0",
        border_style="cyan",
        expand=False
    )
    console.print("\n")
    console.print(welcome_panel)

def main():
    print_welcome()
    
    # Prompt the user for disease and drug
    disease = Prompt.ask("[bold cyan]Enter disease or condition to search (e.g. diabetes)[/bold cyan]").strip()
    drug = Prompt.ask("[bold cyan]Enter drug name to search (e.g. semaglutide)[/bold cyan]").strip()
    
    if not disease or not drug:
        console.print("[bold red]Error: Both disease and drug names are required.[/bold red]")
        sys.exit(1)
        
    console.print(f"\n[bold yellow]Starting research orchestration for disease: '{disease}' and drug: '{drug}'...[/bold yellow]")
    
    # Instantiate PlannerAgent and run end-to-end workflow
    planner = PlannerAgent()
    
    with console.status("[bold green]Executing Pharma Intelligence pipeline...[/bold green]"):
        results = planner.run(f"{disease} {drug}")
        
    # Display a structured summary table using rich
    console.print("\n")
    
    summary_table = Table(show_header=True, header_style="bold magenta", border_style="cyan")
    summary_table.add_column("Metric / Artifact", style="bold cyan")
    summary_table.add_column("Value / Output Path", style="white")
    
    summary_table.add_row("Disease Query", results["disease_query"])
    summary_table.add_row("Drug Query", results["drug_query"])
    summary_table.add_row("Clinical Trials Records Found", str(results["trials_records_found"]))
    summary_table.add_row("FDA Drug Label Records Found", str(results["fda_records_found"]))
    summary_table.add_row("Executive Briefing Generation", results["report_generation_status"])
    summary_table.add_row("Executive Briefing File", f"[link=file:///{results['report_output_path'].replace('\\', '/')}]" + results["report_output_path"] + "[/link]")
    summary_table.add_row("Dashboard Data File", f"[link=file:///{results['dashboard_data_path'].replace('\\', '/')}]" + results["dashboard_data_path"] + "[/link]")
    summary_table.add_row("Dashboard Chart Image", f"[link=file:///{results['dashboard_chart_path'].replace('\\', '/')}]" + results["dashboard_chart_path"] + "[/link]")
    
    # Highlight score based on pass/fail status
    score_color = "green" if results["evaluator_status"] == "PASS" else "red"
    summary_table.add_row("Evaluator Score", f"[{score_color}]{results['evaluator_score']}/100 ({results['evaluator_status']})[/{score_color}]")
    summary_table.add_row("Evaluator Report File", f"[link=file:///{results['evaluator_report_path'].replace('\\', '/')}]" + results["evaluator_report_path"] + "[/link]")
    
    summary_panel = Panel(
        summary_table,
        title="Pipeline Execution Summary",
        border_style="green",
        expand=False
    )
    console.print(summary_panel)
    console.print("\n[bold green][SUCCESS] All steps completed successfully. Thank you for using Pharma Intelligence Agent![/bold green]\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Application interrupted. Exiting.[/bold yellow]\n")
        sys.exit(0)
