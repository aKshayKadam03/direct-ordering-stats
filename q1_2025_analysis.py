import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

def load_data(file_path):
    try:
        # Read CSV with first row as header
        df = pd.read_csv(file_path, header=0)
        
        # Convert date columns safely
        date_columns = ['Created', 'Completed', 'Updated', 'Started']
        for col in date_columns:
            try:
                df[col] = pd.to_datetime(df[col], format='ISO8601', errors='coerce')
            except Exception as e:
                print(f"Error converting {col}: {e}")
                df[col] = pd.NaT
        
        # Calculate cycle time only for completed items
        df['Cycle Time'] = None
        mask = ~(df['Created'].isna() | df['Completed'].isna())
        df.loc[mask, 'Cycle Time'] = (df.loc[mask, 'Completed'] - df.loc[mask, 'Created']).dt.total_seconds() / (24 * 60 * 60)

        return df
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        return pd.DataFrame()  # Return an empty DataFrame if file is not found

def preprocess_data(df):
    # Remove duplicate rows based on the 'ID' column, keeping the first occurrence
    df = df.drop_duplicates(subset='ID', keep='first')
    
    # Filter out tasks with the 'sub-task' label
    df = df[~df['Labels'].str.contains('sub-task', case=False, na=False)]
    
    return df

def sprint_velocity_trend(df):
    # Rename sprints for clarity
    df['Cycle Name'] = df['Cycle Name'].replace({
        'FEB-S-3': 'MAR-S-1',
        'FEB-S-4': 'MAR-S-2'
    })
    
    # Define the custom sprint order
    sprint_order = ['JAN-S-1', 'JAN-S-2', 'FEB-S-1', 'FEB-S-2', 'MAR-S-1', 'MAR-S-2']
    
    # Calculate tasks completed per sprint
    completed_tasks = df[df['Status'] == 'Done'].groupby('Cycle Name').size().reindex(sprint_order, fill_value=0)
    
    # Create a bar chart
    fig = px.bar(
        completed_tasks,
        title="Sprint Velocity (Tasks Completed per Sprint)",
        labels={'value': 'Tasks Completed', 'index': 'Sprint'},
        text=completed_tasks
    )
    fig.update_layout(xaxis_title="Sprint", yaxis_title="Tasks Completed")
    return fig

def bandwidth_efficiency(df):
    # Calculate actual efficiency in person weeks
    df['Estimate'] = pd.to_numeric(df['Estimate'], errors='coerce').fillna(0)
    actual_efficiency = df['Estimate'].sum() / 5  # 1 person week = 5 story points
    
    # Predicted efficiency (available bandwidth)
    predicted_efficiency = 12  # 12 person weekss
    
    # Create a bar chart to compare actual vs predicted efficiency
    efficiency_data = pd.DataFrame({
        'Type': ['Predicted Efficiency', 'Actual Efficiency'],
        'Person Weeks': [predicted_efficiency, actual_efficiency]
    })
    fig = px.bar(
        efficiency_data,
        x='Type',
        y='Person Weeks',
        title="Bandwidth Efficiency: Actual vs Predicted",
        text='Person Weeks',
        labels={'Person Weeks': 'Person Weeks'}
    )
    fig.update_layout(yaxis_title="Person Weeks", xaxis_title="Efficiency Type")
    return fig

def bandwidth_efficiency_per_person(df):
    # Create a copy of the DataFrame to avoid SettingWithCopyWarning
    df_copy = df.copy()
    
    # Filter for specific people and clean up names
    allowed_people = ['gagan', 'ganesh', 'akshay']
    df_copy.loc[:, 'Assignee'] = df_copy['Assignee'].fillna('').str.replace('@urbanpiper.com', '', regex=False)
    df_filtered = df_copy[df_copy['Assignee'].apply(lambda x: any(person in x for person in allowed_people))]
    
    # Calculate actual efficiency in person weeks per person
    df_filtered.loc[:, 'Estimate'] = pd.to_numeric(df_filtered['Estimate'], errors='coerce').fillna(0)
    person_efficiency = df_filtered.groupby('Assignee')['Estimate'].sum() / 5  # 1 person week = 5 story points
    
    # Predicted efficiency (available bandwidth per person)
    predicted_efficiency_per_person = 12  # Assuming 12 person weeks available per person
    
    # Create a DataFrame for visualization
    efficiency_data = pd.DataFrame({
        'Person': person_efficiency.index,
        'Predicted Efficiency (Person Weeks)': [predicted_efficiency_per_person] * len(person_efficiency),
        'Actual Efficiency (Person Weeks)': person_efficiency.values
    })
    
    # Melt the DataFrame for grouped bar chart
    efficiency_data_melted = efficiency_data.melt(
        id_vars='Person',
        var_name='Efficiency Type',
        value_name='Person Weeks'
    )
    
    # Ensure the order of bars: Predicted Efficiency first, then Actual Efficiency
    efficiency_data_melted['Efficiency Type'] = pd.Categorical(
        efficiency_data_melted['Efficiency Type'],
        categories=['Predicted Efficiency (Person Weeks)', 'Actual Efficiency (Person Weeks)'],
        ordered=True
    )
    
    # Create a grouped bar chart
    fig = px.bar(
        efficiency_data_melted,
        x='Person',
        y='Person Weeks',
        color='Efficiency Type',
        barmode='group',
        title="Bandwidth Efficiency Per Person: Actual vs Predicted",
        labels={'Person Weeks': 'Person Weeks', 'Person': 'Team Member'}
    )
    fig.update_layout(yaxis_title="Person Weeks", xaxis_title="Team Member")
    return fig

def task_completion_efficiency(df):
    # Calculate average cycle time per sprint
    avg_cycle_time = df.groupby('Cycle Name')['Cycle Time'].mean()
    fig = px.bar(avg_cycle_time, 
                 title="Task Completion Efficiency (Average Cycle Time per Sprint)",
                 labels={'value': 'Average Cycle Time (days)', 'index': 'Sprint'})
    return fig

def priority_vs_completion(df):
    # Analyze completion rate by priority
    priority_completion = df[df['Status'] == 'Done'].groupby('Priority').size() / df.groupby('Priority').size() * 100
    fig = px.bar(priority_completion, 
                 title="Completion Rate by Priority",
                 labels={'value': 'Completion Rate (%)', 'index': 'Priority'})
    return fig

def task_type_split_by_service(df):
    # Define services as a proper list
    services = [
        "api", "app", "atlas-web", "aurelia", "editor", 
        "frodo", "luna", "meraki-sdk", "web",
        "payment-svc"
    ]
    
    # Derive task type from Labels with improved categorization
    def get_task_type(labels):
        labels_lower = str(labels).lower()
        if 'bug' in labels_lower or 'confirmed-bug' in labels_lower:
            return 'Bug'
        elif 'service-request' in labels_lower:
            return 'Service Request'
        elif 'infra-related' in labels_lower:
            return 'Infrastructure'
        else:
            return 'Feature/Enhancement'
    
    df['Task Type'] = df['Labels'].apply(get_task_type)
    
    # Define consistent colors for task types
    task_type_colors = {
        'Bug': '#FF4B4B',  # Red
        'Service Request': '#36B37E',  # Green
        'Infrastructure': '#FFB700',  # Yellow
        'Feature/Enhancement': '#00B8D9'  # Blue
    }
    
    # Generate pie charts for each service
    for service in services:
        # Filter for tasks containing the service label
        service_df = df[df['Labels'].str.contains(service, case=False, na=False)]
        
        if not service_df.empty:
            task_type_counts = service_df['Task Type'].value_counts()
            
            # Only show services that have data
            if not task_type_counts.empty:
                fig = px.pie(
                    values=task_type_counts.values,
                    names=task_type_counts.index,
                    title=f"Task Type Split for {service.upper()}",
                    labels={'value': 'Count', 'names': 'Task Type'},
                    color=task_type_counts.index,
                    color_discrete_map=task_type_colors
                )
                fig.update_layout(
                    title_x=0.5,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig)

def task_distribution_by_type(df):
    # Use the same categorization as task_type_split_by_service
    def get_task_type(labels):
        labels_lower = str(labels).lower()
        if 'bug' in labels_lower or 'confirmed-bug' in labels_lower:
            return 'Bug'
        elif 'service-request' in labels_lower:
            return 'Service Request'
        elif 'infra-related' in labels_lower:
            return 'Infrastructure'
        else:
            return 'Feature/Enhancement'
    
    # Apply consistent categorization
    df['Task Type'] = df['Labels'].apply(get_task_type)
    
    # Calculate task distribution by type
    task_type_counts = df['Task Type'].value_counts()
    
    # Use the same color scheme as task_type_split_by_service
    task_type_colors = {
        'Bug': '#FF4B4B',  # Red
        'Service Request': '#36B37E',  # Green
        'Infrastructure': '#FFB700',  # Yellow
        'Feature/Enhancement': '#00B8D9'  # Blue
    }
    
    # Create a pie chart for task distribution by type
    fig = px.pie(
        values=task_type_counts.values,
        names=task_type_counts.index,
        title="Task Distribution Across Task Types",
        labels={'value': 'Count', 'names': 'Task Type'},
        color=task_type_counts.index,  # Apply consistent colors
        color_discrete_map=task_type_colors
    )
    return fig

def create_dashboard():
    st.title("Direct Ordering Squad : Q1 2025 Insights 🚀")
    
    # Load data
    file_path = './direct-ordering-squad-Q1-2025.csv'  # Updated to use a relative path
    df = load_data(file_path)
    
    if df.empty:
        st.warning("No data available to display. Please check the file path or data format.")
        return

    # Preprocess data to remove duplicates
    df = preprocess_data(df)

    # Team Member Analysis
    assignee_counts = df['Assignee'].value_counts()
    fig_team = px.pie(values=assignee_counts.values, 
                      names=assignee_counts.index,
                      title="Task Distribution Across Team")
    st.plotly_chart(fig_team)

    # Task Distribution by Type
    fig_task_type_distribution = task_distribution_by_type(df)
    st.plotly_chart(fig_task_type_distribution)

    # Priority Analysis
    col1, col2 = st.columns(2)
    with col1:
        priority_counts = df['Priority'].value_counts()
        fig_priority = px.pie(values=priority_counts.values,
                            names=priority_counts.index,
                            title="Task Distribution Across Priorities")
        st.plotly_chart(fig_priority)

    # Bandwidth Efficiency Per Person
    st.header("📊 Bandwidth Efficiency Per Person: Actual vs Predicted")
    fig_efficiency_per_person = bandwidth_efficiency_per_person(df)
    st.plotly_chart(fig_efficiency_per_person)

    # Task Type Split by Service
    st.header("📊 Task Type Split by Service")
    task_type_split_by_service(df)


if __name__ == "__main__":
    create_dashboard()