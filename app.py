import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests

# ----------------- CONFIG -----------------
st.set_page_config(layout="wide", page_title="AI CFO: Company Decision System", page_icon="📈")

# ----------------- TITLE -----------------
st.title("📈 AI CFO: Company-Level Financial Decision System")
st.markdown("### Liquidity • Modeling • Valuation • Strategy • AI Advisor")
st.markdown("---")

# ----------------- API KEY -----------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = ""

if not api_key:
    st.error("Add GEMINI_API_KEY in secrets.toml")
    st.stop()

# ----------------- INPUTS -----------------
st.header("1. Business Inputs")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("💰 Pricing & Costs")
    fixed_costs = st.number_input("Fixed Costs ($/Month)", 25000.0)
    variable_cost = st.number_input("Variable Cost per Unit ($)", 10.0)
    price_per_unit = st.number_input("Price per Unit ($)", 20.0)

with col2:
    st.subheader("📦 Operations")
    units_sold = st.number_input("Units Sold", 4000)
    marketing_spend = st.number_input("Marketing Spend ($)", 1000.0)
    employee_count = st.number_input("Employees", 15)
    avg_salary = st.number_input("Avg Salary / Employee ($)", 3000.0)

with col3:
    st.subheader("🏢 Business Context")
    company_stage = st.selectbox("Company Stage", ["Idea", "Early Startup", "Growth", "Mature"])
    industry = st.selectbox("Industry", ["SaaS", "E-commerce", "FinTech", "EdTech", "Manufacturing"])
    current_cash = st.number_input("Cash on Hand ($)", 50000.0)

with col4:
    st.subheader("🚀 Growth")
    monthly_growth = st.slider("Monthly Growth %", 0.0, 20.0, 5.0)
    discount_rate = st.slider("Discount Rate %", 5, 20, 10)
    forecast_months = st.selectbox("Forecast Horizon", [6,12,24,60])

# ----------------- CORE CALCULATIONS -----------------
salary_cost = employee_count * avg_salary
total_revenue = units_sold * price_per_unit
total_variable_cost = units_sold * variable_cost
total_costs = fixed_costs + total_variable_cost + marketing_spend + salary_cost
net_profit = total_revenue - total_costs

monthly_burn = fixed_costs + marketing_spend + salary_cost
runway_months = current_cash / monthly_burn if monthly_burn > 0 else 0

# ----------------- TABS -----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Performance", "💧 Liquidity", "📈 Forecast", "💰 Valuation", "🤖 AI Advisor"
])

# ----------------- TAB 1 -----------------
with tab1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Revenue", f"${total_revenue:,.0f}")
    c2.metric("Costs", f"${total_costs:,.0f}")
    c3.metric("Net Profit", f"${net_profit:,.0f}")

# ----------------- TAB 2 -----------------
with tab2:
    st.metric("Monthly Burn", f"${monthly_burn:,.0f}")
    st.metric("Runway (Months)", f"{runway_months:.1f}")

    if runway_months < 3:
        st.error("CRITICAL")
    elif runway_months < 6:
        st.warning("CAUTION")
    else:
        st.success("HEALTHY")

# ----------------- TAB 3 -----------------
with tab3:
    months = list(range(1, forecast_months+1))
    proj_revenue, proj_profit = [], []
    curr_units = units_sold

    for m in months:
        decay = np.exp(-0.05*m)
        effective_growth = (monthly_growth/100) * decay
        curr_units *= (1 + effective_growth)
        rev = curr_units * price_per_unit
        cost = fixed_costs + marketing_spend + salary_cost + (curr_units * variable_cost)
        prof = rev - cost
        proj_revenue.append(rev)
        proj_profit.append(prof)

    df = pd.DataFrame({"Month": months, "Revenue": proj_revenue, "Profit": proj_profit})
    fig = px.line(df, x="Month", y=["Revenue","Profit"], markers=True)
    st.plotly_chart(fig, use_container_width=True)

# ----------------- TAB 4 -----------------
with tab4:
    st.subheader("Company-Aware Valuation")

    annual_revenue = total_revenue * 12
    annual_profit = net_profit * 12

    if company_stage == "Idea":
        st.warning("Valuation not reliable at idea stage.")

    elif company_stage == "Early Startup":
        multiple = 3 if industry == "SaaS" else 1.5
        valuation = annual_revenue * multiple
        st.metric("Revenue Multiple Valuation", f"${valuation:,.0f}")

    elif company_stage == "Growth":
        ebitda = annual_profit * 0.8
        valuation = ebitda * 6
        st.metric("EV/EBITDA Valuation", f"${valuation:,.0f}")

    elif company_stage == "Mature":
        if annual_profit <= 0:
            st.warning("DCF requires positive cash flow.")
        else:
            years = [1,2,3,4,5]
            cf = annual_profit
            pvs = []
            for y in years:
                cf *= (1 + monthly_growth*12/100)
                pv = cf / ((1 + discount_rate/100)**y)
                pvs.append(pv)

            terminal_growth = 0.03
            terminal_val = (cf*(1+terminal_growth))/((discount_rate/100)-terminal_growth)
            terminal_pv = terminal_val/((1+discount_rate/100)**5)
            total_val = sum(pvs)+terminal_pv
            st.metric("Simplified DCF Valuation", f"${total_val:,.0f}")

    st.markdown("""
    ### Model Assumptions
    - Growth slows over time  
    - Employee cost affects burn  
    - Valuation depends on stage  
    - Educational / strategic model  
    """)

# ----------------- TAB 5 -----------------
with tab5:
    user_q = st.text_input("Ask CFO:", "How can I improve profitability?")
    if st.button("Get AI Advice"):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents":[{
                "parts":[{
                    "text":f"""
You are a CFO.
Revenue: {total_revenue}
Profit: {net_profit}
Runway: {runway_months}
Stage: {company_stage}
Industry: {industry}
Question: {user_q}
Give strategic advice.
"""
                }]
            }]
        }
        res = requests.post(url, json=payload)
        ans = res.json()['candidates'][0]['content']['parts'][0]['text']
        st.success(ans)
