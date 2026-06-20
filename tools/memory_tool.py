import os
import json

def save_memory(file_name, data):
    """
    Saves data to a JSON file inside the 'memory/' directory.
    
    Parameters:
        file_name (str): The name of the memory file (e.g., 'session_memory.json').
        data (any): The data to save (usually a list or dict).
    """
    # Get the project root directory (parent of the tools directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Ensure memory directory is inside the project root
    memory_dir = os.path.join(project_root, "memory")
    
    # Create the memory directory if it doesn't exist
    if not os.path.exists(memory_dir):
        os.makedirs(memory_dir)
        
    # Extract only the filename to ensure it is saved inside the memory directory
    clean_name = os.path.basename(file_name)
    file_path = os.path.join(memory_dir, clean_name)
    
    # Write the data to a JSON file
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
        
    print(f"[Memory] Data saved successfully to: {file_path}")

def load_memory(file_name):
    """
    Loads data from a JSON file inside the 'memory/' directory.
    If the file does not exist, returns an empty list.
    
    Parameters:
        file_name (str): The name of the memory file (e.g., 'session_memory.json').
        
    Returns:
        list or dict: The loaded data, or an empty list if the file does not exist.
    """
    # Get the project root directory (parent of the tools directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Extract only the filename to ensure we load from the memory directory
    clean_name = os.path.basename(file_name)
    file_path = os.path.join(project_root, "memory", clean_name)
    
    # If the memory file does not exist, return an empty list
    if not os.path.exists(file_path):
        print(f"[Memory] File {file_path} not found. Returning empty list.")
        return []
        
    # Read and parse the JSON file
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        print(f"[Memory] Data loaded successfully from: {file_path}")
        return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"[Memory] Error loading memory from {file_path}: {e}. Returning empty list.")
        return []

if __name__ == "__main__":
    # Test block to verify memory tool functionality
    print("Testing memory_tool...")
    
    # Define test file and sample data
    test_file = "session_memory.json"
    sample_data = [
        {"agent": "Clinical Trial Agent", "status": "SUCCESS", "last_run": "2026-06-20 16:15:00"},
        {"agent": "FDA Approval Agent", "status": "SUCCESS", "last_run": "2026-06-20 16:58:00"}
    ]
    
    # 1. Try to load non-existent memory file (should return empty list)
    print("\n--- Test 1: Load non-existent file ---")
    loaded_empty = load_memory(test_file)
    print(f"Loaded empty data: {loaded_empty}")
    
    # 2. Save sample data
    print("\n--- Test 2: Save memory data ---")
    save_memory(test_file, sample_data)
    
    # 3. Load the saved memory data
    print("\n--- Test 3: Load saved file ---")
    loaded_data = load_memory(test_file)
    print(f"Loaded data: {loaded_data}")
    
    # Verify the test output matches the input
    assert loaded_data == sample_data, "Error: Loaded data does not match saved data!"
    print("\n[Memory Tool Test] All tests passed successfully!")
