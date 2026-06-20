"""
Simple Dashboard Chart Generator

This beginner-friendly Python script reads combined pharma intelligence data from:
- data/dashboard_data.csv

And generates a simple bar chart comparing the number of records by record type:
- Saved to: reports/dashboard_chart.png

Requirements:
- pandas
- matplotlib
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

def generate_dashboard_chart(data_csv_path: str, output_image_path: str) -> None:
    """
    Reads the dashboard CSV data, counts occurrences of each record_type,
    generates a bar chart, and saves the chart as an image.
    
    Parameters:
        data_csv_path (str): Path to the dashboard_data.csv file.
        output_image_path (str): Path where the generated chart PNG will be saved.
    """
    print(f"Reading dashboard data from: {data_csv_path}")
    
    # Check if the data file exists
    if not os.path.exists(data_csv_path):
        print(f"ERROR: Data file not found at '{data_csv_path}'.")
        print("Please make sure you have generated the dashboard data first.")
        return
        
    try:
        # Load the dataset
        df = pd.read_csv(data_csv_path)
        
        # Verify the record_type column exists
        if 'record_type' not in df.columns:
            print("ERROR: 'record_type' column not found in the CSV file.")
            return
            
        # Count the frequency of each record type
        counts = df['record_type'].value_counts()
        print("Record Type Counts:")
        for record_type, count in counts.items():
            print(f" - {record_type}: {count}")
            
        # Create a new figure for plotting
        plt.figure(figsize=(8, 6))
        
        # Set up a professional, clean color palette (e.g., steel blue and soft orange/teal)
        colors = ['#4682B4', '#FFA07A', '#20B2AA', '#778899']
        
        # Plot the counts as a bar chart
        bar_colors = colors[:len(counts)]
        
        # Create the bar chart
        counts.plot(kind='bar', color=bar_colors, edgecolor='grey', width=0.6)
        
        # Add titles and labels as per the requirements
        plt.title('Pharma Intelligence Dashboard', fontsize=16, fontweight='bold', pad=15)
        plt.xlabel('Record Type', fontsize=12, labelpad=10)
        plt.ylabel('Count', fontsize=12, labelpad=10)
        
        # Rotate x-axis labels to make them readable
        plt.xticks(rotation=0, fontsize=10)
        plt.yticks(fontsize=10)
        
        # Add a light grid for readability (on y-axis only)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Adjust layout to make sure everything fits nicely
        plt.tight_layout()
        
        # Ensure target folder exists
        output_dir = os.path.dirname(output_image_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        # Save the figure
        plt.savefig(output_image_path, dpi=150)
        plt.close() # Close the figure to free up memory
        
        print(f"SUCCESS: Chart successfully saved to: {output_image_path}")
        
    except Exception as e:
        print(f"An error occurred while generating the dashboard: {e}")

if __name__ == "__main__":
    # Resolve absolute paths based on the location of this script
    # This script resides in tools/, so project root is one level up.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Define paths
    data_csv = os.path.join(project_root, "data", "dashboard_data.csv")
    output_png = os.path.join(project_root, "reports", "dashboard_chart.png")
    
    print("==================================================")
    print("Running Simple Dashboard Tool Test Block")
    print("==================================================")
    
    # Generate the chart
    generate_dashboard_chart(data_csv_path=data_csv, output_image_path=output_png)
    
    print("==================================================")
