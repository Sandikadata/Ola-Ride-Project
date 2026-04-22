import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import os
from sqlalchemy import create_engine
def get_connection():
    engine = create_engine("postgresql+psycopg2://postgres:1234@localhost:5432/postgres")
    return engine.connect()

BASE_DIR = "images"

icon = Image.open("images/ola.jpg")

# Page Config
st.set_page_config(
    page_title="OLA DASHBOARD",
    page_icon=icon,
    layout="wide"
)

# Title
st.title("🚖 Ola Ride Analysis Dashboard")

# Load Data
df = pd.read_csv("OLA_ride.csv")
# Vehicle Images Dictionary
vehicle_images = {
    "Auto": os.path.join(BASE_DIR, "auto.png"),
    "Bike": os.path.join(BASE_DIR, "bike.png"),
    "Mini": os.path.join(BASE_DIR, "mini.png"),
    "Prime Plus": os.path.join(BASE_DIR, "prime_plus.png"),
    "Prime SUV": os.path.join(BASE_DIR, "prime_suv.png"),
    "Prime Sedan": os.path.join(BASE_DIR, "prime_sedan.png"),
    "eBike": os.path.join(BASE_DIR, "ebike.png")
}
# Convert Date
df["Date"] = pd.to_datetime(df["Date"]).dt.date

# Sidebar Filters
st.sidebar.title("🔎 Filter OLA Ride Data")

# Date Filter
date_range = st.sidebar.slider(
    "Select Date Range",
    min_value=min(df["Date"]),
    max_value=max(df["Date"]),
    value=(min(df["Date"]), max(df["Date"]))
)

# Vehicle Filter
vehicle_type = st.sidebar.multiselect(
    "Select Vehicle Type",
    options=df["Vehicle_Type"].unique(),
    default=df["Vehicle_Type"].unique()
)

# Booking Status
booking_status = st.sidebar.multiselect(
    "Select Booking Status",
    options=df["Booking_Status"].unique(),
    default=df["Booking_Status"].unique()
)

# Filter Data
filtered_df = df[
    (df["Vehicle_Type"].isin(vehicle_type)) &
    (df["Booking_Status"].isin(booking_status)) &
    (df["Date"] >= date_range[0]) &
    (df["Date"] <= date_range[1])
]

# KPI Function
def show_kpi():
    col1, col2 = st.columns(2)

    total_booking = filtered_df["Booking_ID"].count()
    total_value = filtered_df[filtered_df["Booking_Status"] == "Success"]["Booking_Value"].sum() 

    col1.metric("Total Bookings", total_booking)
    col2.metric("Total Booking Value", f"₹{total_value:,.0f}")


# Cancellation KPI
def cancel_kpi():
    col1, col2, col3 = st.columns(3)

    # Cancel by Customer
    cancel_customer = filtered_df["Canceled_Rides_by_Customer"].notna().sum()

    # Cancel by Driver
    cancel_driver = filtered_df["Canceled_Rides_by_Driver"].notna().sum()

    # Total Cancelled
    total_cancelled = cancel_customer + cancel_driver

    # Total Bookings
    total_booking = filtered_df["Booking_ID"].count()

    # Cancel Percentage
    cancel_percent = (total_cancelled / total_booking) * 100 if total_booking > 0 else 0

    col1.metric("Cancelled by Customer", cancel_customer)
    col2.metric("Cancelled by Driver", cancel_driver)
    col3.metric("Cancelled %", f"{cancel_percent:.2f}%")
# Tabs
tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["🏠 Home", "📊 Overview", "🚗 Vehicle Type", "💰 Revenue", "❌ Cancellation", "⭐ Ratings", "🗄️ SQL Insights"]
)

# Home Tab
with tab0:

    show_kpi()

    st.subheader("Filtered Data")

    st.dataframe(filtered_df)


# Overview Tab
with tab1:
    col1, col2 = st.columns([1,4])

    col1.image("images/overall_tab.png")

    with col2:
        show_kpi()

        # Line Chart
        ride_volume = filtered_df.groupby("Date")["Booking_ID"].count().reset_index()

        fig = px.line(
            ride_volume,
            x="Date",
            y="Booking_ID",
            title="Ride Volume vs Date"
        )

        st.plotly_chart(fig)

        # Pie Chart
        status = filtered_df["Booking_Status"].value_counts().reset_index()
        status.columns=["Booking_Status","Count"]

        fig2 = px.pie(
            status,
            names="Booking_Status",
            values="Count"
        )

        st.plotly_chart(fig2)

# Vehicle Tab
with tab2:
    col1, col2 = st.columns([1,4])

    with col1:
        st.image("images/Vehicle_type_tab.png")

    with col2:

        show_kpi()

        vehicle = filtered_df.groupby("Vehicle_Type").agg({
            "Booking_Value": "sum",
            "Ride_Distance": "sum",
            "Booking_ID": "count"
        }).reset_index()

        # Rename count column for clarity
        vehicle = vehicle.rename(columns={"Booking_ID": "Total_Bookings"})

        # Success Booking Value
        success = filtered_df[filtered_df["Booking_Status"] == "Success"].groupby("Vehicle_Type")["Booking_Value"].sum().reset_index()
        success.columns = ["Vehicle_Type", "Success_Booking_Value"]

        # Merge
        vehicle = vehicle.merge(success, on="Vehicle_Type", how="left")

        # Avg Distance = Total Distance / Number of Rides
        vehicle["Avg_Distance"] = vehicle["Ride_Distance"] / vehicle["Total_Bookings"]
        # Total Ride_Distance
        vehicle = vehicle.rename(columns={"Ride_Distance": "Total_Ride_Distance"})

        # Round values
        vehicle = vehicle.round(2)

        st.subheader("Vehicle Performance")

        # Header
        col1, col2, col3, col4, col5, col6 = st.columns([1,2,2,2,2,2])

        col1.write("Vehicle")
        col2.write("Vehicle Type")
        col3.write("Total Booking Value")
        col4.write("Success Booking Value")
        col5.write("Avg Distance (km)")
        col6.write("Total Distance (km)")

        st.markdown("---")

        for index, row in vehicle.iterrows():

            col1, col2, col3, col4, col5, col6 = st.columns([1,2,2,2,2,2])

            vehicle_name = row["Vehicle_Type"]
            image_path = f"images/{vehicle_name.lower().replace(' ','_')}.png"

            col1.image(image_path, width=45)
            col2.write(vehicle_name)
            col3.write(f"₹{row['Booking_Value']:,.0f}")
            col4.write(f"₹{row['Success_Booking_Value']:,.0f}")
            col5.write(f"{row['Avg_Distance']} km")
            col6.write(f"{row['Total_Ride_Distance']} km")
# Revenue Tab
with tab3:
    col1, col2 = st.columns([1,4])

    with col1:
        st.image("images/Revenue_tab.png")

    with col2:
        show_kpi()

        payment = filtered_df.groupby("Payment_Method")["Booking_Value"].sum().reset_index()

        fig = px.bar(
            payment,
            x="Payment_Method",
            y="Booking_Value"
        )

        st.plotly_chart(fig)

        distance = filtered_df.groupby("Date")["Ride_Distance"].sum().reset_index()

        fig2 = px.line(
            distance,
            x="Date",
            y="Ride_Distance"
        )

        st.plotly_chart(fig2)


# Cancellation Tab
with tab4:
    col1, col2 = st.columns([1,4])

    col1.image("images/Cancellation_tab.png")

    with col2:
        show_kpi()
        cancel_kpi()

        # Cancel by Driver Pie
        cancel_driver = filtered_df["Canceled_Rides_by_Driver"].value_counts()

        fig1 = px.pie(
            names=cancel_driver.index,
            values=cancel_driver.values,
            title="Cancelled by Driver"
        )

        st.plotly_chart(fig1)

        # Cancel by Customer Pie
        cancel_customer = filtered_df["Canceled_Rides_by_Customer"].value_counts()

        fig2 = px.pie(
            names=cancel_customer.index,
            values=cancel_customer.values,
            title="Cancelled by Customer"
        )

        st.plotly_chart(fig2)

# Ratings Tab
with tab5:
    col1, col2 = st.columns([1,4])

    with col1:
        st.image("images/Ratings_tab.png")  # add your ratings tab image if you have one

    with col2:
        show_kpi()

        rating = filtered_df.groupby("Vehicle_Type").agg({
            "Driver_Ratings": "mean",
            "Customer_Rating": "mean"
        }).reset_index()

        rating = rating.round(2)

        st.subheader("Vehicle Ratings")

        # Header
        col1, col2, col3, col4 = st.columns([1,2,2,2])
        col1.write("Vehicle")
        col2.write("Vehicle Type")
        col3.write("Driver Rating")
        col4.write("Customer Rating")

        st.markdown("---")

        for index, row in rating.iterrows():
            col1, col2, col3, col4 = st.columns([1,2,2,2])

            vehicle = row["Vehicle_Type"]
            image_path = f"images/{vehicle.lower().replace(' ','_')}.png"

            col1.image(image_path, width=50)
            col2.write(vehicle)
            col3.write(row["Driver_Ratings"])
            col4.write(row["Customer_Rating"])

# SQL Insights Tab
with tab6:
    st.header("🗄️ SQL Query Insights")

    SQL_DIR = r"E:\CODE\OLA_RIDE _PROJECT\SQL_Result"

    # ── 1. Successful Bookings ────────────────────────────
    st.subheader("1. Retrieve all Successful Bookings")
    df1 = pd.read_csv(os.path.join(SQL_DIR, "1_Sucess_booking_status.csv"))
    st.dataframe(df1, use_container_width=True,hide_index=True)

    st.markdown("---")

    # ── 2. Average Ride Distance ──────────────────────────
    st.subheader("2. Average Ride Distance by Vehicle Type")
    df2 = pd.read_csv(os.path.join(SQL_DIR, "2_Avg_ride_distance.csv"))
    st.dataframe(df2, use_container_width=True,hide_index=True)

    st.markdown("---")

    # ── 3. Cancelled by Customer ──────────────────────────
    st.subheader("3. Total Cancelled Rides by Customers")
    df3 = pd.read_csv(os.path.join(SQL_DIR, "3_cancelled_by_customers.csv"))
    st.metric("Total Cancelled by Customer", int(df3.iloc[0, 0]))

    st.markdown("---")

    # ── 4. Top 5 Customers ────────────────────────────────
    st.subheader("4. Top 5 Customers by Number of Rides")
    df4 = pd.read_csv(os.path.join(SQL_DIR, "4_Top_five_Customer.csv"))
    st.dataframe(df4, use_container_width=True,hide_index=True)

    st.markdown("---")

    # ── 5. Cancelled by Driver ────────────────────────────
    st.subheader("5. Rides Cancelled by Driver (Personal & Car Related Issue)")
    df5 = pd.read_csv(os.path.join(SQL_DIR, "5_Cancelled_by_driver_personal_and_car_issue.csv"))
    st.dataframe(df5, use_container_width=True,hide_index=True)

    st.markdown("---")

    # ── 6. Driver Ratings ─────────────────────────────────
    st.subheader("6. Max & Min Driver Ratings for Prime Sedan")
    df6 = pd.read_csv(os.path.join(SQL_DIR, "6_driver_rating_prime_sedan.csv"))
    col1, col2 = st.columns(2)
    col1.metric("⭐ Max Driver Rating", df6.iloc[0, 0])
    col2.metric("⭐ Min Driver Rating", df6.iloc[0, 1])

    st.markdown("---")

    # ── 7. UPI Payments ───────────────────────────────────
    st.subheader("7. Rides Paid via UPI")
    df7 = pd.read_csv(os.path.join(SQL_DIR, "7_ payment_by_upi.csv"))
    st.dataframe(df7, use_container_width=True,hide_index=True)

    st.markdown("---")

    # ── 8. Customer Rating ────────────────────────────────
    st.subheader("8. Average Customer Rating by Vehicle Type")
    df8 = pd.read_csv(os.path.join(SQL_DIR, "8_avg_customer_rating.csv"))
    st.dataframe(df8, use_container_width=True)

    st.markdown("---")

    # ── 9. Total Booking Value ────────────────────────────
    st.subheader("9. Total Booking Value of Successful Rides")
    df9 = pd.read_csv(os.path.join(SQL_DIR, "9_successful_booking_value.csv"))
    st.metric("💰 Total Successful Booking Value", f"₹{df9.iloc[0, 0]:,.0f}")

    st.markdown("---")

    # ── 10. Incomplete Rides ──────────────────────────────

    st.subheader("10. Incomplete Rides Count by Reason")

    df10 = pd.read_csv(os.path.join(SQL_DIR, "10_incomplete_ride_reseaon.csv"))

    st.dataframe(df10, use_container_width=True, hide_index=True)
