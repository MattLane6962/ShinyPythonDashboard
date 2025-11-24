import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")

@st.cache_data
def generate_sales_data():
    np.random.seed(42)
    
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 11, 24)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    products = ['Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Monitor', 'Keyboard', 'Mouse', 'Webcam']
    regions = ['North America', 'Europe', 'Asia', 'South America', 'Africa']
    categories = ['Electronics', 'Accessories', 'Computers', 'Audio']
    
    data = []
    for date in date_range:
        num_transactions = np.random.randint(5, 15)
        for _ in range(num_transactions):
            product = np.random.choice(products)
            
            if product in ['Laptop', 'Monitor']:
                category = 'Computers'
                price = np.random.uniform(500, 2000)
            elif product in ['Smartphone', 'Tablet']:
                category = 'Electronics'
                price = np.random.uniform(300, 1200)
            elif product in ['Headphones', 'Webcam']:
                category = 'Audio'
                price = np.random.uniform(50, 400)
            else:
                category = 'Accessories'
                price = np.random.uniform(20, 150)
            
            quantity = np.random.randint(1, 10)
            revenue = price * quantity
            
            data.append({
                'Date': date,
                'Product': product,
                'Category': category,
                'Region': np.random.choice(regions),
                'Quantity': quantity,
                'Unit_Price': round(price, 2),
                'Revenue': round(revenue, 2)
            })
    
    df = pd.DataFrame(data)
    return df

df = generate_sales_data()

st.title("📊 Sales Dashboard")
st.markdown("---")

with st.sidebar:
    st.header("🔍 Filters")
    
    date_range = st.date_input(
        "Select Date Range",
        value=(df['Date'].min(), df['Date'].max()),
        min_value=df['Date'].min().date(),
        max_value=df['Date'].max().date()
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range[0]
    
    selected_categories = st.multiselect(
        "Select Categories",
        options=sorted(df['Category'].unique()),
        default=sorted(df['Category'].unique())
    )
    
    selected_regions = st.multiselect(
        "Select Regions",
        options=sorted(df['Region'].unique()),
        default=sorted(df['Region'].unique())
    )
    
    selected_products = st.multiselect(
        "Select Products",
        options=sorted(df['Product'].unique()),
        default=sorted(df['Product'].unique())
    )

filtered_df = df[
    (df['Date'] >= pd.Timestamp(start_date)) &
    (df['Date'] <= pd.Timestamp(end_date)) &
    (df['Category'].isin(selected_categories)) &
    (df['Region'].isin(selected_regions)) &
    (df['Product'].isin(selected_products))
]

period_days = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days + 1
previous_start = pd.Timestamp(start_date) - timedelta(days=period_days)
previous_end = pd.Timestamp(start_date) - timedelta(days=1)

previous_df = df[
    (df['Date'] >= previous_start) &
    (df['Date'] <= previous_end) &
    (df['Category'].isin(selected_categories)) &
    (df['Region'].isin(selected_regions)) &
    (df['Product'].isin(selected_products))
]

current_revenue = filtered_df['Revenue'].sum()
previous_revenue = previous_df['Revenue'].sum()

if previous_revenue > 0:
    growth_rate = ((current_revenue - previous_revenue) / previous_revenue) * 100
else:
    growth_rate = 0

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_revenue = filtered_df['Revenue'].sum()
    st.metric("💰 Total Revenue", f"${total_revenue:,.2f}")

with col2:
    total_transactions = len(filtered_df)
    st.metric("🛒 Total Transactions", f"{total_transactions:,}")

with col3:
    avg_transaction = filtered_df['Revenue'].mean() if len(filtered_df) > 0 else 0
    st.metric("📈 Avg Transaction Value", f"${avg_transaction:,.2f}")

with col4:
    total_quantity = filtered_df['Quantity'].sum()
    st.metric("📦 Units Sold", f"{total_quantity:,}")

with col5:
    st.metric("📊 Revenue Growth", f"{growth_rate:,.1f}%", delta=f"{growth_rate:,.1f}%")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Revenue Over Time")
    daily_revenue = filtered_df.groupby('Date')['Revenue'].sum().reset_index()
    fig_line = px.line(
        daily_revenue,
        x='Date',
        y='Revenue',
        title='Daily Revenue Trend',
        labels={'Revenue': 'Revenue ($)', 'Date': 'Date'}
    )
    fig_line.update_layout(hovermode='x unified')
    st.plotly_chart(fig_line, width='stretch')

with col2:
    st.subheader("🎯 Revenue by Category")
    category_revenue = filtered_df.groupby('Category')['Revenue'].sum().reset_index()
    fig_pie = px.pie(
        category_revenue,
        values='Revenue',
        names='Category',
        title='Revenue Distribution by Category'
    )
    st.plotly_chart(fig_pie, width='stretch')

col3, col4 = st.columns(2)

with col3:
    st.subheader("🌍 Revenue by Region")
    region_revenue = filtered_df.groupby('Region')['Revenue'].sum().reset_index().sort_values('Revenue', ascending=False)
    fig_bar = px.bar(
        region_revenue,
        x='Region',
        y='Revenue',
        title='Revenue by Region',
        labels={'Revenue': 'Revenue ($)', 'Region': 'Region'},
        color='Revenue',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_bar, width='stretch')

with col4:
    st.subheader("🏆 Top Products by Revenue")
    product_revenue = filtered_df.groupby('Product')['Revenue'].sum().reset_index().sort_values('Revenue', ascending=False).head(8)
    fig_bar_products = px.bar(
        product_revenue,
        x='Revenue',
        y='Product',
        orientation='h',
        title='Top 8 Products by Revenue',
        labels={'Revenue': 'Revenue ($)', 'Product': 'Product'},
        color='Revenue',
        color_continuous_scale='Greens'
    )
    st.plotly_chart(fig_bar_products, width='stretch')

st.markdown("---")

st.subheader("📊 Detailed Sales Data")

display_df = filtered_df.copy()
display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
display_df = display_df.sort_values('Date', ascending=False)

st.dataframe(
    display_df,
    width='stretch',
    hide_index=True,
    column_config={
        "Revenue": st.column_config.NumberColumn(
            "Revenue",
            format="$%.2f"
        ),
        "Unit_Price": st.column_config.NumberColumn(
            "Unit Price",
            format="$%.2f"
        ),
        "Quantity": st.column_config.NumberColumn(
            "Quantity",
            format="%d"
        )
    }
)

st.markdown("---")

col5, col6 = st.columns(2)

with col5:
    st.subheader("🔝 Top 5 Best Selling Products")
    top_products = filtered_df.groupby('Product').agg({
        'Quantity': 'sum',
        'Revenue': 'sum'
    }).sort_values('Revenue', ascending=False).head(5).reset_index()
    top_products['Revenue'] = top_products['Revenue'].apply(lambda x: f"${x:,.2f}")
    st.dataframe(top_products, width='stretch', hide_index=True)

with col6:
    st.subheader("🌟 Top 5 Regions by Performance")
    top_regions = filtered_df.groupby('Region').agg({
        'Revenue': 'sum',
        'Quantity': 'sum'
    }).sort_values('Revenue', ascending=False).head(5).reset_index()
    top_regions['Revenue'] = top_regions['Revenue'].apply(lambda x: f"${x:,.2f}")
    st.dataframe(top_regions, width='stretch', hide_index=True)
