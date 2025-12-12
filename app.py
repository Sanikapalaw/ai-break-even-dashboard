import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ----------------- CONFIG -----------------
st.set_page_config(layout="wide", page_title="AI CFO: Ultimate Dashboard", page_icon="📈")

# ----------------- CUSTOM STYLE (Clean White Theme) -----------------
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    h1, h2, h3 { color: #111827; }
    .stMetric { background-color: #f3f4f6; padding: 10px; border-radius: 5px; border: 1px solid #e5e7eb; }
    </style>
    """, unsafe_allow_html=True)

# ----------------- TITLE -----------------
st.title("📈 AI CFO: The Roadmap to Profitability")
st.markdown("### Liquidity • Financial Modeling • Valuation • AI Insights")
st.markdown("---")

# ----------------- 1. UNIVERSAL INPUTS (Center of Screen) -----------------
st.header("1. Enter Your Business Metrics")
st.info("👇 Change these values to see all charts update instantly.")

# Creating 3 Columns for inputs so it looks professional
col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    st.subheader("💰 Costs & Pricing")
    fixed_costs = st.number_input("Fixed Costs ($/Month)", min_value=0.0, value=25000.0, step=1000.0)
    variable_cost = st.number_input("Variable Cost per Unit ($)", min_value=0.0, value=10.0, step=1.0)
    price_per_unit = st.number_input("Price per Unit ($)", min_value=0.0, value=20.0, step=1.0)

with col_in2:
    st.subheader("📦 Sales & Operations")
    units_sold = st.number_input("Current Units Sold", min_value=0, value=4000, step=100)
    marketing_spend = st.number_input("Marketing Spend ($)", min_value=0.0, value=1000.0, step=100.0)
    employee_count = st.number_input("Employee Count", min_value=1, value=15)

with col_in3:
    st.subheader("🔮 Modeling & Cash")
    current_cash = st.number_input("Cash on Hand ($)", value=50000.0, step=5000.0, help="Used for Liquidity Runway")
    growth_rate = st.slider("Expected Monthly Growth (%)", 0, 20, 5, help="Used for Future Projections")
    discount_rate = st.slider("Valuation Discount Rate (%)", 5, 20, 10, help="Used for DCF Valuation")

# ----------------- 2. CORE CALCULATIONS -----------------
total_revenue = units_sold * price_per_unit
total_costs = fixed_costs + (variable_cost * units_sold)
net_profit = total_revenue - total_costs

# Break Even Logic
if (price_per_unit - variable_cost) > 0:
    break_even_units = fixed_costs / (price_per_unit - variable_cost)
    break_even_revenue = break_even_units * price_per_unit
else:
    break_even_units = float('inf')
    break_even_revenue = float('inf')

# ----------------- 3. DASHBOARD TABS -----------------
st.markdown("---")
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Break-Even Analysis", 
    "💧 Liquidity (Runway)", 
    "📈 Future Modeling", 
    "💰 Valuation (DCF)",
    "🤖 AI Advisor"
])

# --- TAB 1: BREAK-EVEN (Original) ---
with tab1:
    st.subheader("Snapshot: Current Performance")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"${total_revenue:,.2f}")
    c2.metric("Total Costs", f"${total_costs:,.2f}")
    c3.metric("Net Profit", f"${net_profit:,.2f}", delta_color="normal" if net_profit>=0 else "inverse")
    c4.metric("Break-Even Units", f"{break_even_units:,.0f}")

    # Plot
    st.subheader("Interactive Break-Even Plot")
    units_range = np.linspace(0, max(units_sold * 1.5, break_even_units * 1.5), 100)
    rev_line = units_range * price_per_unit
    cost_line = fixed_costs + (units_range * variable_cost)

    fig = go.Figure()
    # Green Revenue Line
    fig.add_trace(go.Scatter(x=units_range, y=rev_line, mode='lines', name='Revenue', line=dict(color='#10B981', width=3)))
    # Red Cost Line
    fig.add_trace(go.Scatter(x=units_range, y=cost_line, mode='lines', name='Total Costs', line=dict(color='#EF4444', width=3, dash='dash')))
    # Current Status Dot
    fig.add_trace(go.Scatter(x=[units_sold], y=[total_revenue], mode='markers', name='Current Status', marker=dict(color='blue', size=15)))
    # Break Even Dot
    if break_even_units != float('inf'):
        fig.add_trace(go.Scatter(x=[break_even_units], y=[break_even_revenue], mode='markers', name='Break-Even Point', marker=dict(color='orange', size=15)))

    fig.update_layout(title="Cost vs Revenue Structure", xaxis_title="Units Sold", yaxis_title="Amount ($)", template="plotly_white", height=500)
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: LIQUIDITY (New) ---
with tab2:
    st.subheader("Liquidity: How long can we survive?")
    
    monthly_burn = fixed_costs  # Conservative: Fixed costs are the minimum burn
    runway_months = current_cash / monthly_burn if monthly_burn > 0 else 0
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.metric("Cash on Hand", f"${current_cash:,.2f}")
        st.metric("Monthly Burn Rate", f"${monthly_burn:,.2f}")
    
    with col_l2:
        # Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = runway_months,
            title = {'text': "Runway (Months)"},
            gauge = {
                'axis': {'range': [0, 12]},
                'bar': {'color': "#3B82F6"},
                'steps': [
                    {'range': [0, 3], 'color': "#EF4444"},
                    {'range': [3, 6], 'color': "gold"},
                    {'range': [6, 12], 'color': "#10B981"}],
            }
        ))
        fig_gauge.update_layout(height=300, template="plotly_white")
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    if runway_months < 3:
        st.error("⚠️ CRITICAL: Less than 3 months of cash left!")
    else:
        st.success("✅ HEALTHY: Sufficient cash runway.")

# --- TAB 3: PROJECTIONS (New) ---
with tab3:
    st.subheader("Financial Modeling: 12-Month Forecast")
    st.write(f"Projection based on **{growth_rate}% monthly growth**.")
    
    # Generate Projection Data
    months = list(range(1, 13))
    proj_revenue = []
    proj_profit = []
    
    curr_u = units_sold
    for m in months:
        curr_u = curr_u * (1 + (growth_rate/100))
        r = curr_u * price_per_unit
        c = fixed_costs + (curr_u * variable_cost)
        p = r - c
        proj_revenue.append(r)
        proj_profit.append(p)
        
    df_proj = pd.DataFrame({"Month": months, "Revenue": proj_revenue, "Profit": proj_profit})
    
    fig_proj = px.line(df_proj, x="Month", y=["Revenue", "Profit"], title=f"Projection with {growth_rate}% Monthly Growth", markers=True)
    fig_proj.update_layout(template="plotly_white", height=500)
    st.plotly_chart(fig_proj, use_container_width=True)

# --- TAB 4: VALUATION (New) ---
with tab4:
    st.subheader("Valuation: What is the business worth?")
    
    annualized_profit = net_profit * 12
    if annualized_profit <= 0:
        st.error("Business is currently not profitable. DCF Valuation requires positive cash flow.")
    else:
        # Simple DCF
        years = [1, 2, 3, 4, 5]
        pvs = []
        
        cf = annualized_profit
        for y in years:
            cf = cf * (1 + (growth_rate/100)) # Simple annual growth assumption
            pv = cf / ((1 + (discount_rate/100)) ** y)
            pvs.append(pv)
            
        terminal_val = (cf * 1.03) / ( (discount_rate/100) - 0.03 )
        terminal_pv = terminal_val / ((1 + (discount_rate/100)) ** 5)
        
        total_val = sum(pvs) + terminal_pv
        
        st.metric("Estimated Company Value", f"${total_val:,.2f}", f"Based on {discount_rate}% Discount Rate")
        st.write("This uses a 5-Year Discounted Cash Flow (DCF) model assuming constant growth.")

# --- TAB 5: AI ADVISOR (Restored Demo) ---
with tab5:
    st.subheader("🤖 AI Financial Advisor")
    st.write("Ask questions about your data.")
    
    user_question = st.text_input("Ask something:", placeholder="How can I improve my runway?")
    
    if st.button("Get AI Answer"):
        # Simulated AI Response for Expo (Faster & Safer than Live API)
        st.info("AI Analysis:")
        st.markdown(f"""
        **Insight for your Business:**
        
        1. **Break-Even:** You need to sell **{break_even_units:,.0f} units** to cover costs.
        2. **Liquidity:** You have **{runway_months:.1f} months** of cash left.
        3. **Strategy:** To improve your margin, try increasing your price to **${price_per_unit + 2}** or reducing variable costs by negotiating with suppliers.
        """)
