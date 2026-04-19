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
SQL_DIR = "SQL_Result"  # Relative path — place this folder next to ola_app.py

# ── Safe image loader ──────────────────────────────────────────────────────────
def safe_image(path, **kwargs):
    """Display an image only if the file exists, otherwise show a placeholder."""
    if os.path.exists(path):
        st.image(path, **kwargs)
    else:
        st.caption(f"_(image not found: {path})_")

def safe_col_image(col, path, **kwargs):
    """Display an image in a column only if the file exists."""
    if os.path.exists(path):
        col.image(path, **kwargs)
    else:
        col.caption(f"_(image not found: {path})_")
# ──────────────────────────────────────────────────────────────────────────────

# Page Config
icon_path = os.path.join(BASE_DIR, "ola.jpg")
if os.path.exists(icon_path):
    icon = Image.open(icon_path)
    st.set_page_config(page_title="OLA DASHBOARD", page_icon=icon, layout="wide")
else:
    st.set_page_config(page_title="OLA DASHBOARD", page_icon="🚖", layout="wide")

# Title
st.title("🚖 Ola Ride Analysis Dashboard")

# Load Data
df = pd.read_csv("OLA_ride.csv")

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
    total_value = filtered_df["Booking_Value"].sum()
    col1.metric("Total Bookings", total_booking)
    col2.metric("Total Booking Value", f"₹{total_value:,.0f}")

# Cancellation KPI
def cancel_kpi():
    col1, col2, col3 = st.columns(3)
    cancel_customer = filtered_df["Canceled_Rides_by_Customer"].notna().sum()
    cancel_driver   = filtered_df["Canceled_Rides_by_Driver"].notna().sum()
    total_cancelled = cancel_customer + cancel_driver
    total_booking   = filtered_df["Booking_ID"].count()
    cancel_percent  = (total_cancelled / total_booking) * 100 if total_booking > 0 else 0
    col1.metric("Cancelled by Customer", cancel_customer)
    col2.metric("Cancelled by Driver",   cancel_driver)
    col3.metric("Cancelled %",           f"{cancel_percent:.2f}%")

# Tabs
tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["🏠 Home", "📊 Overview", "🚗 Vehicle Type", "💰 Revenue", "❌ Cancellation", "⭐ Ratings", "🗄️ SQL Insights"]
)

# ── Home Tab ──────────────────────────────────────────────────────────────────
with tab0:
    show_kpi()
    st.subheader("Filtered Data")
    st.dataframe(filtered_df)

# ── Overview Tab ──────────────────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns([1, 4])

    safe_col_image(col1, os.path.join(BASE_DIR, "Overall_tab.png"))

    with col2:
        show_kpi()

        ride_volume = filtered_df.groupby("Date")["Booking_ID"].count().reset_index()
        fig = px.line(ride_volume, x="Date", y="Booking_ID", title="Ride Volume vs Date")
        st.plotly_chart(fig)

        status = filtered_df["Booking_Status"].value_counts().reset_index()
        status.columns = ["Booking_Status", "Count"]
        fig2 = px.pie(status, names="Booking_Status", values="Count")
        st.plotly_chart(fig2)

# ── Vehicle Tab ───────────────────────────────────────────────────────────────
with tab2:
    col1, col2 = st.columns([1, 4])

    safe_col_image(col1, os.path.join(BASE_DIR, "Vehicle_type_tab.png"))

    with col2:
        show_kpi()

        vehicle = filtered_df.groupby("Vehicle_Type").agg({
            "Booking_Value": "sum",
            "Ride_Distance": "sum",
            "Booking_ID":    "count"
        }).reset_index().rename(columns={"Booking_ID": "Total_Bookings"})

        success = (
            filtered_df[filtered_df["Booking_Status"] == "Success"]
            .groupby("Vehicle_Type")["Booking_Value"].sum()
            .reset_index()
        )
        success.columns = ["Vehicle_Type", "Success_Booking_Value"]

        vehicle = vehicle.merge(success, on="Vehicle_Type", how="left")
        vehicle["Avg_Distance"] = vehicle["Ride_Distance"] / vehicle["Total_Bookings"]
        vehicle = vehicle.rename(columns={"Ride_Distance": "Total_Ride_Distance"}).round(2)

        st.subheader("Vehicle Performance")

        hdr = st.columns([1, 2, 2, 2, 2, 2])
        for col, label in zip(hdr, ["Vehicle", "Vehicle Type", "Total Booking Value",
                                     "Success Booking Value", "Avg Distance (km)", "Total Distance (km)"]):
            col.write(label)
        st.markdown("---")

        for _, row in vehicle.iterrows():
            c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 2, 2, 2, 2])
            vehicle_name = row["Vehicle_Type"]
            image_path   = os.path.join(BASE_DIR, f"{vehicle_name.lower().replace(' ', '_')}.png")
            safe_col_image(c1, image_path, width=45)
            c2.write(vehicle_name)
            c3.write(f"₹{row['Booking_Value']:,.0f}")
            c4.write(f"₹{row['Success_Booking_Value']:,.0f}")
            c5.write(f"{row['Avg_Distance']} km")
            c6.write(f"{row['Total_Ride_Distance']} km")

# ── Revenue Tab ───────────────────────────────────────────────────────────────
with tab3:
    col1, col2 = st.columns([1, 4])

    safe_col_image(col1, os.path.join(BASE_DIR, "Revenue_tab.png"))

    with col2:
        show_kpi()

        payment = filtered_df.groupby("Payment_Method")["Booking_Value"].sum().reset_index()
        fig = px.bar(payment, x="Payment_Method", y="Booking_Value")
        st.plotly_chart(fig)

        distance = filtered_df.groupby("Date")["Ride_Distance"].sum().reset_index()
        fig2 = px.line(distance, x="Date", y="Ride_Distance")
        st.plotly_chart(fig2)

# ── Cancellation Tab ──────────────────────────────────────────────────────────
with tab4:
    col1, col2 = st.columns([1, 4])

    safe_col_image(col1, os.path.join(BASE_DIR, "Cancellation_tab.png"))

    with col2:
        show_kpi()
        cancel_kpi()

        cancel_driver_counts = filtered_df["Canceled_Rides_by_Driver"].value_counts()
        fig1 = px.pie(names=cancel_driver_counts.index, values=cancel_driver_counts.values,
                      title="Cancelled by Driver")
        st.plotly_chart(fig1)

        cancel_customer_counts = filtered_df["Canceled_Rides_by_Customer"].value_counts()
        fig2 = px.pie(names=cancel_customer_counts.index, values=cancel_customer_counts.values,
                      title="Cancelled by Customer")
        st.plotly_chart(fig2)

# ── Ratings Tab ───────────────────────────────────────────────────────────────
with tab5:
    col1, col2 = st.columns([1, 4])

    safe_col_image(col1, os.path.join(BASE_DIR, "Ratings_tab.png"))

    with col2:
        show_kpi()

        rating = filtered_df.groupby("Vehicle_Type").agg({
            "Driver_Ratings":  "mean",
            "Customer_Rating": "mean"
        }).reset_index().round(2)

        st.subheader("Vehicle Ratings")

        hdr = st.columns([1, 2, 2, 2])
        for col, label in zip(hdr, ["Vehicle", "Vehicle Type", "Driver Rating", "Customer Rating"]):
            col.write(label)
        st.markdown("---")

        for _, row in rating.iterrows():
            c1, c2, c3, c4 = st.columns([1, 2, 2, 2])
            vehicle_name = row["Vehicle_Type"]
            image_path   = os.path.join(BASE_DIR, f"{vehicle_name.lower().replace(' ', '_')}.png")
            safe_col_image(c1, image_path, width=50)
            c2.write(vehicle_name)
            c3.write(row["Driver_Ratings"])
            c4.write(row["Customer_Rating"])

# ── SQL Insights Tab ──────────────────────────────────────────────────────────
with tab6:
    st.header("🗄️ SQL Query Insights")

    sql_files = {
        "1. Retrieve all Successful Bookings":              ("1_Sucess_booking_status.csv",                       "table"),
        "2. Average Ride Distance by Vehicle Type":         ("2_Avg_ride_distance.csv",                           "table"),
        "3. Total Cancelled Rides by Customers":            ("3_cancelled_by_customers.csv",                      "metric"),
        "4. Top 5 Customers by Number of Rides":            ("4_Top_five_Customer.csv",                           "table"),
        "5. Rides Cancelled by Driver (Personal & Car)":    ("5_Cancelled_by_driver_personal_and_car_issue.csv",  "table"),
        "6. Max & Min Driver Ratings for Prime Sedan":      ("6_driver_rating_prime_sedan.csv",                   "dual_metric"),
        "7. Rides Paid via UPI":                            ("7_ payment_by_upi.csv",                             "table"),
        "8. Average Customer Rating by Vehicle Type":       ("8_avg_customer_rating.csv",                         "table"),
        "9. Total Booking Value of Successful Rides":       ("9_successful_booking_value.csv",                    "value_metric"),
        "10. Incomplete Rides with Reason":                 ("10_incomplete_ride_reason.csv",                     "table"),
    }

    for title, (filename, display_type) in sql_files.items():
        st.subheader(title)
        filepath = os.path.join(SQL_DIR, filename)

        if not os.path.exists(filepath):
            st.warning(f"File not found: `{filepath}` — make sure SQL_Result/ is pushed to GitHub.")
            st.markdown("---")
            continue

        data = pd.read_csv(filepath)

        if display_type == "table":
            st.dataframe(data, use_container_width=True)
        elif display_type == "metric":
            st.metric("Total Cancelled by Customer", int(data.iloc[0, 0]))
        elif display_type == "dual_metric":
            c1, c2 = st.columns(2)
            c1.metric("⭐ Max Driver Rating", data.iloc[0, 0])
            c2.metric("⭐ Min Driver Rating", data.iloc[0, 1])
        elif display_type == "value_metric":
            st.metric("💰 Total Successful Booking Value", f"₹{data.iloc[0, 0]:,.0f}")

        st.markdown("---")
