# Sprint Analysis Dashboard

A Streamlit dashboard for analyzing quarterly sprint data from Linear, focusing on team performance metrics and developer insights.

## Overview

This project provides visual analytics and insights for Q4 2024 sprint data, including:
- Task distribution across sprints
- Team member workload analysis
- Priority distribution
- Individual developer performance metrics

Link to Dashboard -> https://q4-2024-analysis-menu-squad.streamlit.app/

## Prerequisites

- Python 3.9+
- pip
- virtualenv (recommended)

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install requirements:
```bash
pip install requirements.txt
```

3. Prepare the data:
   - Export sprint data from Linear for each sprint
   - Combine the CSV files into a single file named `menu_q4_sprints.csv`
   - Place the CSV file in the same directory as the script

## Running the Dashboard

```bash
streamlit run q4_sprint_analysis.py
```

## Data Structure

The input CSV should contain the following columns:
- ID: Task identifier
- Title: Task description
- Status: Current status
- Estimate: Story points
- Priority: Task priority
- Labels: Task labels/tags
- Cycle Name: Sprint name
- Created: Creation timestamp
- Completed: Completion timestamp
- Assignee: Team member email

## Features

- **Sprint Performance**: Visual breakdown of task types per sprint
- **Team Insights**: Workload distribution and priority analysis
- **Developer Deep Dive**: Individual performance metrics and task history

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License