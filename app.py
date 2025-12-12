import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- Page Config ---
st.set_page_config(page_title="AI CFO: Business Intelligence Dashboard", layout="wide", page_icon="koi")

# --- Title ---
st.title("AI CFO: The Roadmap to Profitability 🚀")
st.markdown("### A Live Financial Intelligence System for Startups")

# --- SIDEBAR: ALL INPUTS ---
st.sidebar.header("1. Business Metrics")
fixed_cost = st.sidebar.number_input("Fixed Costs ($/month)", value=25000.0, step=1000.0)
var_cost = st.sidebar.number_input("Variable Cost per Unit ($)", value=10.0, step=1.0)
price_per_unit = st.sidebar.number_input("Selling Price per Unit ($)", value=20.0, step=1.0)
units_sold = st.sidebar.number_input("Projected Units Sold", value=4000, step=100)

st.sidebar.markdown("---")
st.sidebar.header("2. Financial Conditions")
current_cash = st.sidebar.number_input("Current Cash on Hand ($)", value=50000.0, step=5000.0, help="For Liquidity Analysis")
growth_rate = st.sidebar.slider("Expected Monthly Growth (%)", 0, 20, 5, help="For Projections")
discount_rate = st.sidebar.slider("Risk/Discount Rate (%)", 5, 20, 10, help="For DCF Valuation")

# --- CORE CALCULATIONS ---
total_revenue = units_sold * price_per_unit
total_variable_cost = units_sold * var_cost
total_cost = fixed_cost + total_variable_cost
net_profit = total_revenue - total_cost

# Break Even Calculation
if (price_per_unit - var_cost) > 0:
    break_even_units = fixed_cost / (price_per_unit - var_cost)
    break_even_revenue = break_even_units * price_per_unit
else:
    break_even_units = float('inf')
    break_even_revenue = float('inf')

# --- TABS FOR THE EXPO PRESENTATION ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Break-Even Analysis", "💧 Liquidity & Runway", "📈 Future Modeling", "💰 DCF Valuation"])

# --- TAB 1: EXISTING BREAK-EVEN (Refined) ---
with tab1:
    st.header("Snapshot: Current Performance")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("Total Costs", f"${total_cost:,.2f}")
    
    profit_color = "normal" if net_profit >= 0 else "inverse"
    col3.metric("Net Profit/Loss", f"${net_profit:,.2f}", delta_color=profit_color)
    col4.metric("Break-Even Units", f"{break_even_units:,.0f} Units")

    # Chart
    st.subheader("Interactive Break-Even Plot")
    
    # Generate data for the plot
    units_range = np.linspace(0, max(units_sold * 1.5, break_even_units * 1.5), 100)
    rev_line = units_range * price_per_unit
    cost_line = fixed_cost + (units_range * var_cost)

    fig = go.Figure()
    # Green for Revenue, Red for Costs
    fig.add_trace(go.Scatter(x=units_range, y=rev_line, mode='lines', name='Revenue', line=dict(color='#10B981', width=3)))
    fig.add_trace(go.Scatter(x=units_range, y=cost_line, mode='lines', name='Total Costs', line=dict(color='#EF4444', width=3, dash='dash')))
    
    # Add current position marker
    fig.add_trace(go.Scatter(x=[units_sold], y=[total_revenue], mode='markers', name='Current Status', marker=dict(color='blue', size=12)))
    # Add Break-even marker
    fig.add_trace(go.Scatter(x=[break_even_units], y=[break_even_revenue], mode='markers', name='Break-Even Point', marker=dict(color='orange', size=12)))

    # CHANGED TO WHITE TEMPLATE
    fig.update_layout(title="Cost vs Revenue Structure", xaxis_title="Units Sold", yaxis_title="Amount ($)", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: LIQUIDITY ANALYSIS (New) ---
with tab2:
    st.header("Liquidity: Survival Analysis")
    st.write("This module analyzes if the business has enough cash to survive without sales.")
    
    # Calculate Runway
    monthly_burn = fixed_cost # Assuming fixed cost is what you MUST pay
    if monthly_burn > 0:
        runway_months = current_cash / monthly_burn
    else:
        runway_months = 0
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Cash on Hand", f"${current_cash:,.2f}")
        st.metric("Monthly Burn Rate (Fixed)", f"${monthly_burn:,.2f}")
    
    with c2:
        # Visualizing Runway
        st.subheader(f"Runway: {runway_months:.1f} Months")
        
        # Gauge Chart for Runway
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = runway_months,
            title = {'text': "Months of Survival (Zero Sales)"},
            gauge = {
                'axis': {'range': [0, 12]},
                'bar': {'color': "#3B82F6"},
                'steps': [
                    {'range': [0, 3], 'color': "#EF4444"},
                    {'range': [3, 6], 'color': "gold"},
                    {'range': [6, 12], 'color': "#10B981"}],
            }
        ))
        # REMOVED DARK BACKGROUND
        fig_gauge.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    if runway_months < 3:
        st.error("⚠️ CRITICAL WARNING: Low Runway. Immediate capital injection or cost cutting required.")
    else:
        st.success("✅ HEALTHY: Business has sufficient liquidity for the short term.")

# --- TAB 3: FINANCIAL MODELING (New) ---
with tab3:
    st.header("Financial Modeling: 12-Month Projection")
    st.write(f"Projection based on a **{growth_rate}% monthly growth rate** in sales volume.")

    # Create Dynamic Data
    months = list(range(1, 13))
    proj_units = []
    proj_revenue = []
    proj_cost = []
    proj_profit = []

    current_units = units_sold
    
    for m in months:
        # Grow units
        current_units = current_units * (1 + (growth_rate/100))
        
        # Calculate financials
        rev = current_units * price_per_unit
        cost = fixed_cost + (current_units * var_cost)
        profit = rev - cost
        
        proj_units.append(current_units)
        proj_revenue.append(rev)
        proj_cost.append(cost)
        proj_profit.append(profit)

    # Create DataFrame for plotting
    df_proj = pd.DataFrame({
        "Month": months,
        "Revenue": proj_revenue,
        "Total Cost": proj_cost,
        "Net Profit": proj_profit
    })

    # Plot - CHANGED TO WHITE TEMPLATE
    fig_proj = px.line(df_proj, x="Month", y=["Revenue", "Total Cost", "Net Profit"], 
                       title="12-Month Financial Trajectory", markers=True)
    fig_proj.update_layout(template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig_proj, use_container_width=True)

    st.info("💡 Note how the 'Net Profit' gap widens over time due to Economies of Scale (Fixed costs stay flat while revenue grows).")

# --- TAB 4: DCF MODEL (New) ---
with tab4:
    st.header("Valuation: Discounted Cash Flow (DCF)")
    st.write("Estimating the company's value based on future cash flows.")

    # DCF Logic
    # We will use the 'Net Profit' from the projection as a proxy for Free Cash Flow for this simplified expo model
    
    # 1. Annualize the current profit (Simple projection)
    annualized_profit = net_profit * 12 
    
    st.subheader(" Valuation Inputs")
    col_d1, col_d2 = st.columns(2)
    col_d1.metric("Current Annualized Profit", f"${annualized_profit:,.2f}")
    col_d2.metric("Discount Rate (Risk)", f"{discount_rate}%")

    # 2. Calculate DCF for 5 Years
    future_cash_flows = []
    discount_factors = []
    present_values = []

    years = [1, 2, 3, 4, 5]
    
    # Assumption: Year over Year growth matches the monthly growth inputs roughly (simplified for demo)
    yearly_growth = growth_rate  

    running_cash_flow = annualized_profit

    for year in years:
        running_cash_flow = running_cash_flow * (1 + (yearly_growth/100))
        df = 1 / ((1 + (discount_rate/100)) ** year)
        pv = running_cash_flow * df
        
        future_cash_flows.append(running_cash_flow)
        discount_factors.append(df)
        present_values.append(pv)

    # Terminal Value (Value beyond year 5) - Simplified Gordon Growth
    terminal_growth = 0.03 # 3% long term growth
    terminal_value = (future_cash_flows[-1] * (1 + terminal_growth)) / ((discount_rate/100) - terminal_growth)
    terminal_value_discounted = terminal_value / ((1 + (discount_rate/100)) ** 5)

    total_valuation = sum(present_values) + terminal_value_discounted

    st.markdown("---")
    st.metric(label="💰 ESTIMATED COMPANY VALUATION", value=f"${total_valuation:,.2f}", 
              delta="Based on 5-Year DCF Model")
    
    st.write("### Cash Flow Breakdown")
    df_dcf = pd.DataFrame({
        "Year": years,
        "Projected Cash Flow": future_cash_flows,
        "Present Value (Today's Money)": present_values
    })
    st.dataframe(df_dcf.style.format("${:,.2f}"))

# --- DATASET VIEW (Kept from old project for reference) ---
with st.expander("📂 View Source Data (BreakEvenDB.csv)"):
    try:
        df = pd.read_csv('BreakEvenDB.csv')
        st.dataframe(df)
    except:
        st.warning("BreakEvenDB.csv not found. Using simulation mode.")
