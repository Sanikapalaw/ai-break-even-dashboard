import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import json

# ----------------- CONFIG -----------------
st.set_page_config(layout="wide", page_title="AI CFO: Ultimate Dashboard", page_icon="📈")



# ----------------- TITLE -----------------
st.title("📈 AI CFO: The Roadmap to Profitability")
st.markdown("### Liquidity • Financial Modeling • Valuation • AI Insights")
st.markdown("---")

# ----------------- API KEY HANDLING (Your Original Method) -----------------
# Try to get key from secrets first (Best for Cloud), then Sidebar (Best for Local/Expo)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = ""

if not api_key:
    with st.sidebar:
        st.warning("⚠️ API Key not found in secrets.")
        api_key = st.text_input("Enter Gemini API Key", type="password")

# ----------------- 1. UNIVERSAL INPUTS -----------------
st.header("1. Enter Your Business Metrics")
st.info("👇 Change these values to see all charts update instantly.")

col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    st.subheader("💰 Costs & Pricing")
    fixed_costs = st.number_input("Fixed Costs ($/Month)", min_value=0.0, value=25000.0, step=1000.0)
    variable_cost = st.number_input("Variable Cost per Unit ($)", min_value=0.0, value=10.0, step=1.0)
    price_per_unit = st.number_input("Price per Unit ($)", min_value=0.0, value=20.0, step=1.0)

with col_in2:
    st.subheader("📦 Sales & Operations")
    units_sold = st.number_input("Current Units Sold", min_value=0, value=4000, step=100)
    # Marketing spend is now included in total costs!
    marketing_spend = st.number_input("Marketing Spend ($)", min_value=0.0, value=1000.0, step=100.0)
    employee_count = st.number_input("Employee Count", min_value=1, value=15)

with col_in3:
    st.subheader("🔮 Modeling & Cash")
    current_cash = st.number_input("Cash on Hand ($)", value=50000.0, step=5000.0, help="Used for Liquidity Runway")
    growth_rate = st.slider("Expected Monthly Growth (%)", 0, 20, 5, help="Used for Future Projections")
    discount_rate = st.slider("Valuation Discount Rate (%)", 5, 20, 10, help="Used for DCF Valuation")

# ----------------- 2. CORE CALCULATIONS -----------------
total_revenue = units_sold * price_per_unit
total_variable_cost = units_sold * variable_cost
# Logic Correction: Adding Marketing Spend to Total Costs
total_costs = fixed_costs + total_variable_cost + marketing_spend
net_profit = total_revenue - total_costs

# Break Even Logic
if (price_per_unit - variable_cost) > 0:
    break_even_units = (fixed_costs + marketing_spend) / (price_per_unit - variable_cost)
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

# --- TAB 1: BREAK-EVEN ---
with tab1:
    st.subheader("Snapshot: Current Performance")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"${total_revenue:,.2f}")
    c2.metric("Total Costs", f"${total_costs:,.2f}")
    c3.metric("Net Profit", f"${net_profit:,.2f}", delta_color="normal" if net_profit>=0 else "inverse")
    c4.metric("Break-Even Units", f"{break_even_units:,.0f}")

    st.subheader("Interactive Break-Even Plot")
    units_range = np.linspace(0, max(units_sold * 1.5, break_even_units * 1.5), 100)
    rev_line = units_range * price_per_unit
    cost_line = fixed_costs + marketing_spend + (units_range * variable_cost)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=units_range, y=rev_line, mode='lines', name='Revenue', line=dict(color='#10B981', width=3)))
    fig.add_trace(go.Scatter(x=units_range, y=cost_line, mode='lines', name='Total Costs', line=dict(color='#EF4444', width=3, dash='dash')))
    fig.add_trace(go.Scatter(x=[units_sold], y=[total_revenue], mode='markers', name='Current Status', marker=dict(color='blue', size=15)))
    if break_even_units != float('inf'):
        fig.add_trace(go.Scatter(x=[break_even_units], y=[break_even_revenue], mode='markers', name='Break-Even Point', marker=dict(color='orange', size=15)))

    fig.update_layout(title="Cost vs Revenue Structure", xaxis_title="Units Sold", yaxis_title="Amount ($)", template="plotly_white", height=500)
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: LIQUIDITY ---
# --- TAB 2: LIQUIDITY (Updated with Warning System) ---
with tab2:
    st.subheader("Liquidity: How long can we survive?")
    
    monthly_burn = fixed_costs + marketing_spend
    runway_months = current_cash / monthly_burn if monthly_burn > 0 else 0
    
    # --- NEW: Dynamic Alert System ---
    if runway_months < 3:
        st.error(f"⚠️ CRITICAL ALERT: Only {runway_months:.1f} months of cash remaining! Immediate action required.")
    elif runway_months < 6:
        st.warning(f"⚠️ CAUTION: {runway_months:.1f} months of runway. Plan fundraising soon.")
    else:
        st.success(f"✅ HEALTHY: {runway_months:.1f} months of runway available.")
    # ---------------------------------
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.metric("Cash on Hand", f"${current_cash:,.2f}")
        st.metric("Monthly Burn Rate", f"${monthly_burn:,.2f}")
    
    with col_l2:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = runway_months,
            title = {'text': "Runway (Months)"},
            gauge = {
                'axis': {'range': [0, 12]},
                'bar': {'color': "black"},  # Changed needle to black for visibility
                'steps': [
                    {'range': [0, 3], 'color': "#EF4444"}, # Red Zone
                    {'range': [3, 6], 'color': "gold"},    # Yellow Zone
                    {'range': [6, 12], 'color': "#10B981"} # Green Zone
                ],
            }
        ))
        fig_gauge.update_layout(height=300, template="plotly_white")
        st.plotly_chart(fig_gauge, use_container_width=True)

#---with tab3
with tab3:
    st.subheader("Financial Modeling: 12-Month Forecast")
    
    months = list(range(1, 13))
    proj_revenue = []
    proj_profit = []
    
    curr_u = units_sold
    for m in months:
        curr_u = curr_u * (1 + (growth_rate/100))
        r = curr_u * price_per_unit
        c = fixed_costs + marketing_spend + (curr_u * variable_cost)
        p = r - c
        proj_revenue.append(r)
        proj_profit.append(p)
        
    df_proj = pd.DataFrame({"Month": months, "Revenue": proj_revenue, "Profit": proj_profit})
    
    fig_proj = px.line(df_proj, x="Month", y=["Revenue", "Profit"], title=f"Projection with {growth_rate}% Monthly Growth", markers=True)
    fig_proj.update_layout(template="plotly_white", height=500)
    st.plotly_chart(fig_proj, use_container_width=True)

# --- TAB 4: VALUATION ---
with tab4:
    st.subheader("Valuation: What is the business worth?")
    
    annualized_profit = net_profit * 12
    if annualized_profit <= 0:
        st.warning("⚠️ Business is not profitable. Valuation models work best with positive cash flow.")
    else:
        years = [1, 2, 3, 4, 5]
        pvs = []
        cf = annualized_profit
        for y in years:
            cf = cf * (1 + (growth_rate/100))
            pv = cf / ((1 + (discount_rate/100)) ** y)
            pvs.append(pv)
            
        terminal_val = (cf * 1.03) / ( (discount_rate/100) - 0.03 )
        terminal_pv = terminal_val / ((1 + (discount_rate/100)) ** 5)
        total_val = sum(pvs) + terminal_pv
        
        st.metric("Estimated Company Value (DCF)", f"${total_val:,.2f}")

# --- TAB 5: AI ADVISOR (Requests Method) ---
with tab5:
    st.subheader("🤖 AI Financial Advisor (Powered by Gemini)")
    st.write("Ask the AI about your financial health, risks, or strategy.")
    
    user_question = st.text_input("Ask something:", placeholder="How can I double my profit?")
    
    if st.button("Get AI Analysis"):
        if not api_key:
            st.error("⚠️ API Key missing. Please check your secrets or enter it in the sidebar.")
        else:
            with st.spinner("Analyzing your financial data..."):
                # Prepare Context
                context_prompt = f"""
                You are a CFO. Analyze this data:
                - Revenue: ${total_revenue}
                - Costs: ${total_costs}
                - Profit: ${net_profit}
                - Break-Even: {break_even_units} units
                - Cash: ${current_cash}
                - Runway: {runway_months} months
                
                User Question: "{user_question}"
                Answer strategically in bullet points.
                """
                
                # CALL API DIRECTLY (No library installation needed)
                # Using standard Gemini 1.5 Flash model
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                data = {"contents": [{"parts": [{"text": context_prompt}]}]}
                
                try:
                    response = requests.post(url, headers=headers, json=data)
                    if response.status_code == 200:
                        ai_text = response.json()['candidates'][0]['content']['parts'][0]['text']
                        st.success("Analysis Complete")
                        st.markdown(ai_text)
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")


