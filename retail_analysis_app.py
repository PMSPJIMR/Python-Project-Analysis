import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Retail EDA Dashboard", layout="wide")
st.title("🛍️ Online Retail Data Analysis Dashboard")

# ----------------------------------------
# 📥 Load and Clean Data
# ----------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("Online Retail.xlsx", sheet_name=0)
    df = df.dropna(subset=["CustomerID"])
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
    df["Year"] = df["InvoiceDate"].dt.year
    df["Month"] = df["InvoiceDate"].dt.month
    df["Month_Year"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    return df

df = load_data()
all_countries = sorted(df["Country"].unique())

# ----------------------------------------
# 🔍 Raw Data Preview
# ----------------------------------------
st.subheader("🔍 Preview Raw Data")
if st.checkbox("Show Raw Dataset"):
    st.dataframe(df)

# ----------------------------------------
# 📊 Dashboard Metrics (Filtered by Country)
# ----------------------------------------
st.subheader("📊 Dashboard Metrics")

selected_country_dash = st.selectbox("Filter Metrics by Country", ["All"] + all_countries)
dash_df = df if selected_country_dash == "All" else df[df["Country"] == selected_country_dash]

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Revenue", f"£ {dash_df['TotalPrice'].sum():,.2f}")
col2.metric("👥 Unique Customers", dash_df["CustomerID"].nunique())
col3.metric("📦 Total Transactions", dash_df["InvoiceNo"].nunique())

# ----------------------------------------
# 📅 Sales by Country & Product (Date Range)
# ----------------------------------------
st.subheader("📅 Sales by Country and Products (Date Range)")

min_date = df["InvoiceDate"].min().date()
max_date = df["InvoiceDate"].max().date()

date_range = st.date_input("Select Date Range", [min_date, max_date])

if len(date_range) == 2:
    start_date, end_date = date_range
    if start_date > end_date:
        st.error("❌ End date must be after start date.")
    else:
        range_df = df[(df["InvoiceDate"].dt.date >= start_date) & (df["InvoiceDate"].dt.date <= end_date)]

        if not range_df.empty:
            # 🌍 Sales by Country
            st.markdown("### 🌍 Sales by Country")
            country_sales = range_df.groupby("Country")["TotalPrice"].sum().sort_values(ascending=False).reset_index()
            fig1 = px.bar(country_sales, x="Country", y="TotalPrice", text_auto=True)
            st.plotly_chart(fig1, use_container_width=True)

            top_country = country_sales.iloc[0]
            st.markdown(f"📌 **Insight**: Most revenue came from **{top_country['Country']}** (£{top_country['TotalPrice']:,.2f}).")

            # 🏷️ Top Products
            st.markdown("### 🏷️ Top 20 Products by Revenue")
            product_sales = range_df.groupby("Description")["TotalPrice"].sum().sort_values(ascending=False).head(20).reset_index()
            fig2 = px.bar(product_sales, x="TotalPrice", y="Description", orientation="h", text_auto=True)
            st.plotly_chart(fig2, use_container_width=True)

            top_product = product_sales.iloc[0]
            st.markdown(f"📌 **Insight**: Highest earning product was **{top_product['Description']}** (£{top_product['TotalPrice']:,.2f}).")
        else:
            st.warning("🚫 No data available for the selected date range.")
else:
    st.info("📆 Please select both start and end dates to generate charts.")

# ----------------------------------------
# 🧑‍💼 Top Customers (Pie Chart)
# ----------------------------------------
st.subheader("🧑‍💼 Top 10 Customers (Pie Chart)")

selected_country_cust = st.selectbox("Filter by Country (Top Customers)", ["All"] + all_countries)
cust_df = df if selected_country_cust == "All" else df[df["Country"] == selected_country_cust]

top_customers = cust_df.groupby("CustomerID")["TotalPrice"].sum().sort_values(ascending=False).head(10).reset_index()
fig3 = px.pie(top_customers, names="CustomerID", values="TotalPrice", hole=0.4, title="Top 10 Customers by Revenue")
st.plotly_chart(fig3, use_container_width=True)

top_cust = top_customers.iloc[0]
st.markdown(f"📌 **Insight**: Customer ID **{int(top_cust['CustomerID'])}** contributed the most revenue (£{top_cust['TotalPrice']:,.2f}).")

# ----------------------------------------
# 📈 Customer Retention Over Time
# ----------------------------------------
st.subheader("📈 Customer Retention Over Time (Monthly Returning Customers)")

df["InvoiceMonth"] = df["InvoiceDate"].dt.to_period("M")
monthly_customers = df.groupby("InvoiceMonth")["CustomerID"].nunique().reset_index()
monthly_customers["InvoiceMonth"] = monthly_customers["InvoiceMonth"].astype(str)

fig4 = px.line(monthly_customers, x="InvoiceMonth", y="CustomerID", markers=True, title="Monthly Unique Customers (Retention)")
st.plotly_chart(fig4, use_container_width=True)

st.markdown("📌 **Insight**: This shows how many unique customers are retained over time by month. A healthy upward trend indicates good retention.")

# ----------------------------------------
# 📌 Footer
# ----------------------------------------
st.markdown("---")
st.caption("📊 Dashboard built by Group E | Streamlit + Plotly + Pandas | Online Retail Dataset")
