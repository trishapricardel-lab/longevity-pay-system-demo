import streamlit as st
import pandas as pd
import math
from datetime import datetime

st.set_page_config(page_title="Integrated Longevity Audit System", layout="wide")

st.title("Integrated Longevity Pay Audit System")
st.markdown("### Validation & Forensic Compensation Analytics Engine")

# ======================================================
# SIDEBAR MODE SELECTOR
# ======================================================

st.sidebar.header("System Mode")
mode = st.sidebar.radio(
    "Select Audit Mode",
    [
        "Single-Month Validation",
        "Multi-Month Forensic Audit"
    ]
)

st.markdown("---")

# ======================================================
# SINGLE MONTH VALIDATION MODULE
# ======================================================

def single_month_validation():

    st.header("Single-Month Longevity Validation")

    soi_file = st.file_uploader("Upload SOI File (CSV)", type=["csv"], key="sm_soi")
    payroll_file = st.file_uploader("Upload Payroll File (CSV)", type=["csv"], key="sm_pay")

    if soi_file and payroll_file:

        soi_df = pd.read_csv(soi_file)
        payroll_df = pd.read_csv(payroll_file)

        soi_df["Date of Entry"] = pd.to_datetime(
            soi_df["Date of Entry"], format="%m/%d/%Y"
        )

        payroll_df["Basic Salary"] = pd.to_numeric(payroll_df["Basic Salary"])
        payroll_df["Longevity Pay"] = pd.to_numeric(payroll_df["Longevity Pay"])

        today = datetime.today()

        soi_df["Years_of_Service"] = (
            (today - soi_df["Date of Entry"]).dt.days / 365.25
        )

        soi_df["LP_Count"] = soi_df["Years_of_Service"].apply(
            lambda x: min(math.floor(x / 5), 5)
        )

        merged_df = pd.merge(
            soi_df,
            payroll_df,
            on="Serial Number",
            how="inner"
        )

        def compute_correct_lp(base_salary, lp_count):
            if lp_count <= 0:
                return 0
            elif lp_count == 5:
                return base_salary * 0.50
            else:
                return base_salary * (1.1 ** lp_count - 1)

        merged_df["Correct_Long_Pay"] = merged_df.apply(
            lambda row: compute_correct_lp(
                row["Basic Salary"],
                row["LP_Count"]
            ),
            axis=1
        )

        merged_df["LP_Difference"] = (
            merged_df["Longevity Pay"] - merged_df["Correct_Long_Pay"]
        )

        merged_df["Status"] = merged_df["LP_Difference"].apply(
            lambda x: "OK" if abs(x) <= 1 else "DISCREPANCY"
        )

        st.dataframe(merged_df)

        total_variance = merged_df["LP_Difference"].sum()
        st.metric("Total Monthly Variance", f"₱{total_variance:,.2f}")

# ======================================================
# MULTI MONTH FORENSIC MODULE
# ======================================================

def multi_month_forensic():

    st.header("Multi-Month Forensic Longevity Audit")

    soi_file = st.file_uploader("Upload SOI File (CSV)", type=["csv"], key="mm_soi")

    payroll_files = st.file_uploader(
        "Upload Monthly Payroll Files (CSV)",
        type=["csv"],
        accept_multiple_files=True,
        key="mm_pay"
    )

    if soi_file and payroll_files:

        soi_df = pd.read_csv(soi_file)

        soi_df["Date of Entry"] = pd.to_datetime(
            soi_df["Date of Entry"],
            format="%m/%d/%Y"
        )

        payroll_list = []

        for file in payroll_files:
            df = pd.read_csv(file)
            payroll_list.append(df)

        payroll_df = pd.concat(payroll_list, ignore_index=True)

        payroll_df["Basic Salary"] = pd.to_numeric(payroll_df["Basic Salary"])
        payroll_df["Longevity Pay"] = pd.to_numeric(payroll_df["Longevity Pay"])

        payroll_df["Payroll_Date"] = pd.to_datetime(
            payroll_df["Payroll Month"] + "-01"
        )

        merged_df = pd.merge(
            payroll_df,
            soi_df,
            on="Serial Number",
            how="inner"
        )

        merged_df["Years_of_Service"] = (
            (merged_df["Payroll_Date"] - merged_df["Date of Entry"]).dt.days / 365.25
        )

        merged_df["LP_Count"] = merged_df["Years_of_Service"].apply(
            lambda x: min(math.floor(x / 5), 5)
        )

        def compute_correct_lp(base_salary, lp_count):
            if lp_count <= 0:
                return 0
            elif lp_count == 5:
                return base_salary * 0.50
            else:
                return base_salary * (1.1 ** lp_count - 1)

        merged_df["Correct_Long_Pay"] = merged_df.apply(
            lambda row: compute_correct_lp(
                row["Basic Salary"],
                row["LP_Count"]
            ),
            axis=1
        )

        merged_df["LP_Difference"] = (
            merged_df["Longevity Pay"] - merged_df["Correct_Long_Pay"]
        )

        merged_df["Error_Flag"] = merged_df["LP_Difference"].abs() > 1

        summary_df = merged_df.groupby("Serial Number").agg(
            Months_Incorrect=("Error_Flag", "sum"),
            Total_Variance=("LP_Difference", "sum"),
            Total_Overpaid=("LP_Difference", lambda x: x[x > 1].sum()),
            Total_Underpaid=("LP_Difference", lambda x: abs(x[x < -1].sum()))
        ).reset_index()

        total_overpayment = summary_df["Total_Overpaid"].sum()
        total_underpayment = summary_df["Total_Underpaid"].sum()
        net_exposure = total_underpayment - total_overpayment

        st.metric("Total Overpayment", f"₱{total_overpayment:,.2f}")
        st.metric("Total Underpayment", f"₱{total_underpayment:,.2f}")
        st.metric("Net Organizational Liability", f"₱{net_exposure:,.2f}")

        st.markdown("---")
        st.subheader("Individual Forensic Summary")
        st.dataframe(summary_df)

        st.markdown("---")
        st.subheader("Detailed Monthly Audit")
        st.dataframe(merged_df)

        csv_report = merged_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Multi-Month Audit Report",
            data=csv_report,
            file_name="forensic_longevity_audit.csv",
            mime="text/csv",
        )

# ======================================================
# ROUTING
# ======================================================

if mode == "Single-Month Validation":
    single_month_validation()

if mode == "Multi-Month Forensic Audit":
    multi_month_forensic()
