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
    growth_rate = st.slider("Expected Monthly Growth (%)", 0, 20, 5)
    discount_rate = st.slider("Valuation Discount Rate (%)", 5, 20, 10)

# ----------------- 2. CALCULATIONS -----------------
total_revenue = units_sold * price_per_unit
total_variable_cost = units_sold * variable_cost
total_costs = fixed_costs + total_variable_cost + marketing_spend
net_profit = total_revenue - total_costs
if (price_per_unit - variable_cost) > 0:
    break_even_units = (fixed_costs + marketing_spend) / (price_per_unit - variable_cost)
else:
    break_even_units = 0

# ----------------- 3. TABS -----------------
st.markdown("---")
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Break-Even", "💧 Liquidity", "📈 Modeling", "💰 Valuation", "🤖 AI Advisor"
])

# --- TAB 1, 2, 3, 4 (Standard Charts) ---
with tab1:
    st.metric("Net Profit", f"${net_profit:,.2f}")
    st.metric("Break-Even Units", f"{break_even_units:,.0f}")

with tab2:
    monthly_burn = fixed_costs + marketing_spend
    runway = current_cash / monthly_burn if monthly_burn > 0 else 0
    if runway < 3: st.error(f"⚠️ Critical: {runway:.1f} Months Runway")
    else: st.success(f"✅ Healthy: {runway:.1f} Months Runway")
    
    fig = go.Figure(go.Indicator(mode="gauge+number", value=runway, title={'text':"Months"}))
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    months = list(range(1, 13))
    rev_proj = [total_revenue * ((1 + growth_rate/100)**m) for m in months]
    fig_proj = px.line(x=months, y=rev_proj, title="12-Month Revenue Projection")
    st.plotly_chart(fig_proj, use_container_width=True)

with tab4:
    annual_growth = ((1 + (growth_rate/100)) ** 12) - 1
    pvs = []
    cf = net_profit * 12
    for y in range(1, 6):
        cf = cf * (1 + annual_growth)
        pvs.append(cf / ((1 + discount_rate/100)**y))
    val = sum(pvs) + (cf * 1.03 / (discount_rate/100 - 0.03)) / ((1 + discount_rate/100)**5)
    st.metric("Valuation (DCF)", f"${val:,.2f}")

# --- TAB 5: AI ADVISOR (ROBUST API VERSION) ---
with tab5:
    st.subheader("🤖 AI Financial Advisor")
    user_q = st.text_input("Ask a question:", "How can I improve my valuation?")
    
    if st.button("Get Answer"):
        with st.spinner("Connecting to Gemini..."):
            
            # 1. THE URL (Using the most standard name)
            model_name = "gemini-1.5-flash" 
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": f"You are a CFO. Data: Profit ${net_profit}, Cash ${current_cash}. Question: {user_q}"}]
                }]
            }
            
            try:
                # 2. SEND REQUEST
                response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
                
                # 3. SUCCESS?
                if response.status_code == 200:
                    ans = response.json()['candidates'][0]['content']['parts'][0]['text']
                    st.success("Success!")
                    st.markdown(ans)
                    
                # 4. FAILURE (404) -> DIAGNOSTIC MODE
                elif response.status_code == 404:
                    st.error(f"❌ Model '{model_name}' not found.")
                    st.info("🔍 Attempting to list available models for your key...")
                    
                    # Call the 'list models' endpoint
                    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                    list_resp = requests.get(list_url)
                    
                    if list_resp.status_code == 200:
                        models = list_resp.json().get('models', [])
                        valid_names = [m['name'].replace('models/', '') for m in models if 'generateContent' in m.get('supportedGenerationMethods', [])]
                        
                        st.warning("⚠️ YOUR AVAILABLE MODELS ARE:")
                        st.code(valid_names)
                        st.write("👉 Please edit line 87 in app.py to use one of these names.")
                    else:
                        st.error("Could not list models. Is your API Key valid?")
                        
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                st.error(f"Connection Error: {e}")
