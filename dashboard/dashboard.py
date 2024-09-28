import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english").order_id.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def create_sum_customer_spending_df(df):
    monthly_orders_df = df.resample(rule='M', on='order_approved_at').agg({
        "payment_value": "sum"
    })
    monthly_orders_df.index = monthly_orders_df.index.strftime('%B') #mengubah format order date menjadi nama bulan

    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "payment_value": "spending"
    }, inplace=True)

    monthly_final_df = monthly_orders_df.sort_values("spending").drop_duplicates("order_approved_at", keep="last")
    months = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12
    }
    monthly_final_df["month_number"] = monthly_final_df["order_approved_at"].map(months)
    monthly_final_df = monthly_final_df.sort_values("month_number")
    monthly_final_df = monthly_final_df.drop("month_number", axis=1)
    
    return monthly_final_df

def create_sum_max_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english").product_id.count().sort_values(ascending=False).reset_index()
    max_price_items_df = df.groupby("product_category_name_english").price.max().sort_values(ascending=False).reset_index()

    return sum_order_items_df, max_price_items_df

def create_mean_delivery_score_df(df):
    delivery_time_df = df.groupby("review_score").time_delivery.mean().sort_values(ascending=False).reset_index()
    return delivery_time_df


# Load cleaned data
all_df = pd.read_csv("https://media.githubusercontent.com/media/Frederickyzw/analisis_data_dicoding/refs/heads/main/dashboard/main_data.csv")

datetime_columns = ["order_approved_at", "order_delivered_customer_date"]
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Filter data
min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

with st.sidebar:
    # Menambahkan judul
    st.header('Frederick')
    st.text('Username : m319b4ky1553\nEmail : m319b4ky1553@bangkit.academy')
    # Menambahkan logo perusahaan
    st.image("https://github.com/Frederickyzw/analisis_data_dicoding/blob/main/bangkit_logo.jpg?raw=true")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu Penyajian Data',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                (all_df["order_approved_at"] <= str(end_date))]


# Menyiapkan berbagai dataframe
daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
monthly_final_df = create_sum_customer_spending_df(main_df)
sum_order_items_df, max_price_items_df = create_sum_max_items_df(main_df)
delivery_time_df = create_mean_delivery_score_df(main_df)

# plot number of daily orders (2021) [ACC]
st.header('Project Analisis Data : E-Commerce Public :sparkles:\nBelajar Analisis Data dengan Python')
st.subheader('Pesanan Harian')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total pesanan", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "USD", locale='es_CO') 
    st.metric("Total pendapatan", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#ffa900"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.set_ylabel("Jumlah pesanan", fontsize=20)
ax.set_xlabel("Waktu", fontsize=20)

plt.suptitle("Grafik Jumlah Pesanan Harian", fontsize=25)
st.pyplot(fig)


#10 Produk paling banyak terjual dan termahal [ACC]

st.subheader("10 Produk paling banyak terjual dan termahal")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#ffa900", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="product_id", y="product_category_name_english", data=sum_order_items_df.head(10), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("10 Produk paling banyak terjual", loc="center", fontsize=50)
ax[0].tick_params(axis ='y', labelsize=45)

sns.barplot(x="price", y="product_category_name_english", data=max_price_items_df.head(10), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.tick_right()
ax[1].set_title("10 Produk termahal", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=45)

plt.suptitle("10 Produk paling banyak terjual dan termahal", fontsize=70)
plt.show()

st.pyplot(fig)


# Pengaruh lama waktu pengiriman rata-rata terhadap review score [ACC]

st.subheader("Pengaruh lama mean delivery time terhadap review score")

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    delivery_time_df["time_delivery"],
    delivery_time_df["review_score"],
    marker='o',
    linewidth=2,
    color="#ffa900"
)
ax.set_ylabel("Review Score", fontsize=20)
ax.set_xlabel("Delivery Time Rata-Rata (hari)", fontsize=20)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=20)

plt.style.use('ggplot')
plt.suptitle("Grafik review score vs mean delivery time", fontsize=25)
plt.show()

st.pyplot(fig)


# 3. Total Pengeluaran Customer per Bulan (2018) [ACC]

st.subheader("Total Pengeluaran Customer per Bulan (2018)")

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_final_df["order_approved_at"], 
    monthly_final_df["spending"],
    marker='o',
    linewidth=2,
    color="#ffa900"
)
ax.set_ylabel("Harga ($)", fontsize=20)
ax.set_xlabel("Bulan", fontsize=20)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=20, rotation=45)

plt.style.use('ggplot')
plt.suptitle("Grafik pengeluaran customer vs bulan", fontsize=25)
plt.show()

st.pyplot(fig)

st.caption('Copyright (C) Frederick - m319b4ky1553@bangkit.academy 2024')