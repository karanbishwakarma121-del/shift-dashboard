import pandas as pd
import streamlit as st
import plotly.express as px

# Page setup
st.set_page_config(page_title="Shift Dashboard", layout="wide")

st.title("SILA - Extra Shift Not Billed Dashboard")

# Upload file
file = st.file_uploader("Upload Shift Data File", type=["xlsx"])

if file:
    df = pd.read_excel(file)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Required columns
    required_cols = [
        "Site Code", "Site Name", "State", "Designation Name",
        "Year", "Month", "Extra Shifts Not Billed", "Per Day Wages"
    ]

    if not all(col in df.columns for col in required_cols):
        st.error("❌ Column names not matching. Please check Excel headers.")
    else:
        # ✅ Fix numeric conversion
        df["Extra Shifts Not Billed"] = pd.to_numeric(
            df["Extra Shifts Not Billed"].astype(str).str.replace(",", ""),
            errors="coerce"
        ).fillna(0)

        df["Per Day Wages"] = pd.to_numeric(
            df["Per Day Wages"].astype(str).str.replace(",", ""),
            errors="coerce"
        ).fillna(0)

        # ✅ Calculate Loss
        df["Loss Amount"] = df["Extra Shifts Not Billed"] * df["Per Day Wages"]

        # 🔍 Filters
        st.sidebar.header("Filters")

        year = st.sidebar.multiselect("Select Year", sorted(df["Year"].dropna().unique()))
        month = st.sidebar.multiselect("Select Month", sorted(df["Month"].dropna().unique()))
        state = st.sidebar.multiselect("Select State", sorted(df["State"].dropna().unique()))
        site = st.sidebar.multiselect("Select Site", sorted(df["Site Name"].dropna().unique()))

        # Apply filters
        if year:
            df = df[df["Year"].isin(year)]

        if month:
            df = df[df["Month"].isin(month)]

        if state:
            df = df[df["State"].isin(state)]

        if site:
            df = df[df["Site Name"].isin(site)]

        # Toggle
        show_all = st.sidebar.checkbox("Show All Data", value=False)

        if not show_all:
            df = df[df["Extra Shifts Not Billed"] > 0]

        # Stop if no data
        if df.empty:
            st.warning("✅ No extra shifts found for selected filters")
            st.stop()

        # 📊 KPIs
        col1, col2 = st.columns(2)

        col1.metric(
            "Total Extra Shifts",
            round(df["Extra Shifts Not Billed"].sum(), 2)
        )

        col2.metric(
            "Total Loss ₹",
            round(df["Loss Amount"].sum(), 2)
        )

        # 📊 Site-wise chart
        fig1 = px.bar(
            df,
            x="Site Name",
            y="Extra Shifts Not Billed",
            color="Designation Name",
            title="Site-wise Extra Shifts Not Billed"
        )
        st.plotly_chart(fig1, use_container_width=True)

        # 📊 State-wise chart
        state_df = df.groupby("State", as_index=False)["Extra Shifts Not Billed"].sum()

        fig2 = px.bar(
            state_df,
            x="State",
            y="Extra Shifts Not Billed",
            title="State-wise Extra Shifts"
        )
        st.plotly_chart(fig2, use_container_width=True)

        # 📈 Monthly trend
        trend_df = df.groupby(["Year", "Month"], as_index=False)["Extra Shifts Not Billed"].sum()

        fig3 = px.line(
            trend_df,
            x="Month",
            y="Extra Shifts Not Billed",
            color="Year",
            markers=True,
            title="Monthly Trend"
        )
        st.plotly_chart(fig3, use_container_width=True)

        # ✅ -------------------- SUMMARY TABLE --------------------
        st.subheader("📊 Summary - State Wise Extra Amount")

        summary_df = df.groupby(
            ["Month", "Year", "State"], as_index=False
        )["Loss Amount"].sum()

        summary_df.rename(columns={"Loss Amount": "Extra Amount"}, inplace=True)

        summary_df = summary_df.sort_values(by=["Year", "Month"])

        st.dataframe(summary_df, use_container_width=True)

        # 📋 Detailed Table
        st.subheader("Detailed Data")
        st.dataframe(df)
