import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests

# ----------------- CONFIG -----------------
st.set_page_config(layout="wide", page_title="AI CFO Dashboard", page_icon="📈")

# ----------------- TITLE -----------------
st.title("📈 AI CFO: Startup Decision Dashboard")
st.markdown("### Simple insights for founders: Profit • Runway • Growth • Valuation")
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
st.header("Step 1: Enter Your Business Basics")

col1, col2, col3 = st.columns(3)

with col1:
    fixed_costs = st.number_input(
        "Fixed Costs ($/month)", 25000.0, step=1000.0,
        help="Rent, software, subscriptions etc."
    )
    marketing_spend = st.number_input(
        "Marketing Spend ($/month)", 1000.0, step=100.0,
        help="Ads, influencers, campaigns."
    )

with col2:
    price_per_unit = st.number_input(
        "Price per Unit ($)", 20.0, step=1.0,
        help="How much you charge customers."
    )
    variable_cost = st.number_input(
        "Cost per Unit ($)", 10.0, step=1.0,
        help="Delivery, manufacturing, cloud usage."
    )
    units_sold = st.number_input(
        "Units Sold (per month)", 4000, step=100,
        help="How many customers or orders per month."
    )

with col3:
    employee_count = st.number_input("Employees", 15)
    avg_salary = st.number_input(
        "Avg Salary per Employee ($/month)", 3000.0, step=500.0
    )
    current_cash = st.number_input(
        "Cash in Bank ($)", 50000.0, step=5000.0
    )

# ----------------- GROWTH SLIDER -----------------
st.header("Step 2: How fast are you growing?")

growth_label = st.select_slider(
    "Growth Speed",
    options=["Slow", "Moderate", "Rocket Ship"],
    value="Moderate",
    help="How fast you think your business will grow."
)

if growth_label == "Slow":
    monthly_growth_rate = 5
elif growth_label == "Moderate":
    monthly_growth_rate = 10
else:
    monthly_growth_rate = 20

annual_growth_rate = ((1 + (monthly_growth_rate/100)) ** 12) - 1

forecast_months = st.selectbox(
    "Forecast Period",
    [6, 12, 24, 60]
)

company_stage = st.selectbox(
    "Company Stage",
    ["Idea", "Early Startup", "Growth", "Mature"]
)

discount_rate = st.slider("Risk Level (Discount Rate %)", 5, 20, 10)

# ----------------- CORE CALCULATIONS -----------------
salary_cost = employee_count * avg_salary
total_revenue = units_sold * price_per_unit
total_variable_cost = units_sold * variable_cost
total_costs = fixed_costs + marketing_spend + salary_cost + total_variable_cost
net_profit = total_revenue - total_costs

monthly_burn = fixed_costs + marketing_spend + salary_cost
runway_months = current_cash / monthly_burn if monthly_burn > 0 else 0

# Break-even
if price_per_unit - variable_cost > 0:
    break_even_units = (fixed_costs + marketing_spend + salary_cost) / (price_per_unit - variable_cost)
else:
    break_even_units = np.inf

# ----------------- TABS -----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Health Check", "💧 Runway", "📈 Growth", "💰 Valuation", "🤖 AI CFO"
])

# ----------------- TAB 1: HEALTH -----------------
with tab1:
    st.subheader("Business Health")

    st.metric("Revenue", f"${total_revenue:,.0f}")
    st.metric("Profit", f"${net_profit:,.0f}")

    if net_profit > 0:
        st.success("🟢 You are profitable! Great job.")
    else:
        st.error("🔴 You are burning cash.")

    st.metric("Break-even Units", f"{break_even_units:,.0f}")

# ----------------- TAB 2: RUNWAY -----------------
with tab2:
    st.subheader("Cash Runway")

    st.metric("Monthly Burn", f"${monthly_burn:,.0f}")
    st.metric("Runway (months)", f"{runway_months:.1f}")

    if runway_months > 12:
        st.success("🟢 Safe: You have more than 1 year of runway.")
    elif runway_months > 6:
        st.warning("🟡 Caution: Less than 1 year runway.")
    else:
        st.error("🔴 Danger: You may run out of cash soon!")

# ----------------- TAB 3: GROWTH -----------------
with tab3:
    st.subheader("Growth Projection")

    months = list(range(1, forecast_months + 1))
    proj_revenue, proj_profit = [], []
    curr_units = units_sold

    for m in months:
        decay = np.exp(-0.05*m)
        curr_units *= (1 + (monthly_growth_rate/100)*decay)
        r = curr_units * price_per_unit
        c = fixed_costs + marketing_spend + salary_cost + (curr_units * variable_cost)
        p = r - c
        proj_revenue.append(r)
        proj_profit.append(p)

    df = pd.DataFrame({
        "Month": months,
        "Revenue": proj_revenue,
        "Profit": proj_profit
    })

    fig = px.line(df, x="Month", y=["Revenue", "Profit"], markers=True)
    st.plotly_chart(fig, use_container_width=True)

# ----------------- TAB 4: VALUATION -----------------
with tab4:
    st.subheader("Valuation")

    if company_stage == "Idea":
        st.info("Using simple heuristic (early-stage rule of thumb).")
        valuation = current_cash * 5
        st.metric("Indicative Valuation", f"${valuation:,.0f}")

    elif net_profit <= 0:
        st.info("Using Revenue Multiple (loss-making startup).")
        valuation = total_revenue * 6
        st.metric("Indicative Valuation (6x Revenue)", f"${valuation:,.0f}")

    else:
        st.info("Using DCF (cash-flow based valuation).")
        years = [1,2,3,4,5]
        pvs = []
        cf = net_profit * 12

        for y in years:
            cf *= (1 + annual_growth_rate)
            pv = cf / ((1 + (discount_rate/100)) ** y)
            pvs.append(pv)

        terminal_growth = 0.03
        if discount_rate/100 > terminal_growth:
            terminal_val = (cf*(1+terminal_growth))/((discount_rate/100)-terminal_growth)
            terminal_pv = terminal_val/((1+(discount_rate/100))**5)
            valuation = sum(pvs) + terminal_pv
            st.metric("Estimated Valuation (DCF)", f"${valuation:,.0f}")
        else:
            st.error("Discount rate too low for DCF.")

# ----------------- TAB 5: AI CFO -----------------
with tab5:
    st.subheader("Ask Your AI CFO")

    user_q = st.text_input("Ask a business question:")
    if st.button("Get Advice"):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents":[{
                "parts":[{
                    "text":f"""
You are a startup CFO.
Revenue: {total_revenue}
Profit: {net_profit}
Burn: {monthly_burn}
Runway: {runway_months}
Stage: {company_stage}
Question: {user_q}
Give simple strategic advice.
"""
                }]
            }]
        }
        res = requests.post(url, json=payload)
        ans = res.json()['candidates'][0]['content']['parts'][0]['text']
        st.success(ans)
