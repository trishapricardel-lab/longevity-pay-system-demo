import streamlit as st
import pandas as pd
from datetime import datetime
import math

st.set_page_config(page_title="Integrated Longevity Validation System", layout="wide")

st.title("Integrated Personnel–Finance Longevity Pay Validation System")
st.markdown("### Automated SOI–Payroll Cross-Validation Engine")

st.markdown("---")

# =============================
# FILE UPLOAD SECTION
# =============================

st.header("1. Upload Required Files")

soi_file = st.file_uploader("Upload SOI File (S1) - CSV", type=["csv"])
payroll_file = st.file_uploader("Upload Payroll File (Finance) - CSV", type=["csv"])

st.markdown("---")

# =============================
# VALIDATION ENGINE
# =============================

if soi_file is not None and payroll_file is not None:

    try:
        # Read files
        soi_df = pd.read_csv(soi_file)
        payroll_df = pd.read_csv(payroll_file)

        # Required Columns
        required_soi_cols = ["Name", "Entry_Date"]
        required_payroll_cols = ["Name", "Base_Pay", "Long_Pay_Given", "Total_Salary"]

        if not all(col in soi_df.columns for col in required_soi_cols):
            st.error("SOI file must contain columns: Name, Entry_Date")
            st.stop()

        if not all(col in payroll_df.columns for col in required_payroll_cols):
            st.error("Payroll file must contain columns: Name, Base_Pay, Long_Pay_Given, Total_Salary")
            st.stop()

        # Convert Entry Date (MM/DD/YYYY)
        soi_df["Entry_Date"] = pd.to_datetime(soi_df["Entry_Date"], format="%m/%d/%Y")

        # Convert numeric columns
        payroll_df["Base_Pay"] = pd.to_numeric(payroll_df["Base_Pay"])
        payroll_df["Long_Pay_Given"] = pd.to_numeric(payroll_df["Long_Pay_Given"])
        payroll_df["Total_Salary"] = pd.to_numeric(payroll_df["Total_Salary"])

        # Compute Years of Service
        today = datetime.today()
        soi_df["Years_of_Service"] = (today - soi_df["Entry_Date"]).dt.days / 365.25

        # Compute LP Count (max 5)
        soi_df["LP_Count"] = soi_df["Years_of_Service"].apply(lambda x: min(math.floor(x / 5), 5))

        # Merge SOI and Payroll
        merged_df = pd.merge(soi_df, payroll_df, on="Name", how="inner")

        # =============================
        # LONG PAY COMPUTATION (Policy Based)
        # =============================

        def compute_correct_lp(base_pay, lp_count):
            if lp_count == 0:
                return 0
            elif lp_count == 5:
                return base_pay * 0.50  # Policy cap
            else:
                return base_pay * (1.1 ** lp_count - 1)

        merged_df["Correct_Long_Pay"] = merged_df.apply(
            lambda row: compute_correct_lp(row["Base_Pay"], row["LP_Count"]),
            axis=1
        )

        merged_df["Expected_Total_Salary"] = (
            merged_df["Base_Pay"] + merged_df["Correct_Long_Pay"]
        )

        # =============================
        # VALIDATION CHECKS
        # =============================

        merged_df["LP_Status"] = merged_df.apply(
            lambda row: "🔴 ERROR"
            if abs(row["Long_Pay_Given"] - row["Correct_Long_Pay"]) > 1
            else "🟢 OK",
            axis=1
        )

        merged_df["Salary_Status"] = merged_df.apply(
            lambda row: "🔴 ERROR"
            if abs(row["Total_Salary"] - row["Expected_Total_Salary"]) > 1
            else "🟢 OK",
            axis=1
        )

        # =============================
        # DISPLAY RESULTS
        # =============================

        st.header("2. Validation Results")

        st.dataframe(merged_df)

        total_liability = (
            merged_df["Correct_Long_Pay"] - merged_df["Long_Pay_Given"]
        ).sum()

        if abs(total_liability) > 1:
            st.error(f"Total Organizational Liability: ₱{total_liability:,.2f}")
        else:
            st.success("No discrepancies detected across uploaded records.")

    except Exception as e:
        st.error(f"Processing Error: {e}")

else:
    st.info("Please upload both SOI and Payroll files to begin validation.")

st.markdown("---")

st.markdown("### System Objective")
st.markdown("""
This system cross-validates Personnel (S1) service entry data against Finance payroll records.
It computes statutory longevity pay using a compound method with a policy cap at 50% (5th Long Pay),
and automatically flags discrepancies in both long pay and total salary.
""")
