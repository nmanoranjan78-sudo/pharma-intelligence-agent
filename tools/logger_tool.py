import os
from datetime import datetime

def log_event(agent_name, task, status, message):
    """
    Logs an agent event to a text file.
    
    Parameters:
        agent_name (str): Name of the agent.
        task (str): The task being performed.
        status (str): The status of the task (e.g., SUCCESS, FAILED, RUNNING).
        message (str): A descriptive message or detail about the event.
    """
    # Define the directory and file path
    log_dir = "logs"
    log_file = os.path.join(log_dir, "agent_logs.txt")
    
    # Ensure the log directory exists (creates it if missing)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # Get the current date and time formatted nicely (YYYY-MM-DD HH:MM:SS)
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Construct the log line using pipe delimiters for clarity and easy parsing
    log_line = f"{date_time} | {agent_name} | {task} | {status} | {message}\n"
    
    # Append the log line to the file
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(log_line)
        
    print(f"[Logger] Event logged successfully: {status} - {message}")

if __name__ == "__main__":
    # Test block to verify logging works
    print("Testing logger_tool...")
    
    # Log a few sample events
    log_event(
        agent_name="Clinical Trial Agent", 
        task="Fetch Trials", 
        status="SUCCESS", 
        message="Successfully fetched trials for diabetes"
    )
    
    log_event(
        agent_name="FDA Approval Agent", 
        task="Query Drug Labels", 
        status="SUCCESS", 
        message="Found 5 FDA approvals for Aspirin"
    )
    
    log_event(
        agent_name="Evaluator Agent", 
        task="Assess Data Quality", 
        status="FAILED", 
        message="Missing required FDA data file"
    )
    
    # Read and print the last few lines of the log file to confirm it wrote correctly
    log_file_path = os.path.join("logs", "agent_logs.txt")
    if os.path.exists(log_file_path):
        print("\n--- Recent Logs in logs/agent_logs.txt ---")
        with open(log_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[-3:]:  # Print the last 3 logged events
                print(line.strip())
