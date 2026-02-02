import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests

# ----------------- CONFIG & DATA -----------------
st.set_page_config(layout="wide", page_title="AI CFO: Strategic Dashboard", page_icon="📉")

# Grounding the model in your 5,000-row static dataset
@st.cache_data
def load_data():
    df = pd.read_csv('BreakEvenDB.csv (3).csv')
    return df

try:
    hist_df = load_data()
    # Calculating averages to initialize the "Dynamic" part of the model
    avg_price = hist_df['price_per_unit'].mean()
    avg_var_cost = hist_df['variable_cost_per_unit'].mean()
    avg_fixed = hist_df['fixed_costs'].mean()
    avg_units = hist_df['units_sold'].mean()
    avg_marketing = hist_df['marketing_spend'].mean()
    avg_employees = hist_df['employee_count'].mean()
except Exception as e:
    st.error(f"Error loading CSV: {e}")
    st.stop()

# ----------------- TITLE & API -----------------
st.title("📈 AI CFO: The Roadmap to Profitability")
st.markdown(f"**Data Scientist Perspective:** Analyzing {len(hist_df):,} historical records to drive future strategy.")

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Gemini API Key (Required for AI Advisor)", type="password")

# ----------------- 1. STRATEGIC INPUTS (The Sliders) -----------------
st.sidebar.header("🕹️ Strategy Levers")
with st.sidebar:
    company_stage = st.selectbox("Company Stage", ["Idea", "Early Startup", "Growth", "Mature"])
    current_cash = st.number_input("Cash on Hand ($)", value=50000.0)
    monthly_growth = st.slider("Target Monthly Growth (%)", 0.0, 20.0, 5.0)

col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Unit Economics (Future)")
    price = st.number_input("Target Price per Unit ($)", value=float(avg_price))
    v_cost = st.number_input("Target Variable Cost ($)", value=float(avg_var_cost))
    volume = st.number_input("Target Sales Volume (Units)", value=int(avg_units))

with col2:
    st.subheader("🏢 Operating Structure")
    fixed = st.number_input("Fixed Overheads ($/Mo)", value=float(avg_fixed))
    marketing = st.number_input("Marketing Spend ($/Mo)", value=float(avg_marketing))
    employees = st.number_input("Headcount", value=int(avg_employees))
    salary = st.number_input("Avg Salary per Employee ($/Mo)", value=3000.0)

# ----------------- 2. CORE CALCULATIONS -----------------
total_salaries = employees * salary
total_burn = fixed + marketing + total_salaries # Fixed Costs
revenue = volume * price
variable_total = volume * v_cost
net_profit = revenue - (variable_total + total_burn) # EBITDA logic

# Break-Even Formula
contribution_margin = price - v_cost
be_units = total_burn / contribution_margin if contribution_margin > 0 else 0

# Liquidity Logic
runway = current_cash / abs(net_profit) if net_profit < 0 else 99

# ----------------- 3. EXECUTIVE TABS -----------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance & Liquidity", "📄 Dynamic P&L", "💰 Valuation", "🤖 AI Advisor"])

# --- TAB 1: CHARTS ---
with tab1:
    st.subheader("Profitability & Runway Analysis")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Projected Net Profit", f"${net_profit:,.0f}")
    m2.metric("Break-Even Volume", f"{be_units:,.0f} Units")
    m3.metric("Monthly Burn", f"${total_burn:,.0f}")
    m4.metric("Runway (Months)", f"{runway:.1f}", delta_color="inverse")

    c_left, c_right = st.columns(2)

    with c_left:
        # Break-Even Chart
        u_range = np.linspace(0, max(volume, be_units) * 1.5, 100)
        fig_be = go.Figure()
        fig_be.add_trace(go.Scatter(x=u_range, y=u_range * price, name="Revenue"))
        fig_be.add_trace(go.Scatter(x=u_range, y=total_burn + (u_range * v_cost), name="Total Costs"))
        fig_be.add_trace(go.Scatter(x=[volume], y=[revenue], name="Current Target", marker=dict(size=12, color="green")))
        fig_be.update_layout(title="Break-Even Point Visualization", template="plotly_white")
        st.plotly_chart(fig_be, use_container_width=True)

    with c_right:
        # Liquidity Runway Chart
        timeline = list(range(13))
        cash_flow = [max(0, current_cash + (net_profit * m)) for m in timeline]
        fig_liq = px.area(x=timeline, y=cash_flow, title="Cash Depletion Forecast (12 Months)")
        fig_liq.add_hline(y=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig_liq, use_container_width=True)

# --- TAB 2: P&L (The Dynamic Logic) ---
with tab2:
    st.subheader("Dynamic Pro-Forma P&L Statement")
    st.write("This statement recalculates instantly as you move the sliders.")
    pl_df = pd.DataFrame({
        "Line Item": ["Total Revenue", "Less: Variable Costs", "Gross Margin", "Operating Expenses", "Net Income"],
        "Amount ($)": [f"{revenue:,.2f}", f"({variable_total:,.2f})", f"{revenue - variable_total:,.2f}", f"({total_burn:,.2f})", f"{net_profit:,.2f}"]
    })
    st.table(pl_df)

# --- TAB 3: VALUATION ---
with tab3:
    st.subheader("Strategic Business Valuation")
    if company_stage == "Idea":
        val = current_cash * 5
        method = "VC Heuristic"
    elif net_profit <= 0:
        val = (revenue * 12) * 3 # 3x Revenue Multiple for non-profitable
        method = "Revenue Multiple (Growth Stage)"
    else:
        # Discounted Cash Flow
        val = (net_profit * 12) / 0.15 
        method = "Discounted Cash Flow (DCF)"
    
    st.metric(f"Estimated Valuation ({method})", f"${val:,.2f}")

# --- TAB 4: AI ADVISOR ---
with tab4:
    if st.button("Generate Executive Analysis"):
        if not api_key: st.error("Add API Key")
        else:
            prompt = f"CFO Analysis: Stage {company_stage}, Revenue {revenue}, Profit {net_profit}, Runway {runway}. Give 3 CEO-level strategies."
            res = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}", 
                                json={"contents":[{"parts":[{"text": prompt}]}]})
            st.success(res.json()['candidates'][0]['content']['parts'][0]['text'])
