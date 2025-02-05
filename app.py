import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# Set up database connection
DATABASE_URL = "postgresql://jim:HGxcoyUGmxkmRJcqoA0fsleiTDZmRwN7@dpg-cuh7201u0jms73fvj8j0-a.virginia-postgres.render.com/liquor_db"
engine = create_engine(DATABASE_URL)

@st.cache_data
def load_data():
    query = "SELECT trans_id, product_id, transaction_date, sale_quantity, total_price, transaction_type FROM fact_sales;"
    query2 = "SELECT product_id, product_name, product_size, product_price, product_group FROM dim_products;"
    
    df_sales = pd.read_sql(query, engine)
    df_products = pd.read_sql(query2, engine)
    
    df_sales["transaction_date"] = pd.to_datetime(df_sales["transaction_date"])  # ✅ Ensure date format
    merged_df = df_sales.merge(df_products, on="product_id", how="left")
    
    return merged_df

# Load Data
df = load_data()

# **Date Filter**
st.sidebar.subheader("📅 Filter by Date")
min_date = df["transaction_date"].min().date()
max_date = df["transaction_date"].max().date()
selected_dates = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# Ensure two dates are selected
if isinstance(selected_dates, list) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    filtered_df = df[(df["transaction_date"].dt.date >= start_date) & (df["transaction_date"].dt.date <= end_date)]
else:
    filtered_df = df  # If no date is selected, show all data

# **Sales Over Time Chart**
st.subheader("📈 Sales Over Time")
fig = px.line(filtered_df, x="transaction_date", y="total_price", title="Total Sales Over Time")
st.plotly_chart(fig, use_container_width=True)

# **Top Selling Products Chart**
st.subheader("🏆 Top 10 Products")
top_products = filtered_df.groupby("product_name")["total_price"].sum().nlargest(10).reset_index()
fig2 = px.bar(top_products, x="product_name", y="total_price", title="Top 10 Products", text_auto=True)
st.plotly_chart(fig2, use_container_width=True)

# **Display Data Table**
st.subheader("📊 Raw Data")
st.dataframe(filtered_df)