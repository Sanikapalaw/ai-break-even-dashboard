import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests

# ----------------- CONFIG -----------------
st.set_page_config(layout="wide", page_title="AI CFO: Strategic Simulator", page_icon="📉")

# ----------------- TITLE -----------------
st.title("📈 AI CFO: The Roadmap to Profitability")
st.markdown("### Adaptive Valuation • Strategic Simulation • Liquidity")
st.markdown("---")

# ----------------- API KEY HANDLING -----------------
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# ----------------- 1. STRATEGIC INPUTS (Sidebar) -----------------
st.sidebar.header("🕹️ Strategy & Timeline")
with st.sidebar:
    # This input drives the valuation logic below
    company_stage = st.selectbox("Company Stage", ["Idea", "Early Startup", "Growth", "Mature"])
    
    horizon_options = {"6 Months": 6, "12 Months": 12, "24 Months": 24, "60 Months": 60}
    selected_horizon = st.selectbox("Projection Timeline", list(horizon_options.keys()), index=1)
    forecast_months = horizon_options[selected_horizon]
    
    current_cash = st.number_input("Cash on Hand ($)", value=50000.0)
    growth_rate = st.slider("Target Monthly Growth (%)", 0.0, 20.0, 5.0)

# ----------------- 2. OPERATIONS INPUTS (Main Page) -----------------
col_in1, col_in2 = st.columns(2)
with col_in1:
    st.subheader("💰 Pricing & Unit Economics")
    price = st.number_input("Price per Unit ($)", value=20.0)
    v_cost = st.number_input("Variable Cost per Unit ($)", value=10.0)
    units = st.number_input("Current Monthly Volume", value=4000)

with col_in2:
    st.subheader("🏢 Monthly Operating Burn")
    fixed_overhead = st.number_input("Fixed Costs ($/Month)", value=25000.0)
    marketing = st.number_input("Marketing Spend ($)", value=1000.0)
    employees = st.number_input("Employee Count", value=15)
    salary = st.number_input("Avg Salary per Employee ($)", value=3000.0)

# ----------------- 3. CORE CALCULATIONS -----------------
monthly_salaries = employees * salary
total_fixed_burn = fixed_overhead + marketing + monthly_salaries
revenue = units * price
net_profit = revenue - (total_fixed_burn + (units * v_cost))
runway = current_cash / abs(net_profit) if net_profit < 0 else float('inf')

# ----------------- 4. THE ADAPTIVE VALUATION LOGIC -----------------
# This section fulfills your request to have different methods for different stages
if company_stage == "Idea":
    # Logic: Ideas are valued on 'Potential' not math.
    valuation = current_cash * 5 
    v_method = "VC Heuristic (Idea Stage)"
    v_description = "Since there is no revenue, we value the concept based on the current capital and potential."

elif company_stage == "Early Startup":
    # Logic: Startups are valued on 'Revenue Multiples'.
    valuation = (revenue * 12) * 2 
    v_method = "Revenue Multiple (2x Annualized)"
    v_description = "Valuation is based on the top-line revenue growth potential of a new venture."

elif company_stage == "Growth":
    # Logic: Growth companies get a higher multiple because they have traction.
    valuation = (revenue * 12) * 5 
    v_method = "Growth Multiple (5x Annualized)"
    v_description = "A higher revenue multiple is applied here to reflect proven market traction."

else: # Mature
    if net_profit > 0:
        # Logic: Mature profitable companies use DCF (Discounted Cash Flow).
        valuation = (net_profit * 12) / 0.15 
        v_method = "DCF Model (Discount Rate: 15%)"
        v_description = "Valuation based on the present value of future cash flows."
    else:
        # Logic: If Mature but losing money, we revert to Asset value or Revenue Multiple.
        valuation = (revenue * 12) * 1.5
        v_method = "Asset/Revenue Recovery Multiple"
        v_description = "A conservative multiple is used because the company is mature but pre-profit."

# ----------------- 5. EXECUTIVE TABS -----------------
tab1, tab2, tab3 = st.tabs(["📊 Performance", "💰 Strategic Valuation", "🤖 AI Advisor"])

with tab1:
    st.subheader("Financial Health metrics")
    m1, m2, m3 = st.columns(3)
    m1.metric("Projected Profit", f"${net_profit:,.0f}")
    m2.metric("Monthly Burn", f"${total_fixed_burn:,.0f}")
    m3.metric("Runway", f"{runway:.1f} Mo" if runway != float('inf') else "Stable")
    
    # Insert your Break-Even and Liquidity charts here...

with tab2:
    st.header(f"Method: {v_method}")
    st.metric("Estimated Enterprise Value", f"${valuation:,.2f}")
    st.markdown(f"**Professor's Note:** {v_description}")
    st.info(f"As a {company_stage} company, this is the industry-standard valuation approach.")

with tab3:
    if st.button("Generate Briefing"):
        # AI Advisor logic here...
        st.success("Analysis Complete.")
