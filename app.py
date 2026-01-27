import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests

# ----------------- CONFIG -----------------
st.set_page_config(layout="wide", page_title="AI CFO: Ultimate Dashboard", page_icon="📈")

# ----------------- TITLE -----------------
st.title("📈 AI CFO: The Roadmap to Profitability")
st.markdown("### Liquidity • Financial Modeling • Valuation • AI Insights")
st.markdown("---")

# ----------------- API KEY HANDLING -----------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    api_key = ""

if not api_key:
    st.error("🚨 **API Key Missing**")
    st.info("Please add `GEMINI_API_KEY` to your secrets.toml file.")
    st.stop()

# ----------------- 1. UNIVERSAL INPUTS -----------------
st.header("1. Enter Your Business Metrics")

col_in1, col_in2, col_in3, col_in4 = st.columns(4)

with col_in1:
    st.subheader("💰 Costs & Pricing")
    fixed_costs = st.number_input("Fixed Costs ($/Month)", value=25000.0, step=1000.0)
    variable_cost = st.number_input("Variable Cost per Unit ($)", value=10.0, step=1.0)
    price_per_unit = st.number_input("Price per Unit ($)", value=20.0, step=1.0)

with col_in2:
    st.subheader("📦 Operations")
    units_sold = st.number_input("Current Units Sold", value=4000, step=100)
    marketing_spend = st.number_input("Marketing Spend ($)", value=1000.0, step=100.0)
    employee_count = st.number_input("Employee Count", value=15)

with col_in3:
    st.subheader("🔮 Cash & Value")
    current_cash = st.number_input("Cash on Hand ($)", value=50000.0, step=5000.0)
    discount_rate = st.slider("Valuation Discount Rate (%)", 5, 20, 10)

with col_in4:
    st.subheader("🚀 Growth & Time")
    growth_mode = st.radio("Growth Rate Mode:", ["Monthly %", "Annual %"], horizontal=True)
    
    if growth_mode == "Monthly %":
        raw_growth = st.slider("Monthly Growth (%)", 0.0, 20.0, 5.0, step=0.5)
        monthly_growth_rate = raw_growth
        annual_growth_rate = ((1 + (raw_growth/100)) ** 12) - 1
    else:
        raw_growth = st.slider("Annual Growth (%)", 0.0, 200.0, 80.0, step=5.0)
        annual_growth_rate = raw_growth / 100
        monthly_growth_rate = ((1 + annual_growth_rate) ** (1/12) - 1) * 100

    horizon_options = {
        "6 Months": 6,
        "12 Months": 12, 
        "24 Months": 24, 
        "60 Months": 60
    }
    selected_horizon = st.selectbox("Chart Timeline", list(horizon_options.keys()), index=1)
    forecast_months = horizon_options[selected_horizon]

# ---------- Company Stage ----------
company_stage = st.selectbox(
    "Company Stage",
    ["Idea", "Early Startup", "Growth", "Mature"]
)

# ----------------- 2. CALCULATIONS -----------------
total_revenue = units_sold * price_per_unit
total_variable_cost = units_sold * variable_cost
total_costs = fixed_costs + total_variable_cost + marketing_spend
net_profit = total_revenue - total_costs

if (price_per_unit - variable_cost) > 0:
    break_even_units = (fixed_costs + marketing_spend) / (price_per_unit - variable_cost)
else:
    break_even_units = float('inf')

# ----------------- 3. TABS -----------------
st.markdown("---")
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Break-Even", "💧 Liquidity", "📈 Modeling", "💰 Valuation", "🤖 AI Advisor"
])

# --- TAB 1: BREAK-EVEN ---
with tab1:
    st.subheader("Snapshot: Current Performance")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"${total_revenue:,.2f}")
    c2.metric("Total Costs", f"${total_costs:,.2f}")
    c3.metric("Net Profit", f"${net_profit:,.2f}")
    c4.metric("Break-Even Units", f"{break_even_units:,.0f}")

    units_range = np.linspace(0, units_sold*2, 100)
    rev_line = units_range * price_per_unit
    cost_line = fixed_costs + marketing_spend + (units_range * variable_cost)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=units_range, y=rev_line, name="Revenue"))
    fig.add_trace(go.Scatter(x=units_range, y=cost_line, name="Total Cost"))

    fig.add_trace(go.Scatter(
        x=[units_sold], y=[total_revenue],
        mode="markers", marker=dict(size=14),
        name="Current Status"
    ))

    fig.add_trace(go.Scatter(
        x=[break_even_units], y=[break_even_units*price_per_unit],
        mode="markers", marker=dict(size=12),
        name="Break-even"
    ))

    st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: LIQUIDITY ---
with tab2:
    st.subheader("Liquidity")

    avg_salary = 3000
    salary_cost = employee_count * avg_salary
    monthly_burn = fixed_costs + marketing_spend + salary_cost
    runway_months = current_cash / monthly_burn if monthly_burn > 0 else 0

    st.metric("Monthly Burn", f"${monthly_burn:,.2f}")
    st.metric("Runway (Months)", f"{runway_months:.1f}")

# --- TAB 3: PROJECTIONS ---
with tab3:
    months = list(range(1, forecast_months + 1))
    proj_revenue, proj_profit = [], []
    curr_u = units_sold
    
    for m in months:
        decay = np.exp(-0.05*m)
        curr_u = curr_u * (1 + (monthly_growth_rate/100)*decay)
        r = curr_u * price_per_unit
        c = fixed_costs + marketing_spend + (curr_u * variable_cost)
        p = r - c
        proj_revenue.append(r)
        proj_profit.append(p)
        
    df_proj = pd.DataFrame({"Month": months, "Revenue": proj_revenue, "Profit": proj_profit})
    fig_proj = px.line(df_proj, x="Month", y=["Revenue", "Profit"], markers=True)
    st.plotly_chart(fig_proj, use_container_width=True)

# --- TAB 4: VALUATION ---
with tab4:
    st.subheader("Valuation: Decision-Support Financial Model")

    if company_stage == "Idea":
        st.info("Idea-stage companies do not have predictable cash flows. Showing heuristic valuation.")
        vc_estimate = current_cash * 5
        st.metric("Indicative Valuation (VC Heuristic)", f"${vc_estimate:,.2f}")
    else:
        annualized_profit = net_profit * 12

        if annualized_profit > 0:
            years = [1,2,3,4,5]
            pvs = []
            cf = annualized_profit
            for y in years:
                cf *= (1 + annual_growth_rate)
                pv = cf / ((1 + (discount_rate/100)) ** y)
                pvs.append(pv)

            terminal_growth = 0.03
            terminal_val = (cf*(1+terminal_growth))/((discount_rate/100)-terminal_growth)
            terminal_pv = terminal_val/((1+(discount_rate/100))**5)
            total_val = sum(pvs)+terminal_pv

            st.metric("Estimated Valuation (DCF)", f"${total_val:,.2f}")

    st.markdown("""
    ### Disclaimer
    This system provides **indicative financial insights for strategic planning only**.
    It is not intended for real investment or funding decisions.
    """)

# --- TAB 5: AI ADVISOR ---
with tab5:
    user_q = st.text_input("Ask CFO:", "How can I improve profitability?")
    if st.button("Get Answer"):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents":[{
                "parts":[{
                    "text":f"""
You are a startup CFO.
Revenue: {total_revenue}
Profit: {net_profit}
Runway: {runway_months}
Stage: {company_stage}
Question: {user_q}
Give strategic advice.
"""
                }]
            }]
        }
        res = requests.post(url, json=payload)
        ans = res.json()['candidates'][0]['content']['parts'][0]['text']
        st.success(ans)

