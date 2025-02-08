📊 Liquor Sales Dashboard

🚀 Project Overview

This project is a Streamlit-based Liquor Sales Dashboard that provides interactive visualizations and insights into sales transactions. The dashboard allows users to filter data by date, product group, and product name while analyzing weekly sales trends, hourly sales distribution, and commonly purchased products.

The app is deployed on Streamlit Cloud and connected to a PostgreSQL database hosted on Render.

🏗️ Features

📅 Date & Product Filters

Users can select a date, product group, or product name to filter the data dynamically.

The dashboard updates in real-time based on user selections.

📈 Sales Insights & Visualizations

Weekly Sales Graph: Displays total sales for the week of the selected date.

Hourly Sales Graph: Shows sales distribution by hour for the selected date.

Top Selling Products: Identifies the highest revenue-generating products.

Commonly Purchased Items: When a product is selected, shows other frequently bought items.

Sales Breakdown by Product Group: Interactive pie charts for product categories.

📊 Data & Metrics

Total Transactions: Number of orders in the filtered dataset.

Total Sales Revenue: Sum of all sales within the selected range.

Average Order Size: Sales per transaction to understand purchase behavior.

🛠️ Tech Stack

Frontend: Streamlit

Database: PostgreSQL (Hosted on Render)

Data Processing: Pandas, SQLAlchemy

Visualizations: Plotly

Deployment: Streamlit Cloud, GitHub

📂 Project Structure

Portfolio-Projects/
│-- Liquor Database/
│   │-- liq_db_daily_update.py   # Script for daily transaction generation
│   │-- liquor dataclean 2.ipynb  # Data cleaning notebook
│-- app.py       # Streamlit dashboard
│-- requirements.txt  # Dependencies for Streamlit Cloud
│-- README.md    # Project documentation

📌 Setup & Deployment

🔹 1. Clone the Repository

git clone https://github.com/jmcfadd91/Portfolio-Projects.git
cd Portfolio-Projects

🔹 2. Install Dependencies

If running locally, install required packages:

pip install -r requirements.txt

🔹 3. Set Up PostgreSQL Database

Ensure you have access to the PostgreSQL database hosted on Render. Update DATABASE_URL in app.py if needed.

🔹 4. Run the Streamlit App

streamlit run app.py

🔹 5. Deploy to Streamlit Cloud

Ensure requirements.txt is committed to GitHub.

Deploy via Streamlit Cloud by linking the repository.

Restart the app if dependencies don’t install correctly.

🛠️ Troubleshooting

❌ "ModuleNotFoundError: No module named 'plotly.express'"

✔️ Solution: Ensure requirements.txt contains plotly, then redeploy.

❌ "Branch does not exist"

✔️ Solution: Confirm branch is main and correctly set in Streamlit deployment settings.

❌ "This file does not exist"

✔️ Solution: Ensure app.py is in the root directory of the repository.

📧 Contact & Contributions

Author: James McFadden Jr.

GitHub: @jmcfadd91

Contributions & feedback are welcome! 🚀

