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
col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    st.subheader("💰 Costs & Pricing")
    fixed_costs = st.number_input("Fixed Costs ($/Month)", value=25000.0, step=1000.0)
    variable_cost = st.number_input("Variable Cost per Unit ($)", value=10.0, step=1.0)
    price_per_unit = st.number_input("Price per Unit ($)", value=20.0, step=1.0)

with col_in2:
    st.subheader("📦 Sales & Operations")
    units_sold = st.number_input("Current Units Sold", value=4000, step=100)
    marketing_spend = st.number_input("Marketing Spend ($)", value=1000.0, step=100.0)
    employee_count = st.number_input("Employee Count", value=15)

with col_in3:
    st.subheader("🔮 Modeling & Cash")
    current_cash = st.number_input("Cash on Hand ($)", value=50000.0, step=5000.0)
    discount_rate = st.slider("Valuation Discount Rate (%)", 5, 20, 10)
    
    st.markdown("---")
    
    # --- FEATURE 1: Growth Rate Toggle (Monthly vs Annual) ---
    growth_mode = st.radio("Growth Rate Input:", ["Monthly %", "Annual %"], horizontal=True)
    
    if growth_mode == "Monthly %":
        raw_growth = st.slider("Expected Monthly Growth (%)", 0.0, 20.0, 5.0, step=0.5)
        # Convert to Annual for Valuation
        monthly_growth_rate = raw_growth
        annual_growth_rate = ((1 + (raw_growth/100)) ** 12) - 1
    else:
        raw_growth = st.slider("Expected Annual Growth (%)", 0.0, 200.0, 80.0, step=5.0)
        # Convert to Monthly for Projections
        annual_growth_rate = raw_growth / 100
        monthly_growth_rate = ((1 + annual_growth_rate) ** (1/12) - 1) * 100

    # --- FEATURE 2: Forecast Horizon Dropdown ---
    st.write(" **Chart View:**")
    horizon_options = {
        "6 Months (Short Term)": 6,
        "12 Months (1 Year)": 12, 
        "24 Months (2 Years)": 24, 
        "60 Months (5 Years)": 60
    }
    selected_horizon = st.selectbox("Select Forecast Duration", list(horizon_options.keys()), index=1) # Default to 12 Months
    forecast_months = horizon_options[selected_horizon]

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

    st.subheader("Interactive Break-Even Plot")
    
    plot_max = units_sold * 2
    if break_even_units != float('inf'):
        plot_max = max(units_sold * 1.5, break_even_units * 1.5)
    
    units_range = np.linspace(0, plot_max, 100)
    rev_line = units_range * price_per_unit
    cost_line = fixed_costs + marketing_spend + (units_range * variable_cost)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=units_range, y=rev_line, mode='lines', name='Revenue', line=dict(color='#10B981', width=3)))
    fig.add_trace(go.Scatter(x=units_range, y=cost_line, mode='lines', name='Total Costs', line=dict(color='#EF4444', width=3, dash='dash')))
    fig.add_trace(go.Scatter(x=[units_sold], y=[total_revenue], mode='markers', name='Current Status', marker=dict(color='blue', size=15)))
    
    if break_even_units != float('inf'):
        fig.add_trace(go.Scatter(x=[break_even_units], y=[break_even_units * price_per_unit], mode='markers', name='Break-Even Point', marker=dict(color='orange', size=15)))

    fig.update_layout(title="Cost vs Revenue Structure", xaxis_title="Units Sold", yaxis_title="Amount ($)", height=500)
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: LIQUIDITY ---
with tab2:
    st.subheader("Liquidity: How long can we survive?")
    
    monthly_burn = fixed_costs + marketing_spend
    runway_months = current_cash / monthly_burn if monthly_burn > 0 else 0
    
    col_l1, col_l2 = st.columns([1, 2]) 
    
    with col_l1:
        st.metric("Cash on Hand", f"${current_cash:,.2f}")
        st.metric("Monthly Burn Rate", f"${monthly_burn:,.2f}")
        if runway_months < 3:
            st.error(f"⚠️ CRITICAL: {runway_months:.1f} Months")
        elif runway_months < 6:
            st.warning(f"⚠️ CAUTION: {runway_months:.1f} Months")
        else:
            st.success(f"✅ HEALTHY: {runway_months:.1f} Months")

    with col_l2:
        # Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = runway_months,
            title = {'text': "Runway (Months)"},
            gauge = {
                'axis': {'range': [0, 12]},
                'bar': {'color': "black"},
                'steps': [
                    {'range': [0, 3], 'color': "#EF4444"},
                    {'range': [3, 6], 'color': "gold"},
                    {'range': [6, 12], 'color': "#10B981"}
                ],
            }
        ))
        fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Legend
        st.markdown("""
        <div style="text-align: center; background-color: #f9f9f9; padding: 10px; border-radius: 5px;">
            <span style="color: #EF4444; font-weight: bold;">🔴 Danger (0-3 Mo)</span> &nbsp;&nbsp;|&nbsp;&nbsp; 
            <span style="color: #EAB308; font-weight: bold;">🟡 Warning (3-6 Mo)</span> &nbsp;&nbsp;|&nbsp;&nbsp; 
            <span style="color: #10B981; font-weight: bold;">🟢 Safe (6+ Mo)</span>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 3: PROJECTIONS ---
with tab3:
    st.subheader(f"Financial Modeling: {selected_horizon} Forecast")
    
    months = list(range(1, forecast_months + 1))
    
    proj_revenue = []
    proj_profit = []
    curr_u = units_sold
    
    for m in months:
        # Use calculated monthly_growth_rate
        curr_u = curr_u * (1 + (monthly_growth_rate/100))
        r = curr_u * price_per_unit
        c = fixed_costs + marketing_spend + (curr_u * variable_cost)
        p = r - c
        proj_revenue.append(r)
        proj_profit.append(p)
        
    df_proj = pd.DataFrame({"Month": months, "Revenue": proj_revenue, "Profit": proj_profit})
    
    fig_proj = px.line(df_proj, x="Month", y=["Revenue", "Profit"], 
                       title=f"Projection based on {raw_growth}% {growth_mode}", 
                       markers=True)
    
    fig_proj.update_traces(line=dict(dash='dash', width=2), marker=dict(size=8, symbol="circle-open"))
    
    st.plotly_chart(fig_proj, use_container_width=True)

# --- TAB 4: VALUATION ---
with tab4:
    st.subheader("Valuation: What is the business worth? (DCF Model)")
    annualized_profit = net_profit * 12
    
    col_val1, col_val2 = st.columns(2)
    
    if annualized_profit <= 0:
        st.warning("⚠️ Business is not profitable yet. DCF Valuation requires positive profit.")
    else:
        years = [1, 2, 3, 4, 5]
        pvs = []
        cf = annualized_profit
        for y in years:
            # Use calculated annual_growth_rate
            cf = cf * (1 + annual_growth_rate)
            pv = cf / ((1 + (discount_rate/100)) ** y)
            pvs.append(pv)
            
        terminal_growth = 0.03
        terminal_val = (cf * (1 + terminal_growth)) / ((discount_rate/100) - terminal_growth)
        terminal_pv = terminal_val / ((1 + (discount_rate/100)) ** 5)
        total_val = sum(pvs) + terminal_pv
        
        with col_val1:
            st.metric("Estimated Valuation", f"${total_val:,.2f}")
            st.caption(f"Based on approx {annual_growth_rate*100:.1f}% Annual Growth")

# --- TAB 5: AI ADVISOR ---
with tab5:
    st.subheader("🤖 AI Financial Advisor")
    user_q = st.text_input("Ask a question:", "How can I improve my valuation?")
    
    if st.button("Get Answer"):
        with st.spinner("Connecting to Gemini..."):
            model_name = "gemini-2.5-flash" 
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": f"""
                    You are a CFO. Analyze this data:
                    - Monthly Profit: ${net_profit:,.2f}
                    - Cash: ${current_cash:,.2f}
                    - Runway: {runway_months:.1f} months
                    - Growth Input: {raw_growth}% ({growth_mode})
                    User Question: {user_q}
                    Answer concisely.
                    """}]
                }]
            }
            
            try:
                response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
                if response.status_code == 200:
                    ans = response.json()['candidates'][0]['content']['parts'][0]['text']
                    st.success("Success!")
                    st.markdown(ans)
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")
