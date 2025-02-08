import streamlit as st
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
            p.category_id AS product_category_id,
            TO_CHAR(f.transaction_date, 'YYYY-MM-DD') AS date, 
            EXTRACT(HOUR FROM f.transaction_date) AS trans_hour,
            EXTRACT(WEEK FROM f.transaction_date) AS week_num,  
            c.product_subdepartment,
            c.category_id 
        FROM fact_sales f 
        LEFT JOIN dim_products p ON f.product_id = p.product_id
        LEFT JOIN dim_categories c ON p.category_id = c.category_id;
    """
    
    df = pd.read_sql(query, engine)

    # Convert date column to proper format
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    
    return df

# Load Data
df = load_data()

# **Column Layout Preservation**
col1, col2, col3 = st.columns([3,3,3], vertical_alignment="top")
col4, col5 = st.columns((2,1))
col6, col7 = st.columns((1,1))

# **Dynamic Filters**
date_filter = st.sidebar.multiselect('Select Date', df['date'].dt.date.unique())
group_filter = st.sidebar.multiselect('Select Product Group', df['product_group'].unique())
product_filter = st.sidebar.multiselect('Select Product Name', df['product_name'].unique())

# **Apply Filters**
if not date_filter and not group_filter and not product_filter:
    filtered_df = df
else:
    filtered_df = df[
        (df['product_group'].isin(group_filter)) | 
        (df['date'].isin(date_filter)) | 
        (df['product_name'].isin(product_filter))
    ]

with st.container():
    # **Weekly Sales Graph (Filters by the Selected Date’s Week)**
    if date_filter:
        selected_week = df[df["date"].isin(date_filter)]["week_num"].iloc[0]  # Get the week number of the selected date
        weekly_sales_df = df[df["week_num"] == selected_week].groupby("date")["total_price"].sum().reset_index()
    else:
        weekly_sales_df = df.groupby("date")["total_price"].sum().reset_index()

    col4.subheader("📅 Weekly Sales for Selected Date")
    fig_weekly = px.line(weekly_sales_df, x="date", y="total_price", title="Total Sales by Day in Selected Week")
    col4.plotly_chart(fig_weekly, use_container_width=True)

    # **Top Selling Products Chart**
    if product_filter:
        selected_product = product_filter[0]  # Take the first selected product

        # Find transactions where the selected product was purchased
        transactions_with_selected = df[df["product_name"] == selected_product]["trans_id"].unique()

        # Find other products bought in the same transactions
        related_items = df[df["trans_id"].isin(transactions_with_selected) & (df["product_name"] != selected_product)]

        # Count most commonly co-purchased products
        top_related_items = related_items["product_name"].value_counts().sort_values(ascending=True).reset_index()
        top_related_items.columns = ["product_name", "count"]

        col7.subheader(f"🛒 Most Commonly Purchased with '{selected_product}'")
        if not top_related_items.empty:
            fig = px.bar(top_related_items.head(10), x="count", y="product_name", title="Top 10 Co-Purchased Items", text_auto=True, orientation='h')
            col7.plotly_chart(fig, use_container_width=True)
    else:
        col7.subheader("🏆 Top 10 Products")
        top_products = filtered_df.groupby("product_name")["total_price"].sum().nlargest(10).sort_values(ascending=False).reset_index()
        fig2 = px.bar(top_products, x="total_price", y="product_name", text_auto=True, orientation="h")
        col7.plotly_chart(fig2, use_container_width=True)

# **Metrics Display**
def format(value):
    return f"${value:,.2f}"

def format_quantity(value):
    return f"{value:,.0f}"

col1.metric("Total Transactions", value=format_quantity(filtered_df.shape[0]), delta=0)
col2.metric("Total Sales", value=format(round(filtered_df["total_price"].sum(),2)), delta=0)
col3.metric("Average Order Size", value=format(round((filtered_df["total_price"].sum()/filtered_df.shape[0]),2)), delta=0)

# **Hourly Sales Graph (Filters by Selected Date)**
with st.container():
    if date_filter:
        hourly_sales_df = df[df["date"].isin(date_filter)].groupby("trans_hour")["total_price"].sum().reset_index()
    else:
        hourly_sales_df = df.groupby("trans_hour")["total_price"].sum().reset_index()

    col6.subheader("⏳ Hourly Sales for Selected Date")
    fig_hourly = px.bar(hourly_sales_df, x="trans_hour", y="total_price", title="Total Sales by Hour")
    col6.plotly_chart(fig_hourly, use_container_width=True)

# **Pie Chart for Product Group or SubDepartment**
with st.container():
    if not group_filter:
        fig3 = px.pie(filtered_df, names='product_group', title='Sales by Product Group')
        col5.plotly_chart(fig3, use_container_width=True)
    else:
        fig3 = px.pie(filtered_df, names='product_subdepartment', title='Sales by Product SubDepartment')
        col5.plotly_chart(fig3, use_container_width=True)

# **Display Filtered Data Table**
with st.expander("📊 Transactions"):
    st.dataframe(filtered_df.groupby(['trans_id'])[['total_price', 'sale_quantity']].sum().reset_index())
