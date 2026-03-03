import pandas as pd
from datetime import datetime
import math
import streamlit as st
from datetime import date

st.set_page_config(page_title="Integrated Longevity Pay System", layout="wide")

st.title("Integrated Personnel–Finance Longevity Pay Management System")
st.markdown("### Automated Tenure-Based Compensation & Reconciliation Engine")

st.markdown("---")
# ===== File Upload Section =====
st.header("2. Data Upload Module")

soi_file = st.file_uploader("Upload SOI File (S1) - CSV", type=["csv"])
payroll_file = st.file_uploader("Upload Payroll File (Finance) - CSV", type=["csv"])

st.markdown("---")
# ===== Validation Engine =====
if soi_file is not None and payroll_file is not None:

    soi_df = pd.read_csv(soi_file)
    payroll_df = pd.read_csv(payroll_file)

    # Convert Entry Date (MM/DD/YYYY)
    soi_df["Entry_Date"] = pd.to_datetime(soi_df["Entry_Date"], format="%m/%d/%Y")

    today = datetime.today()

    # Compute Years of Service
    soi_df["Years_of_Service"] = (today - soi_df["Entry_Date"]).dt.days / 365.25

    # Compute LP Count (max 5)
    soi_df["LP_Count"] = soi_df["Years_of_Service"].apply(lambda x: min(math.floor(x / 5), 5))

    # Merge SOI and Payroll
    merged_df = pd.merge(soi_df, payroll_df, on="Name", how="inner")

    # Compute Correct Long Pay
   def compute_correct_lp(base_pay, lp_count):
    if lp_count == 0:
        return 0
    elif lp_count == 5:
        return base_pay * 0.50
    else:
        return base_pay * (1.1 ** lp_count - 1)

merged_df["Correct_Long_Pay"] = merged_df.apply(
    lambda row: compute_correct_lp(row["Base_Pay"], row["LP_Count"]),
    axis=1
)

    # Expected Total Salary
    merged_df["Expected_Total_Salary"] = merged_df["Base_Pay"] + merged_df["Correct_Long_Pay"]

    # Variance Checks
    merged_df["LP_Status"] = merged_df.apply(
        lambda row: "🔴 ERROR" if abs(row["Long_Pay_Given"] - row["Correct_Long_Pay"]) > 1 else "🟢 OK",
        axis=1
    )

    merged_df["Salary_Status"] = merged_df.apply(
        lambda row: "🔴 ERROR" if abs(row["Total_Salary"] - row["Expected_Total_Salary"]) > 1 else "🟢 OK",
        axis=1
    )

    st.header("3. Validation Results")
    st.dataframe(merged_df)

# ===== Personnel Module =====
st.header("1. Personnel Record Module")

col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Soldier Name")
    service_start = st.date_input("Service Start Date", date(2010, 1, 1))

with col2:
    today = date.today()
    years_of_service = today.year - service_start.year - (
        (today.month, today.day) < (service_start.month, service_start.day)
    )
    st.metric("Years of Service", years_of_service)

# Longevity Computation (10% per 5 years)
longevity_rate = (years_of_service // 5) * 0.10

st.markdown("---")

# ===== Payroll Module =====
st.header("2. Payroll Computation Module")

base_pay = st.number_input("Base Pay (₱)", min_value=0.0, value=40000.0, step=1000.0)

longevity_pay = base_pay * longevity_rate
total_comp = base_pay + longevity_pay

col3, col4 = st.columns(2)

with col3:
    st.metric("Authorized Longevity Rate", f"{longevity_rate*100:.0f}%")
    st.metric("Longevity Pay", f"₱{longevity_pay:,.2f}")

with col4:
    st.metric("Total Compensation", f"₱{total_comp:,.2f}")

st.markdown("---")

# ===== Simulated Payroll Database Entry =====
st.header("3. Payroll Database (Recorded Tier)")

payroll_recorded_rate = st.selectbox(
    "Recorded Longevity Rate in Payroll System",
    ["0%", "10%", "20%", "30%", "40%", "50%"]
)

payroll_rate_decimal = int(payroll_recorded_rate.replace("%", "")) / 100

st.markdown("---")

# ===== Reconciliation Engine =====
st.header("4. Reconciliation & Control Validation")

if payroll_rate_decimal != longevity_rate:
    st.error("⚠ DISCREPANCY DETECTED")
    difference = (longevity_rate - payroll_rate_decimal) * base_pay
    st.write(f"Monthly Variance: ₱{difference:,.2f}")
else:
    st.success("✔ Records are synchronized. No discrepancy detected.")
    difference = 0

st.markdown("---")

# ===== Retroactive Adjustment =====
st.header("5. Retroactive Liability Calculator")

months_affected = st.number_input("Number of Months Affected", min_value=0, value=12)

retroactive_amount = difference * months_affected

if difference != 0:
    st.warning(f"Total Retroactive Adjustment Required: ₱{retroactive_amount:,.2f}")
else:
    st.info("No retroactive adjustment required.")

st.markdown("---")

# ===== Audit Simulation =====
st.header("6. Audit Trail Log (System Simulation)")

st.write("• Tenure automatically computed from service start date.")
st.write("• Longevity rate auto-derived using statutory 10% per 5-year rule.")
st.write("• Payroll tier cross-validated against authorized rate.")
st.write("• Variance quantified automatically if mismatch detected.")

st.markdown("---")

st.markdown("### Governance Objective")
st.markdown("""
This prototype embeds regulatory longevity computation, eliminates manual recalculation,
and introduces automated reconciliation controls to prevent tenure-based compensation errors.
""")
# ===== CSV Upload & Batch Processing =====
st.markdown("---")
st.header("7. Batch Processing via CSV Upload")

uploaded_file = st.file_uploader("Upload Personnel CSV File", type=["csv"])

if uploaded_file is not None:
    import pandas as pd

    df = pd.read_csv(uploaded_file)

    st.subheader("Uploaded Data")
    st.dataframe(df)

    # Ensure required columns exist
    required_columns = ["Soldier_Name", "Service_Start_Date", "Base_Pay", "Recorded_Longevity_%"]

    if all(col in df.columns for col in required_columns):

        # Convert date column
        df["Service_Start_Date"] = pd.to_datetime(df["Service_Start_Date"])

        today = pd.to_datetime(date.today())

        # Compute Years of Service
        df["Years_of_Service"] = (
            today.year - df["Service_Start_Date"].dt.year -
            ((today.month, today.day) < (df["Service_Start_Date"].dt.month, df["Service_Start_Date"].dt.day))
        )

        # Authorized Longevity Rate
        df["Authorized_Longevity_%"] = (df["Years_of_Service"] // 5) * 10

        # Monthly Variance
        df["Variance"] = (
            (df["Authorized_Longevity_%"] - df["Recorded_Longevity_%"]) / 100
        ) * df["Base_Pay"]

        st.subheader("Processed Results")
        st.dataframe(df)

        total_liability = df["Variance"].sum()

        if total_liability != 0:
            st.error(f"Total Organizational Liability: ₱{total_liability:,.2f}")
        else:
            st.success("No discrepancies detected across uploaded records.")

    else:
        st.warning("CSV must contain columns: Soldier_Name, Service_Start_Date, Base_Pay, Recorded_Longevity_%")

