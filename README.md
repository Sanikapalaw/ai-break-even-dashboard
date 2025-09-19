# 📊 The AI Roadmap to Profitability: Predictive Break-Even Analysis

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)  
[![Streamlit](https://img.shields.io/badge/Streamlit-App-green)](https://streamlit.io/)  
[![License](https://img.shields.io/badge/License-MIT-orange)](LICENSE)

---

## 🔹 Project Overview

This project is an **AI-powered financial planning tool** that predicts your **break-even point** and classifies outcomes into:

- **Profit** 💰  
- **Loss** 📉  
- **Break-even** ⚖️  

Unlike traditional spreadsheets, this project leverages **Machine Learning and interactive dashboards** to deliver **real-time insights** for smarter decision-making.

**Key Objectives:**
- Support small and medium-sized enterprises (SMEs) in financial planning.  
- Automate break-even calculations and predictive analysis.  
- Provide actionable recommendations to improve profitability.  

---

## 🔹 Problem Statement

Many businesses, especially SMEs, face challenges in **accurately analyzing their financial performance**:  

- Manual calculations are **time-consuming and error-prone**.  
- Static spreadsheets provide **no predictive insights**.  
- Scenario testing is inflexible, delaying decisions.  

This can lead to:  
- Misaligned pricing and sales strategies.  
- Poor cost management.  
- Uncertainty in achieving profitability.  

**Solution:**  
An **AI-driven interactive dashboard** that predicts financial outcomes and provides **real-time recommendations** to maximize profit and minimize loss.

---

## 🔹 Features

1. **Real-Time Break-Even Analysis**  
   - Enter your business metrics and instantly see break-even status.  

2. **Profit & Loss Classification**  
   - ML models classify your financial outcome as Profit, Loss, or Break-even.  

3. **AI-Powered Insights**  
   - Get recommendations on pricing, cost reduction, and sales strategy.  

4. **Interactive Visualizations**  
   - Charts and graphs make financial data easy to understand.  

---

## 🔹 Technologies Used

- **Python 3.11**  
- **Pandas, NumPy, Matplotlib, Seaborn** – Data analysis & visualization  
- **Scikit-learn & XGBoost** – Machine learning  
- **Streamlit** – Interactive dashboard for user input and predictions  
- **Joblib** – Model serialization  
- **Google Colab** – Development environment  

---

## 🔹 Installation & Setup

1. Clone the repository:  
```bash
git clone https://github.com/yourusername/ai-break-even-analysis.git
cd ai-break-even-analysis

2. Install dependencies:
pip install -r requirements.txt

3. Run the dashboard:
streamlit run app.py

## 🔹 Usage

Input your financial metrics:

Fixed costs

Variable cost per unit

Price per unit

Units sold

Marketing spend

Employee count

View the Predicted Outcome:

Profit, Loss, or Break-even

Total revenue, total cost, and net profit/loss

Analyze AI-powered recommendations to optimize profitability.

🔹 Data & EDA Highlights

Distribution of Key Financial Metrics

Contribution Margin Analysis: Price per Unit – Variable Cost per Unit

Price vs Variable Cost Scatter Plot showing profit and loss zones

Marketing spend vs Units Sold Analysis

Correlation Heatmaps highlighting factors most affecting profitability

🔹 Machine Learning Models
Model	Accuracy	Notes
Random Forest	97%	Baseline model, robust predictions
XGBoost	98.7%	Advanced model, higher accuracy for real-world data

Confusion matrices show the models correctly identify profit and loss scenarios with high reliability.

🔹 Saving Models for Deployment
import joblib

joblib.dump(rf_model, "random_forest_model.pkl")
joblib.dump(xgb_model, "xgboost_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(le, "label_encoder.pkl")


These files are used in the Streamlit dashboard for real-time predictions.

🔹 Screenshots

Profit Scenario:
## Profit Scenario

![Profit 1](assets/profit1.png)
![Profit 2](assets/profit2.png)
![Profit 3](assets/profit3.png)

## Loss Scenario

![Loss 1](assets/loss1.png)
![Loss 2](assets/loss2.png)
![Loss 3](assets/loss3.png)
![Loss 4](assets/loss4.png)

<img width="2559" height="1088" alt="image" src="https://github.com/user-attachments/assets/4e822b31-c366-4407-a9c9-76ce819f60c8" />
<img width="2558" height="840" alt="image" src="https://github.com/user-attachments/assets/e319131f-1968-4379-beba-a08de3a4e084" />
<img width="2154" height="1285" alt="image" src="https://github.com/user-attachments/assets/0ade513b-4132-4ae5-85dc-a22c053b076b" />

Loss Scenario:
<img width="2537" height="1251" alt="image" src="https://github.com/user-attachments/assets/d364039a-f5b4-489f-b073-653cbd00d3be" />
<img width="2553" height="826" alt="image" src="https://github.com/user-attachments/assets/cc54ee8b-6543-429f-bf20-282f7c0c9889" />
<img width="1971" height="1299" alt="image" src="https://github.com/user-attachments/assets/edf233bf-77f7-415f-9b0c-86d4252d8534" />
<img width="2054" height="342" alt="image" src="https://github.com/user-attachments/assets/b84d2b20-2f87-4747-8a8c-c440c87fcaa6" />





🔹 Future Work

Integrate real-time market data for predictions.

Support multi-product scenario simulation.

Enhance AI insights with actionable strategies for cost reduction and sales optimization.

🔹 Live Demo & Links

Streamlit App: https://ai-break-even-dashboard.streamlit.app/

Linkldn Link: 
