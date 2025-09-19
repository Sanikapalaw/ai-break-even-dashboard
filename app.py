import streamlit as st
import numpy as np
import plotly.graph_objects as go
import requests
import json

# ----------------- CONFIG -----------------
# Set the page configuration for a wide layout and a title.
st.set_page_config(layout="wide", page_title="Break-Even Dashboard", page_icon="📈")

# ----------------- TITLE AND DESCRIPTION -----------------
st.title("📈 The AI Roadmap to Profitability")
st.markdown("### A Live Break-Even Analysis Dashboard")
st.markdown("This tool helps you visualize your business's financial performance. Enter your metrics below to calculate your break-even point and see your live profit or loss status.")
st.markdown("---")

# ----------------- 1. INPUT SECTION -----------------
st.header("1. Enter Your Business Metrics")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Cost and Pricing")
    fixed_costs = st.number_input("Fixed Costs ($)", min_value=0.0, value=25000.0, format="%.2f")
    variable_cost_per_unit = st.number_input("Variable Cost per Unit ($)", min_value=0.01, value=10.0, format="%.2f")
    price_per_unit = st.number_input("Price per Unit ($)", min_value=0.01, value=20.0, format="%.2f")

with col2:
    st.subheader("Sales and Operations")
    units_sold = st.number_input("Units Sold", min_value=0, value=4000)
    marketing_spend = st.number_input("Marketing Spend ($)", min_value=0.0, value=1000.0, format="%.2f")
    employee_count = st.number_input("Employee Count", min_value=1, value=15)

# ----------------- 2. CALCULATIONS -----------------
total_revenue = units_sold * price_per_unit
total_costs = fixed_costs + (variable_cost_per_unit * units_sold)
total_profit_or_loss = total_revenue - total_costs

# Determine status for the metric delta color
if total_profit_or_loss > 0:
    status = "Profit"
    status_color = "normal"
elif total_profit_or_loss < 0:
    status = "Loss"
    status_color = "inverse"
else:
    status = "Break-Even"
    status_color = "off"

# ----------------- 3. FINANCIAL SNAPSHOT -----------------
st.markdown("---")
st.header("2. Your Financial Snapshot")
col_res1, col_res2, col_res3 = st.columns(3)
with col_res1:
    st.metric("Total Revenue", f"${total_revenue:,.2f}")
with col_res2:
    st.metric("Total Costs", f"${total_costs:,.2f}")
with col_res3:
    st.metric("Total Profit or Loss", f"${total_profit_or_loss:,.2f}", delta=status, delta_color=status_color)

# ----------------- 4. INTERACTIVE BREAK-EVEN PLOT -----------------
st.markdown("---")
st.header("3. Interactive Break-Even Plot")

# Generate data points for the plot
units_range = np.arange(0, units_sold * 2 + 100, 100)
revenue_points = units_range * price_per_unit
cost_points = fixed_costs + (units_range * variable_cost_per_unit)

# Create the Plotly figure
fig = go.Figure()
fig.add_trace(go.Scatter(x=units_range, y=revenue_points, mode="lines", name="Total Revenue", line=dict(color="green", width=3)))
fig.add_trace(go.Scatter(x=units_range, y=cost_points, mode="lines", name="Total Costs", line=dict(color="red", width=3, dash="dash")))

# Add a marker for the current status
fig.add_trace(go.Scatter(x=[units_sold], y=[total_revenue], mode="markers", name="Current Status", marker=dict(color="blue", size=12),
                          hovertext=f"Units: {units_sold}<br>Revenue: ${total_revenue:,.2f}<br>Profit/Loss: ${total_profit_or_loss:,.2f}"))

# Calculate and plot the break-even point if it exists
break_even_units = None
break_even_revenue = None
if price_per_unit > variable_cost_per_unit:
    break_even_units = fixed_costs / (price_per_unit - variable_cost_per_unit)
    break_even_revenue = break_even_units * price_per_unit
    fig.add_trace(go.Scatter(x=[break_even_units], y=[break_even_revenue], mode="markers",
                             name="Break-Even Point", marker=dict(color="orange", size=12),
                             hovertext=f"Break-Even Units: {break_even_units:,.2f}<br>Revenue: ${break_even_revenue:,.2f}"))

# Update plot layout
fig.update_layout(title="Break-Even Analysis", xaxis_title="Units Sold", yaxis_title="Total Costs and Revenue ($)", template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

# ----------------- 5. AI INSIGHTS -----------------
st.markdown("---")
st.header("4. AI-Powered Break-Even Insights")
st.markdown("I am your financial advisor. I will analyze your business snapshot and break-even data and provide insights about profitability, risks, and strategies to improve your margins.")

user_question = st.text_input("💬 Ask your financial advisor something specific (optional):", placeholder="E.g., How can I cross the break-even point?")

# Function to securely get AI insights from the Gemini API
def get_ai_insights(query):
    # This securely retrieves your API key from Streamlit Cloud secrets
    api_key = st.secrets["GEMINI_API_KEY"] 
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"
    
    payload = {"contents": [{"parts": [{"text": query}]}]}
    try:
        response = requests.post(api_url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
        if response.status_code == 200:
            result = response.json()
            # Extract the generated text from the API response
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Exception: {str(e)}"

if st.button("Get AI Insights"):
    with st.spinner("Analyzing your break-even data..."):
        # Construct the detailed prompt with business context
        business_context = f"""
Business Financial Snapshot:
- Fixed Costs: ${fixed_costs:,.2f}
- Variable Cost per Unit: ${variable_cost_per_unit:,.2f}
- Price per Unit: ${price_per_unit:,.2f}
- Units Sold: {units_sold}
- Total Revenue: ${total_revenue:,.2f}
- Total Costs: ${total_costs:,.2f}
- Profit/Loss: ${total_profit_or_loss:,.2f}
"""
        if break_even_units:
            business_context += f"- Break-Even Units: {break_even_units:,.2f}\n"
            business_context += f"- Break-Even Revenue: ${break_even_revenue:,.2f}\n"

        final_prompt = business_context
        # Append user's specific question if provided
        if user_question.strip():
            final_prompt += f"\n\nUser Question: {user_question}"

        insights = get_ai_insights(final_prompt)
        
    st.subheader("AI Insights")
    st.write(insights)
