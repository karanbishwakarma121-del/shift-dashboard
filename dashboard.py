import pandas as pd
import streamlit as st
import plotly.express as px

# -------------------- PAGE SETUP --------------------
st.set_page_config(page_title="SILA Dashboard", layout="wide")

st.title("🏢 SILA - Extra Shift Not Billed Dashboard")

# -------------------- FILE UPLOAD --------------------
file = st.file_uploader("Upload Excel File", type=["xlsx"])

if file:

    df = pd.read_excel(file)

    # -------------------- CLEAN COLUMN NAMES --------------------
    df.columns = df.columns.str.strip()

    # -------------------- REQUIRED COLUMNS --------------------
    required_cols = [
        "Site Name", "State", "Month", "Year",
        "Designation Name", "Extra Shifts Not Billed", "CTC Rate"
    ]

    # Check columns
    missing = [col for col in required_cols if col not in df.columns]

    if missing:
        st.error(f"❌ Missing columns: {missing}")
        st.stop()

    # -------------------- DATA CLEANING --------------------
    df["Extra Shifts Not Billed"] = pd.to_numeric(
        df["Extra Shifts Not Billed"], errors="coerce"
    ).fillna(0)

    df["CTC Rate"] = pd.to_numeric(
        df["CTC Rate"], errors="coerce"
    ).fillna(0)

    df["Month"] = pd.to_numeric(df["Month"], errors="coerce")
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

    # Remove invalid rows
    df = df.dropna(subset=["Extra Shifts Not Billed", "CTC Rate"])

    # -------------------- CALCULATIONS --------------------
    df["Total Loss"] = df["Extra Shifts Not Billed"] * df["CTC Rate"]

    # -------------------- FILTERS --------------------
    st.sidebar.header("🔍 Filters")

    year = st.sidebar.multiselect("Year", sorted(df["Year"].dropna().unique()))
    month = st.sidebar.multiselect("Month", sorted(df["Month"].dropna().unique()))
    state = st.sidebar.multiselect("State", sorted(df["State"].dropna().unique()))
    site = st.sidebar.multiselect("Site", sorted(df["Site Name"].dropna().unique()))
    designation = st.sidebar.multiselect("Designation", sorted(df["Designation Name"].dropna().unique()))

    # Apply filters
    filtered_df = df.copy()

    if year:
        filtered_df = filtered_df[filtered_df["Year"].isin(year)]
    if month:
        filtered_df = filtered_df[filtered_df["Month"].isin(month)]
    if state:
        filtered_df = filtered_df[filtered_df["State"].isin(state)]
    if site:
        filtered_df = filtered_df[filtered_df["Site Name"].isin(site)]
    if designation:
        filtered_df = filtered_df[filtered_df["Designation Name"].isin(designation)]

    # Remove zero values
    filtered_df = filtered_df[filtered_df["Extra Shifts Not Billed"] > 0]

    # -------------------- EMPTY CHECK --------------------
    if filtered_df.empty:
        st.warning("✅ No extra shifts found for selected filters")
        st.stop()

    # -------------------- KPI --------------------
    col1, col2 = st.columns(2)

    col1.metric("Total Extra Shifts", round(filtered_df["Extra Shifts Not Billed"].sum(), 2))
    col2.metric("Total Loss ₹", round(filtered_df["Total Loss"].sum(), 2))

    # -------------------- SITE-WISE CHART --------------------
    site_data = filtered_df.groupby("Site Name")["Extra Shifts Not Billed"].sum().reset_index()

    fig1 = px.bar(
        site_data,
        x="Site Name",
        y="Extra Shifts Not Billed",
        title="📊 Site-wise Extra Shifts Not Billed"
    )

    st.plotly_chart(fig1, use_container_width=True)

    # -------------------- STATE-WISE --------------------
    state_data = filtered_df.groupby("State")["Extra Shifts Not Billed"].sum().reset_index()

    fig2 = px.bar(
        state_data,
        x="State",
        y="Extra Shifts Not Billed",
        title="📍 State-wise Extra Shifts"
    )

    st.plotly_chart(fig2, use_container_width=True)

    # -------------------- DESIGNATION-WISE --------------------
    desg_data = filtered_df.groupby("Designation Name")["Extra Shifts Not Billed"].sum().reset_index()

    fig3 = px.bar(
        desg_data,
        x="Designation Name",
        y="Extra Shifts Not Billed",
        title="👔 Designation-wise Extra Shifts"
    )

    st.plotly_chart(fig3, use_container_width=True)

    # -------------------- MONTHLY TREND --------------------
    trend_data = filtered_df.groupby(["Year", "Month"])["Extra Shifts Not Billed"].sum().reset_index()

    fig4 = px.line(
        trend_data,
        x="Month",
        y="Extra Shifts Not Billed",
        color="Year",
        markers=True,
        title="📈 Monthly Trend"
    )

    st.plotly_chart(fig4, use_container_width=True)

    # -------------------- DOWNLOAD BUTTON --------------------
    st.subheader("📥 Download Filtered Report")

    csv = filtered_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="SILA_Shift_Report.csv",
        mime="text/csv"
    )

    # -------------------- TABLE --------------------
    st.subheader("📋 Detailed Data")

    st.dataframe(filtered_df)
