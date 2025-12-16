import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. Setup Dummy Data ---
# Forecast Data
dates = pd.date_range(start="2025-01-01", periods=12, freq="M")
actual_values = [100, 110, 105, 120, 125, 130, None, None, None, None, None, None]
forecast_values = [None, None, None, None, None, 130, 135, 140, 145, 150, 155, 160]
df_forecast = pd.DataFrame({'Date': dates, 'Actual': actual_values, 'Forecast': forecast_values})
df_forecast['Month_Name'] = df_forecast['Date'].dt.strftime('%B') # Create Month Name column

# Gantt Data (Project Roadmap)
df_gantt = pd.DataFrame([
    dict(Task="Data Cleaning", Start='2025-01-01', Finish='2025-01-15', Type="Prep"),
    dict(Task="Model Training", Start='2025-01-10', Finish='2025-02-01', Type="AI Dev"),
    dict(Task="Dashboard UI",   Start='2025-01-20', Finish='2025-02-20', Type="Frontend"),
    dict(Task="Deployment",     Start='2025-02-15', Finish='2025-03-01', Type="DevOps")
])

# --- 2. Sidebar Inputs (Adding Month) ---
st.sidebar.header("Filter Options")

# >>> CHANGE 1: ADD MONTH INPUT <<<
# We extract unique months from our data for the dropdown
all_months = df_forecast['Month_Name'].unique().tolist()
selected_month = st.sidebar.multiselect(
    "Select Month(s) to View:", 
    options=all_months,
    default=all_months[:6] # Default to first 6 months
)

# Filter the dataframe based on input
filtered_df = df_forecast[df_forecast['Month_Name'].isin(selected_month)]

# --- 3. The Forecast Chart (Dashed Model) ---
st.subheader("Financial Forecast Model")

fig_forecast = go.Figure()

# Actual Data (Solid Line)
fig_forecast.add_trace(go.Scatter(
    x=filtered_df['Date'], 
    y=filtered_df['Actual'],
    mode='lines+markers',
    name='Actual Revenue',
    line=dict(color='blue', width=3)
))

# >>> CHANGE 2: FORECAST MODEL IN DASHED FORMAT <<<
# We use 'dash' inside the line dictionary
fig_forecast.add_trace(go.Scatter(
    x=filtered_df['Date'], 
    y=filtered_df['Forecast'],
    mode='lines+markers',
    name='AI Forecast',
    line=dict(color='red', width=3, dash='dash') # <--- HERE IS THE DASH
))

st.plotly_chart(fig_forecast, use_container_width=True)

# --- 4. The Gantt Chart (With Legend) ---
st.subheader("Project Roadmap (Gantt)")

# >>> CHANGE 3: ADD LEGEND IN GANTT CHART <<<
# By mapping 'color' to a column (like 'Type'), Plotly automatically creates a legend.
fig_gantt = px.timeline(
    df_gantt, 
    x_start="Start", 
    x_end="Finish", 
    y="Task", 
    color="Type", # <--- This creates the Legend grouping
    title="Implementation Timeline"
)

# Force the legend to be visible and adjust layout if needed
fig_gantt.update_layout(
    showlegend=True, 
    legend_title_text="Team / Phase"
)
fig_gantt.update_yaxes(autorange="reversed") # Standard Gantt formatting

st.plotly_chart(fig_gantt, use_container_width=True)
