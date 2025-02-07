import streamlit as st
from streamlit_dynamic_filters import DynamicFilters
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# Set up database connection
DATABASE_URL = "postgresql://jim:HGxcoyUGmxkmRJcqoA0fsleiTDZmRwN7@dpg-cuh7201u0jms73fvj8j0-a.virginia-postgres.render.com/liquor_db"
engine = create_engine(DATABASE_URL)

st.set_page_config(layout="wide")
@st.cache_data
def load_data():
    query = """
    SELECT 
        f.trans_id, 
        f.product_id AS sales_product_id,  
        f.transaction_date, 
        f.sale_quantity, 
        f.total_price, 
        f.transaction_type, 
        p.product_name, 
        p.product_size, 
        p.product_price, 
        p.product_group, 
        TO_CHAR(f.transaction_date, 'YYYY-MM-DD') AS date, 
        EXTRACT(hour FROM f.transaction_date) AS trans_hour,
        EXTRACT('week' FROM f.transaction_date) AS week_num
    FROM fact_sales f 
    LEFT JOIN dim_products p ON f.product_id = p.product_id;
    """
    
    df = pd.read_sql(query, engine)

    # Convert date column to proper format
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    
    return df

# Load Data
df = load_data()

col1, col2, col3 = st.columns([3,3,3],vertical_alignment="top")

# **Dynamic Filters**
date_filter = col1.multiselect('Select Date', df['date'].dt.date.unique())
group_filter = col2.multiselect('Select Product Group', df['product_group'].unique())
product_filter = col3.multiselect('Select Product Name', df['product_name'].unique())

if not date_filter and not group_filter and not product_filter:
    filtered_df = df
else:
    filtered_df = df[(df['product_group'].isin(group_filter)) | (df['date'].isin(date_filter)) | (df['product_name'].isin(product_filter))]
# **Hourly Sales Time Chart**
st.subheader("📈 Hourly Sales")
time_chart_df = filtered_df.groupby("trans_hour")["total_price"].sum().reset_index()
fig = px.bar(time_chart_df, x="trans_hour", y="total_price")
st.plotly_chart(fig, use_container_width=True)

# **Top Selling Products Chart**
st.subheader("🏆 Top 10 Products")
top_products = filtered_df.groupby("product_name")["total_price"].sum().nlargest(10).reset_index()
fig2 = px.bar(top_products, x="product_name", y="total_price", text_auto=True)
st.plotly_chart(fig2, use_container_width=True)

# **Metrics**
col1.metric("Total Transactions", value=filtered_df.shape[0], delta=0)
col2.metric("Total Sales", value=round(filtered_df["total_price"].sum(),2), delta=0)
col3.metric("Average Order Size", value=round((filtered_df["total_price"].sum()/filtered_df.shape[0]),2), delta=0)
# **Display Filtered Data Table**
with st.expander("📊 Filtered Data"):
    st.dataframe(filtered_df)