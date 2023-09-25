import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Function to create pivot table / data frame to group customers based on some features
def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule='M', on='order_purchase_timestamp').agg({"order_id": "count", "payment_value": "sum"})
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={"order_id": "order_count", "payment_value": "revenue"}, inplace=True)
    return monthly_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name").agg({'order_id':'count','payment_value':'sum'}).sort_values(by='order_id', ascending=False).reset_index()
    return sum_order_items_df

def create_sum_seller_df(df):
    sum_seller_df = df.groupby('seller_id').agg({'order_id':'count', 'payment_value':'sum'}).sort_values(by='order_id', ascending=False).reset_index()
    return sum_seller_df

def create_cussel_state_df(df):
    customer_state_df = df.groupby(by="customer_state").customer_unique_id.nunique().reset_index()
    seller_state_df = df.groupby(by="seller_state").seller_id.nunique().reset_index()
    return customer_state_df, seller_state_df

def create_state_df(df):
    state_df = df.groupby('customer_state').agg({'order_id':'count', 'payment_value':'sum'}).sort_values(by='order_id', ascending=False).reset_index()
    return state_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_unique_id", as_index=False).agg({
    "order_purchase_timestamp": "max", # get the last order
    "order_id": "nunique", # count total order
    "payment_value": "sum" # count total revenue generated
    })
    rfm_df.columns = ["customer_unique_id", "max_order_timestamp", "frequency", "monetary"]
    
    # menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df

# Read the data
all_df = pd.read_csv("data\all.csv")

# Sort the data frame based on order_purchase_timestamp
datetime_columns = ["order_purchase_timestamp"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Create filter component
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:    
    # Get the start_date and end_date from date_input
    start_date, end_date = st.date_input(
        label='Time Range', min_value=min_date, max_value=max_date, value=[min_date, max_date]
    )

filtered_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & (all_df["order_purchase_timestamp"] <= str(end_date))]

# Function Implementation
monthly_orders_df = create_monthly_orders_df(filtered_df)
sum_order_items_df = create_sum_order_items_df(filtered_df)
sum_seller_df = create_sum_seller_df(filtered_df)
customer_state_df, seller_state_df = create_cussel_state_df(filtered_df)
state_df = create_state_df(filtered_df)
rfm_df = create_rfm_df(filtered_df)

# Dashboard completion with some visualizations
st.header('E-Commerce Company Sales Dashboard :sparkles:')

# Show total order and revenue
st.subheader('Monthly Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(monthly_orders_df.revenue.sum(), "BRL ", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(monthly_orders_df["order_purchase_timestamp"], monthly_orders_df["order_count"], marker='o', linewidth=2,)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

# Show the most and the least sold product
st.subheader("Best & Worst Performing Product")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 15))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
colors2 = ["#ec644b", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="payment_value", y="product_category_name", data=sum_order_items_df.sort_values(by="payment_value", ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="payment_value", y="product_category_name", data=sum_order_items_df.sort_values(by="payment_value", ascending=True).head(5), palette=colors2, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)

# Show best performing seller
st.subheader("Best Performing Seller")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 15))
 
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="order_id", y="seller_id", data=sum_seller_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Sold The Most", loc="left", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="payment_value", y="seller_id", data=sum_seller_df.head(5).sort_values(by='payment_value', ascending=False), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("left")
ax[1].yaxis.tick_right()
ax[1].set_title("The Most Revenue (BRL)", loc="right", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

# Show customer demographics
st.subheader("Customer Demographics")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))
colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="customer_unique_id", y="customer_state", data=customer_state_df.sort_values(by="customer_unique_id", ascending=False).head(5), palette=colors_, ax=ax[0])
ax[0].set_title("Number of Customer by States", loc="center", fontsize=30)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].tick_params(axis='y', labelsize=20)
ax[0].tick_params(axis='x', labelsize=20)

sns.barplot(x="seller_id", y="seller_state", data=seller_state_df.sort_values(by="seller_id", ascending=False).head(5), palette=colors_, ax=ax[1])
ax[1].set_title("Number of Seller by States", loc="center", fontsize=30)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].tick_params(axis='y', labelsize=20)
ax[1].tick_params(axis='x', labelsize=20)

st.pyplot(fig)

# Show revenue demoghrapics
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))
 
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="order_id", y="customer_state", data=state_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Total Product Sold by Customer State", loc="center", fontsize=30)
ax[0].tick_params(axis='y', labelsize=20)
ax[0].tick_params(axis='x', labelsize=20)
 
sns.barplot(x="payment_value", y="customer_state", data=state_df.head(5).sort_values(by='payment_value', ascending=False), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("Total Revenue by Customer State", loc="center", fontsize=30)
ax[1].tick_params(axis='y', labelsize=20)
ax[1].tick_params(axis='x', labelsize=20)

st.pyplot(fig)


# Show RFM Analysis Graph
st.subheader("Best Customer Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "BRL ", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(15,20), constrained_layout=True)
 
colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]
 
sns.barplot(x="recency", y="customer_unique_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", fontsize=30)
ax[0].tick_params(axis='y', labelsize=20)
ax[0].tick_params(axis='x', labelsize=25)
 
sns.barplot(x="frequency", y="customer_unique_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency",fontsize=30)
ax[1].tick_params(axis='y', labelsize=20)
ax[1].tick_params(axis='x', labelsize=25)
 
sns.barplot(x="monetary", y="customer_unique_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary",fontsize=30)
ax[2].tick_params(axis='y', labelsize=20)
ax[2].tick_params(axis='x', labelsize=25)

fig.tight_layout(pad=5)

st.pyplot(fig)
