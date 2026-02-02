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
st.markdown("### Strategic Simulation Engine • Operational Modeling • Risk Analysis")
st.markdown("---")

# ----------------- API KEY HANDLING -----------------
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# ----------------- 1. STRATEGIC INPUTS (Sidebar) -----------------
st.sidebar.header("🕹️ Strategy & Timeline")
with st.sidebar:
    company_stage = st.selectbox("Company Stage", ["Idea", "Early Startup", "Growth", "Mature"])
    
    # TIMELINE: Controls the length of the Projections and the Liquidity Runway
    horizon_options = {"6 Months": 6, "12 Months": 12, "24 Months": 24, "60 Months": 60}
    selected_horizon = st.selectbox("Projection Timeline", list(horizon_options.keys()), index=1)
    forecast_months = horizon_options[selected_horizon]
    
    current_cash = st.number_input("Cash on Hand ($)", value=50000.0)
    growth_rate = st.slider("Target Monthly Growth (%)", 0.0, 20.0, 5.0)

# ----------------- 2. OPERATIONS INPUTS (Main Page) -----------------
col_in1, col_in2 = st.columns(2)
with col_in1:
    st.subheader("💰 Unit Economics")
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
total_salaries = employees * salary
total_fixed_burn = fixed_overhead + marketing + total_salaries
revenue = units * price
variable_total = units * v_cost
total_costs = total_fixed_burn + variable_total
net_profit = revenue - total_costs

# Contribution Margin and Break-even logic
contribution_margin = price - v_cost
be_units = total_fixed_burn / contribution_margin if contribution_margin > 0 else 0

# Liquidity/Runway calculation
runway = current_cash / abs(net_profit) if net_profit < 0 else float('inf')

# ----------------- 4. EXECUTIVE TABS -----------------
# We now have a dedicated tab for Liquidity
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Performance", 
    "💧 Liquidity & Runway", 
    "📈 Modeling", 
    "💰 Valuation", 
    "🤖 AI Advisor"
])

# --- TAB 1: PERFORMANCE (Break-Even Focus) ---
with tab1:
    st.subheader("Current Operational Efficiency")
    m1, m2 = st.columns(2)
    m1.metric("Monthly Net Profit", f"${net_profit:,.0f}")
    m2.metric("Break-Even Volume", f"{be_units:,.0f} Units")

    # Break-Even Chart
    u_range = np.linspace(0, max(units, be_units)*1.5, 100)
    fig_be = go.Figure()
    fig_be.add_trace(go.Scatter(x=u_range, y=u_range*price, name="Revenue", line=dict(color='blue')))
    fig_be.add_trace(go.Scatter(x=u_range, y=total_fixed_burn + (u_range*v_cost), name="Total Costs", line=dict(color='red')))
    fig_be.add_trace(go.Scatter(x=[units], y=[revenue], name="Current Status", marker=dict(size=12, color="green")))
    fig_be.update_layout(title="Break-Even Analysis crossover", template="plotly_white")
    st.plotly_chart(fig_be, use_container_width=True)

# --- TAB 2: LIQUIDITY & RUNWAY (Risk Focus) ---
with tab2:
    st.subheader("Solvency & Cash Risk Analysis")
    l1, l2, l3 = st.columns(3)
    l1.metric("Cash on Hand", f"${current_cash:,.0f}")
    l2.metric("Monthly Burn Rate", f"${total_fixed_burn:,.0f}")
    l3.metric("Survival Runway", f"{runway:.1f} Months" if runway != float('inf') else "Indefinite", delta_color="inverse")

    # Liquidity exhaustion chart
    st.write(f"**Cash Depletion Forecast over {selected_horizon}**")
    timeline = list(range(forecast_months + 1))
    cash_vals = [max(0, current_cash + (net_profit * m)) for m in timeline]
    fig_liq = px.area(x=timeline, y=cash_vals, labels={'x': 'Months from Today', 'y': 'Cash Balance ($)'})
    fig_liq.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Cash Zero Point")
    fig_liq.update_layout(template="plotly_white")
    st.plotly_chart(fig_liq, use_container_width=True)

# --- TAB 3: MODELING (Growth Projections) ---
with tab3:
    st.subheader(f"{selected_horizon} Revenue & Profit Trajectory")
    months = list(range(1, forecast_months + 1))
    p_rev, p_prof = [], []
    curr_u = units
    for m in months:
        curr_u *= (1 + growth_rate/100)
        r = curr_u * price
        c = total_fixed_burn + (curr_u * v_cost)
        p_rev.append(r)
        p_prof.append(r - c)
    
    df_p = pd.DataFrame({"Month": months, "Revenue": p_rev, "Profit": p_prof})
    fig_modeling = px.line(df_p, x="Month", y=["Revenue", "Profit"], markers=True, 
                           title="Projected Path to Scalability")
    fig_modeling.update_layout(template="plotly_white")
    st.plotly_chart(fig_modeling, use_container_width=True)

# --- TAB 4: VALUATION (Adaptive Methodology) ---
with tab4:
    st.subheader("Enterprise Valuation Strategy")
    if company_stage == "Idea":
        val_method, valuation = "VC Heuristic", current_cash * 5
    elif net_profit <= 0:
        val_method, valuation = "Revenue Multiple (2x)", (revenue * 12) * 2
    elif company_stage == "Growth":
        val_method, valuation = "Growth Multiple (5x)", (revenue * 12) * 5
    else: # Mature Profitable
        val_method, valuation = "DCF Model", (net_profit * 12) / 0.15 

    st.metric(f"Valuation: {val_method}", f"${valuation:,.2f}")
    st.info(f"This methodology is tailored to the {company_stage} stage of the business lifecycle.")

# --- TAB 5: AI ADVISOR ---
with tab5:
    if st.button("Generate Strategy Brief"):
        if api_key:
            prompt = f"Analyze: Stage {company_stage}, Profit {net_profit}, Runway {runway}. Give 3 CEO steps."
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            res = requests.post(url, json={"contents":[{"parts":[{"text": prompt}]}]})
            st.success(res.json()['candidates'][0]['content']['parts'][0]['text'])
