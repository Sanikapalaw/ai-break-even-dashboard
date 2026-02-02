import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests

# ----------------- CONFIG & DATA -----------------
st.set_page_config(layout="wide", page_title="AI CFO: Strategic Dashboard", page_icon="📈")

# Grounding the model in your 5,000-row static dataset
@st.cache_data
def load_historical_data():
    try:
        # Ensure the filename matches your uploaded file exactly
        df = pd.read_csv('BreakEvenDB.csv (3).csv')
        return df
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return None

hist_df = load_historical_data()

# Initialize sliders with historical averages (The "Static" grounding)
if hist_df is not None:
    init_price = float(hist_df['price_per_unit'].mean())
    init_var = float(hist_df['variable_cost_per_unit'].mean())
    init_fixed = float(hist_df['fixed_costs'].mean())
    init_vol = int(hist_df['units_sold'].mean())
    init_mkt = float(hist_df['marketing_spend'].mean())
    init_emp = int(hist_df['employee_count'].mean())
else:
    init_price, init_var, init_fixed, init_vol, init_mkt, init_emp = 20.0, 10.0, 25000.0, 4000, 1000.0, 15

# ----------------- TITLE -----------------
st.title("📈 AI CFO: The Roadmap to Profitability")
st.markdown(f"**Executive Decision-Support Engine** | Analyzed {len(hist_df) if hist_df is not None else 0:,} Historical Records")
st.markdown("---")

# ----------------- API KEY HANDLING -----------------
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key (Required for AI Advisor)", type="password")

# ----------------- 1. UNIVERSAL INPUTS (Dynamic Levers) -----------------
st.sidebar.header("🕹️ Strategic Controls")
with st.sidebar:
    company_stage = st.selectbox("Company Stage", ["Idea", "Early Startup", "Growth", "Mature"])
    current_cash = st.number_input("Cash on Hand ($)", value=50000.0, step=5000.0)
    growth_rate = st.slider("Target Monthly Growth (%)", 0.0, 20.0, 5.0)

col_in1, col_in2 = st.columns(2)

with col_in1:
    st.subheader("💰 Unit Economics")
    price = st.number_input("Price per Unit ($)", value=init_price)
    v_cost = st.number_input("Variable Cost per Unit ($)", value=init_var)
    units = st.number_input("Current Monthly Volume", value=init_vol)

with col_in2:
    st.subheader("🏢 Operational Burn")
    fixed_overhead = st.number_input("Fixed Costs ($/Mo)", value=init_fixed)
    marketing = st.number_input("Marketing Spend ($)", value=init_mkt)
    employees = st.number_input("Headcount", value=init_emp)
    salary = st.number_input("Avg Salary per Employee ($/Month)", value=3000.0)

# ----------------- 2. CORE CALCULATIONS -----------------
monthly_salaries = employees * salary
total_fixed_burn = fixed_overhead + marketing + monthly_salaries
revenue = units * price
total_variable = units * v_cost
total_costs = total_fixed_burn + total_variable
net_profit = revenue - total_costs

# Contribution Margin and Break-even logic
contribution_margin = price - v_cost
be_units = total_fixed_burn / contribution_margin if contribution_margin > 0 else 0

# Liquidity and Runway Logic
runway = current_cash / abs(net_profit) if net_profit < 0 else float('inf')

# ----------------- 3. EXECUTIVE TABS -----------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance & Liquidity", "📈 Projections", "💰 Valuation", "🤖 AI Advisor"])

# --- TAB 1: BREAK-EVEN & LIQUIDITY ---
with tab1:
    st.subheader("Financial Health Snapshot")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Net Profit", f"${net_profit:,.0f}")
    m2.metric("Break-Even Units", f"{be_units:,.0f}")
    m3.metric("Monthly Burn", f"${total_fixed_burn:,.0f}")
    m4.metric("Runway", f"{runway:.1f} Mo" if runway != float('inf') else "Stable", delta_color="inverse")

    col_be, col_liq = st.columns(2)
    
    with col_be:
        # Dynamic Break-even chart
        u_range = np.linspace(0, max(units, be_units)*1.5, 100)
        fig_be = go.Figure()
        fig_be.add_trace(go.Scatter(x=u_range, y=u_range*price, name="Revenue", line=dict(color='blue')))
        fig_be.add_trace(go.Scatter(x=u_range, y=total_fixed_burn + (u_range*v_cost), name="Total Costs", line=dict(color='red')))
        fig_be.add_trace(go.Scatter(x=[units], y=[revenue], name="Current Status", marker=dict(size=12, color="green")))
        fig_be.update_layout(title="Break-Even Analysis Chart", template="plotly_white")
        st.plotly_chart(fig_be, use_container_width=True)

    with col_liq:
        # Cash Depletion Forecast (Liquidity)
        timeline = list(range(13))
        cash_vals = [max(0, current_cash + (net_profit * m)) for m in timeline]
        fig_liq = px.area(x=timeline, y=cash_vals, title="12-Month Cash Depletion Forecast", labels={'x': 'Months', 'y': 'Cash ($)'})
        fig_liq.add_hline(y=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig_liq, use_container_width=True)

# --- TAB 3: VALUATION (Adaptive Methodology) ---
with tab3:
    st.subheader("Strategic Business Valuation")
    
    if company_stage == "Idea":
        val_method = "VC Heuristic"
        valuation = current_cash * 5 # Basic multiplier for early potential
    elif net_profit <= 0:
        # Solving the valuation problem with Revenue Multiples
        val_method = "Revenue Multiple (3x Annualized)"
        valuation = (revenue * 12) * 3 
    else:
        # Professional DCF Logic
        val_method = "Discounted Cash Flow (DCF)"
        valuation = (net_profit * 12) / 0.15 # Using 15% Cap Rate

    st.metric(f"Estimated Valuation ({val_method})", f"${valuation:,.2f}")
    st.info(f"Methodology Note: For {company_stage} companies, we apply {val_method} to ensure market-realistic results.")

# --- TAB 4: AI ADVISOR ---
with tab4:
    if st.button("Generate Executive Briefing"):
        if not api_key:
            st.error("Please provide an API Key in the sidebar.")
        else:
            prompt = f"As a PhD CFO, analyze: Stage {company_stage}, Profit {net_profit}, Burn {total_fixed_burn}, Runway {runway}. Provide 3 executive strategies."
            try:
                # Updated to use modern model naming
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                res = requests.post(url, json={"contents":[{"parts":[{"text": prompt}]}]})
                st.success(res.json()['candidates'][0]['content']['parts'][0]['text'])
            except Exception as e:
                st.error(f"AI Service error: {e}")
