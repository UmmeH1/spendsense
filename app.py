import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page setup ---
st.set_page_config(page_title="SpendSense", layout="wide")
st.title("SpendSense — Personal Finance Anomaly Tracker")
st.caption("Tracking spending patterns and flagging unusual transactions")

# --- Load our cleaned data ---
# spending_with_anomalies.csv has the spending rows PLUS the anomaly flag
spending = pd.read_csv("spending_with_anomalies.csv", parse_dates=["date"])

# --- Chart 1: Spending over time ---
st.subheader("Spending Over Time")
# Group all transactions by date and add up the total spent that day
daily = spending.groupby("date")["amount"].sum().reset_index()
fig1 = px.line(daily, x="date", y="amount", title="Daily Spending Total")
st.plotly_chart(fig1, use_container_width=True)

# --- Chart 2: Spending by category ---
st.subheader("Spending by Category")
by_category = spending.groupby("category")["amount"].sum().sort_values(ascending=False).reset_index()
fig2 = px.bar(by_category, x="category", y="amount", title="Total Spent per Category")
st.plotly_chart(fig2, use_container_width=True)

# --- Table: Flagged (unusual) transactions ---
st.subheader("Flagged Transactions")
st.caption("Transactions that stood out as unusual compared to your normal spending in that category")

flagged = spending[spending["anomaly"] == "flagged"].sort_values("amount", ascending=False)

if len(flagged) == 0:
    st.write("No unusual transactions found.")
else:
    # Show the amount in red-ish styling so flagged rows are easy to spot
    st.dataframe(
        flagged[["date", "merchant", "category", "amount"]],
        use_container_width=True,
        hide_index=True,
    )

# --- Quick summary stats at the top-level ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Transactions", len(spending))
col2.metric("Flagged as Unusual", len(flagged))
col3.metric("Total Spending", f"${spending['amount'].sum():,.2f}")
