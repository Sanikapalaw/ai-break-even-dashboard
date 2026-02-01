import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests

# ----------------- CONFIG -----------------
st.set_page_config(layout="wide", page_title="AI CFO: Executive Dashboard", page_icon="📈")

# ----------------- TITLE -----------------
st.title("📈 AI CFO: The Roadmap to Profitability")
st.markdown("### Executive Decision-Support System • Liquidity • Risk • Valuation")
st.markdown("---")

# ----------------- API KEY HANDLING -----------------
# Tip: Using st.secrets is correct for deployment. 
# For local testing, you can use an input or a .streamlit/secrets.toml file.
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    api_key = ""

if not api_key:
    st.error("🚨 **API Key Missing**")
    st.info("Please add `GEMINI_API_KEY` to your secrets.toml file.")
    st.stop()

# ----------------- 1. UNIVERSAL INPUTS -----------------
st.sidebar.header("📊 Global Business Controls")
with st.sidebar:
    company_stage = st.selectbox("Company Stage", ["Idea", "Early Startup", "Growth", "Mature"])
    horizon_options = {"6 Months": 6, "12 Months": 12, "24 Months": 24, "60 Months": 60}
    forecast_months = horizon_options[st.selectbox("Forecast Horizon", list(horizon_options.keys()), index=1)]

col_in1, col_in2, col_in3, col_in4 = st.columns(4)

with col_in1:
    st.subheader("💰 Pricing Strategy")
    price_per_unit = st.number_input("Price per Unit ($)", value=20.0, step=1.0)
    variable_cost = st.number_input("Variable Cost per Unit ($)", value=10.0, step=1.0)
    units_sold = st.number_input("Current Monthly Volume", value=4000, step=100)

with col_in2:
    st.subheader("🏢 Fixed Overhead")
    fixed_costs = st.number_input("Fixed Costs ($/Mo)", value=25000.0, step=1000.0)
    marketing_spend = st.number_input("Marketing Budget ($/Mo)", value=1000.0, step=100.0)
    employee_count = st.number_input("Headcount", value=15)
    avg_salary = st.number_input("Avg Salary ($/Mo)", value=3000.0, step=500.0)

with col_in3:
    st.subheader("🏦 Capital & Risk")
    current_cash = st.number_input("Cash on Hand ($)", value=50000.0, step=5000.0)
    discount_rate = st.slider("WACC / Discount Rate (%)", 5, 25, 12)

with col_in4:
    st.subheader("🚀 Growth Dynamics")
    monthly_growth_rate = st.slider("Expected Monthly Growth (%)", 0.0, 20.0, 5.0, step=0.5)
    annual_growth_rate = ((1 + (monthly_growth_rate/100)) ** 12) - 1

# ----------------- 2. ADVANCED CALCULATIONS -----------------
salary_cost = employee_count * avg_salary
monthly_burn = fixed_costs + marketing_spend + salary_cost
total_revenue = units_sold * price_per_unit
total_variable_cost = units_sold * variable_cost
total_costs = monthly_burn + total_variable_cost
net_profit = total_revenue - total_costs
contribution_margin = price_per_unit - variable_cost
contribution_margin_pct = (contribution_margin / price_per_unit) * 100 if price_per_unit > 0 else 0

if contribution_margin > 0:
    break_even_units = monthly_burn / contribution_margin
else:
    break_even_units = float('inf')

runway_months = current_cash / abs(net_profit) if net_profit < 0 else float('inf')

# ----------------- 3. EXECUTIVE TABS -----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Unit Economics", "📄 P&L Statement", "📈 Growth Projections", "💰 Valuation", "🤖 Executive AI Advisor"
])

# --- TAB 1: UNIT ECONOMICS & SENSITIVITY ---
with tab1:
    st.subheader("Profitability Analysis")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Net Profit", f"${net_profit:,.2f}", delta=f"{contribution_margin_pct:.1f}% Margin")
    c2.metric("Break-Even Volume", f"{break_even_units:,.0f} Units")
    c3.metric("Burn Rate", f"${monthly_burn:,.2f}")
    c4.metric("Cash Runway", f"{runway_months:.1f} Months", delta_color="inverse")

    # Sensitivity Analysis Table (The PhD Layer)
    with st.expander("🔍 Strategic Sensitivity Analysis"):
        st.write("How changes in Price and Variable Costs impact your Break-Even Point:")
        prices = [price_per_unit * 0.9, price_per_unit, price_per_unit * 1.1]
        v_costs = [variable_cost * 0.9, variable_cost, variable_cost * 1.1]
        sensitivity_data = []
        for p in prices:
            row = []
            for v in v_costs:
                be = monthly_burn / (p - v) if (p - v) > 0 else 0
                row.append(f"{be:,.0f}")
            sensitivity_data.append(row)
        
        df_sens = pd.DataFrame(sensitivity_data, 
                               index=[f"Price ${p:,.0f}" for p in prices],
                               columns=[f"Var Cost ${v:,.0f}" for v in v_costs])
        st.table(df_sens)

# --- TAB 2: P&L STATEMENT ---
with tab2:
    st.subheader("Monthly Profit & Loss Statement (Pro-Forma)")
    pl_data = {
        "Metric": ["Total Revenue", "Less: Variable Costs (COGS)", "Gross Profit", 
                   "Fixed Operating Costs", "Marketing Expenses", "Salary & Payroll", 
                   "Total Operating Expenses (OpEx)", "Net Operating Income (EBITDA)"],
        "Current Value": [
            f"${total_revenue:,.2f}", f"(${total_variable_cost:,.2f})", f"${total_revenue - total_variable_cost:,.2f}",
            f"(${fixed_costs:,.2f})", f"(${marketing_spend:,.2f})", f"(${salary_cost:,.2f})",
            f"(${monthly_burn:,.2f})", f"${net_profit:,.2f}"
        ]
    }
    st.table(pd.DataFrame(pl_data))

# --- TAB 3: PROJECTIONS ---
with tab3:
    months = list(range(1, forecast_months + 1))
    proj_revenue, proj_profit = [], []
    curr_u = units_sold
    for m in months:
        decay = np.exp(-0.02*m) # Slower decay for more realistic growth
        curr_u = curr_u * (1 + (monthly_growth_rate/100)*decay)
        r = curr_u * price_per_unit
        c = monthly_burn + (curr_u * variable_cost)
        proj_revenue.append(r)
        proj_profit.append(r - c)
        
    df_proj = pd.DataFrame({"Month": months, "Revenue": proj_revenue, "Profit": proj_profit})
    fig_proj = px.line(df_proj, x="Month", y=["Revenue", "Profit"], 
                       title="Revenue vs Profit Growth Path", template="plotly_white")
    st.plotly_chart(fig_proj, use_container_width=True)

# --- TAB 4: VALUATION ---
with tab4:
    st.subheader("Strategic Valuation Analysis")
    
    if company_stage == "Idea":
        val_method = "VC Heuristic"
        valuation = current_cash * 5
    elif net_profit <= 0:
        val_method = "Revenue Multiple (Early Stage)"
        valuation = (total_revenue * 12) * 3 # 3x Revenue Multiple for non-profitable growth
    else:
        val_method = "DCF Model"
        # Simple DCF Logic
        annual_fcf = net_profit * 12
        valuation = annual_fcf * (1 + annual_growth_rate) / ((discount_rate/100) - 0.03)

    col_v1, col_v2 = st.columns(2)
    col_v1.metric(f"Estimated Valuation ({val_method})", f"${valuation:,.2f}")
    col_v2.info(f"Methodology: {val_method}. Note: For {company_stage} stages, we prioritize {'Revenue Multiples' if net_profit <= 0 else 'Cash Flow'}.")

# --- TAB 5: AI ADVISOR ---
with tab5:
    st.subheader("🤖 CFO Strategic Briefing")
    if st.button("Generate Executive Analysis"):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        prompt = f"""
        Act as a PhD Finance Professor and Startup CFO. Analyze this data:
        - Current Stage: {company_stage}
        - Monthly Revenue: ${total_revenue:,.2f}
        - Net Profit: ${net_profit:,.2f}
        - Monthly Burn: ${monthly_burn:,.2f}
        - Runway: {runway_months:.1f} months
        - Margin: {contribution_margin_pct:.1f}%
        
        Provide:
        1. A 2-sentence 'State of the Union'.
        2. Three specific 'Risk Mitigation' steps.
        3. A recommendation on whether to raise capital now.
        """
        payload = {"contents":[{"parts":[{"text": prompt}]}]}
        try:
            res = requests.post(url, json=payload)
            ans = res.json()['candidates'][0]['content']['parts'][0]['text']
            st.markdown(ans)
        except:
            st.error("Connection to AI Advisor failed. Check API Key.")
