import csv
import os
from datetime import datetime

def parse_sprint_file(input_filepath, output_filepath):
    with open(input_filepath, mode='r', encoding='utf-8') as infile, open(output_filepath, mode='a', encoding='utf-8', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = [
            "ID", "Team", "Title", "Description", "Status", "Estimate", "Priority", 
            "Cycle Name", "Cycle Start", "Cycle End", "Creator", "Assignee", "Labels", 
            "Created", "Updated", "Completed", "Archived"
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        # Write header only if the file is empty
        if os.stat(output_filepath).st_size == 0:
            writer.writeheader()

        for row in reader:
            writer.writerow({
                "ID": row.get("ID"),
                "Team": row.get("Team"),
                "Title": row.get("Title"),
                "Status": row.get("Status"),
                "Estimate": row.get("Estimate"),
                "Priority": row.get("Priority"),
                "Cycle Name": row.get("Cycle Name"),
                "Cycle Start": format_date(row.get("Cycle Start")),
                "Cycle End": format_date(row.get("Cycle End")),
                "Creator": row.get("Creator"),
                "Assignee": row.get("Assignee"),
                "Labels": row.get("Labels"),
                "Created": format_date(row.get("Created")),
                "Updated": format_date(row.get("Updated")),
                "Completed": format_date(row.get("Completed")),
                "Archived": row.get("Archived", "false")
            })

def format_date(date_str):
    if not date_str:
        return ""
    try:
        return datetime.fromisoformat(date_str.replace("Z", "")).strftime("%Y-%m-%d")
    except ValueError:
        return date_str

def process_all_sprints(input_dir, output_filepath):
    for filename in os.listdir(input_dir):
        if filename.endswith(".csv") and "issues" in filename.lower():
            print(filename, " is being processed...")
            input_filepath = os.path.join(input_dir, filename)
            parse_sprint_file(input_filepath, output_filepath)

if __name__ == "__main__":
    input_directory = "/Users/ray/Downloads/Q1_Sprints"
    output_file = "/Users/ray/work/q1-2025-analysis/menu_q1_sprints.csv"
    process_all_sprints(input_directory, output_file)
    print(f"Data has been parsed and saved to {output_file}")
