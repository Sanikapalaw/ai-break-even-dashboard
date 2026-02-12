import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests

# ---------------- CONFIG ----------------
st.set_page_config(layout="wide", page_title="AI CFO: Ultimate Dashboard", page_icon="📈")

# ---------------- TITLE ----------------
st.title("📈 AI CFO: The Roadmap to Profitability")
st.markdown("### Liquidity • Financial Modeling • Valuation • AI Insights")
st.markdown("---")

# ---------------- API KEY ----------------
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("🚨 API Key Missing")
    st.info("Please add GEMINI_API_KEY to your secrets.toml")
    st.stop()

# ---------------- INPUTS ----------------
st.header("1. Enter Your Business Metrics")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.subheader("💰 Costs & Pricing")
    fixed_costs = st.number_input("Fixed Costs ($/Month)", 25000.0)
    variable_cost = st.number_input("Variable Cost per Unit ($)", 10.0)
    price_per_unit = st.number_input("Price per Unit ($)", 20.0)

with c2:
    st.subheader("📦 Operations")
    units_sold = st.number_input("Current Units Sold", 4000)
    marketing_spend = st.number_input("Marketing Spend ($)", 1000.0)
    employee_count = st.number_input("Employee Count", 15)
    avg_salary = st.number_input("Avg Salary per Employee ($/Month)", 3000.0)

with c3:
    st.subheader("🔮 Cash & Value")
    current_cash = st.number_input("Cash on Hand ($)", 50000.0)
    discount_rate = st.slider("Valuation Discount Rate (%)", 5, 20, 10)

with c4:
    st.subheader("🚀 Growth & Time")
    growth_mode = st.radio("Growth Mode", ["Monthly %", "Annual %"], horizontal=True)

    if growth_mode == "Monthly %":
        raw_growth = st.slider("Monthly Growth (%)", 0.0, 20.0, 5.0)
        monthly_growth_rate = raw_growth
        annual_growth_rate = ((1 + raw_growth/100)**12) - 1
    else:
        raw_growth = st.slider("Annual Growth (%)", 0.0, 200.0, 80.0)
        annual_growth_rate = raw_growth / 100
        monthly_growth_rate = ((1 + annual_growth_rate)**(1/12) - 1) * 100

    horizon_map = {"6 Months": 6, "12 Months": 12, "24 Months": 24, "60 Months": 60}
    selected_horizon = st.selectbox("Chart Timeline", list(horizon_map.keys()), index=1)
    forecast_months = horizon_map[selected_horizon]

company_stage = st.selectbox("Company Stage", ["Idea", "Early Startup", "Growth", "Mature"])

# ---------------- CALCULATIONS ----------------
salary_cost = employee_count * avg_salary
total_revenue = units_sold * price_per_unit
total_variable_cost = units_sold * variable_cost
total_costs = fixed_costs + marketing_spend + salary_cost + total_variable_cost
net_profit = total_revenue - total_costs

if (price_per_unit - variable_cost) > 0:
    break_even_units = (fixed_costs + marketing_spend + salary_cost) / (price_per_unit - variable_cost)
else:
    break_even_units = float("inf")

monthly_burn = fixed_costs + marketing_spend + salary_cost
runway_months = current_cash / monthly_burn if monthly_burn > 0 else 0

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Break-Even", "💧 Liquidity", "📈 Modeling", "💰 Valuation", "🤖 AI Advisor"])

# ---- TAB 1 ----
with tab1:
    st.subheader("Snapshot: Current Performance")
    a, b, c, d = st.columns(4)
    a.metric("Revenue", f"${total_revenue:,.0f}")
    b.metric("Costs", f"${total_costs:,.0f}")
    c.metric("Net Profit", f"${net_profit:,.0f}")
    d.metric("Break-Even Units", f"{break_even_units:,.0f}")

    u_range = np.linspace(0, units_sold * 2, 100)
    rev_line = u_range * price_per_unit
    cost_line = fixed_costs + marketing_spend + salary_cost + (u_range * variable_cost)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=u_range, y=rev_line, name="Revenue"))
    fig.add_trace(go.Scatter(x=u_range, y=cost_line, name="Total Cost"))
    fig.add_trace(go.Scatter(x=[units_sold], y=[total_revenue], mode="markers", name="Current"))
    fig.add_trace(go.Scatter(x=[break_even_units], y=[break_even_units*price_per_unit],
                             mode="markers", name="Break-even"))
    st.plotly_chart(fig, use_container_width=True)

# ---- TAB 2 ----
with tab2:
    st.subheader("Liquidity & Runway")
    st.metric("Salary Cost", f"${salary_cost:,.0f}")
    st.metric("Monthly Burn", f"${monthly_burn:,.0f}")
    st.metric("Runway (Months)", f"{runway_months:.1f}")

# ---- TAB 3 ----
with tab3:
    months = list(range(1, forecast_months + 1))
    proj_revenue, proj_profit = [], []
    curr_u = units_sold

    for m in months:
        decay = np.exp(-0.05 * m)
        curr_u = curr_u * (1 + (monthly_growth_rate/100) * decay)
        r = curr_u * price_per_unit
        c = fixed_costs + marketing_spend + salary_cost + (curr_u * variable_cost)
        proj_revenue.append(r)
        proj_profit.append(r - c)

    df = pd.DataFrame({"Month": months, "Revenue": proj_revenue, "Profit": proj_profit})
    fig = px.line(df, x="Month", y=["Revenue", "Profit"], markers=True)
    st.plotly_chart(fig, use_container_width=True)

# ---- TAB 4 ----
# ---- TAB 4: STAGE-BASED VALUATION ----
with tab4:
    st.subheader("Stage-Based Valuation")

    if company_stage == "Idea":
        valuation = current_cash * 5
        method = "VC Heuristic (Cash × 5)"

    elif company_stage == "Early Startup":
        valuation = (total_revenue * 12) * 2
        method = "Revenue Multiple (2× ARR)"

    elif company_stage == "Growth":
        valuation = (total_revenue * 12) * 5
        method = "Growth Multiple (5× ARR)"

    else:  # Mature
        if net_profit > 0:
            valuation = (net_profit * 12) / (discount_rate / 100)
            method = "DCF Proxy (Profit / Discount Rate)"
        else:
            valuation = 0
            method = "Not Profitable – DCF Not Valid"

    st.metric(f"Valuation – {method}", f"${valuation:,.0f}")
    st.info("Valuation method adapts based on the company lifecycle stage.")


# ---- TAB 5 ----
with tab5:
    q = st.text_input("Ask CFO:", "How can I improve profitability?")
    if st.button("Get Advice"):
        prompt = f"""
        Revenue: {total_revenue}
        Profit: {net_profit}
        Burn: {monthly_burn}
        Runway: {runway_months}
        Stage: {company_stage}
        Question: {q}
        """

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        res = requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}]})
        ans = res.json()["candidates"][0]["content"]["parts"][0]["text"]
        st.success(ans)
