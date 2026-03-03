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
        soi_df = pd.read_csv(soi_file)
        payroll_df = pd.read_csv(payroll_file)

        # Required Columns
        required_soi_cols = ["Serial Number", "Date of Entry"]
        required_payroll_cols = ["Serial Number", "Basic Salary", "Longevity Pay"]

        if not all(col in soi_df.columns for col in required_soi_cols):
            st.error("SOI file must contain: Serial Number, Date of Entry")
            st.stop()

        if not all(col in payroll_df.columns for col in required_payroll_cols):
            st.error("Payroll file must contain: Serial Number, Basic Salary, Longevity Pay")
            st.stop()

        # Convert Date of Entry (MM/DD/YYYY)
        soi_df["Date of Entry"] = pd.to_datetime(
            soi_df["Date of Entry"], format="%m/%d/%Y"
        )

        # Convert numeric columns
        payroll_df["Basic Salary"] = pd.to_numeric(payroll_df["Basic Salary"])
        payroll_df["Longevity Pay"] = pd.to_numeric(payroll_df["Longevity Pay"])

        # Compute Years of Service
        today = datetime.today()
        soi_df["Years_of_Service"] = (
            (today - soi_df["Date of Entry"]).dt.days / 365.25
        )

        # Compute LP Count (max 5)
        soi_df["LP_Count"] = soi_df["Years_of_Service"].apply(
            lambda x: min(math.floor(x / 5), 5)
        )

        # Merge by Serial Number
        merged_df = pd.merge(
            soi_df,
            payroll_df,
            on="Serial Number",
            how="inner"
        )

        # =============================
        # LONG PAY COMPUTATION (Policy Cap at 50%)
        # =============================

        def compute_correct_lp(base_salary, lp_count):
            if lp_count == 0:
                return 0
            elif lp_count == 5:
                return base_salary * 0.50  # Policy cap
            else:
                return base_salary * (1.1 ** lp_count - 1)

        merged_df["Correct_Long_Pay"] = merged_df.apply(
            lambda row: compute_correct_lp(
                row["Basic Salary"], row["LP_Count"]
            ),
            axis=1
        )
        # Compute Difference (Over/Under Payment)
        merged_df["LP_Difference"] = (
            merged_df["Longevity Pay"] - merged_df["Correct_Long_Pay"]
)

        # =============================
        # VALIDATION CHECK
        # =============================

        def lp_status_message(diff):
    if abs(diff) <= 1:
        return "🟢 OK"
    elif diff > 0:
        return f"🔴 OVERPAID ₱{diff:,.2f}"
    else:
        return f"🔴 UNDERPAID ₱{abs(diff):,.2f}"

merged_df["LP_Status"] = merged_df["LP_Difference"].apply(lp_status_message)

        st.header("2. Validation Results")

        st.dataframe(
            merged_df[
                [
                    "Serial Number",
                    "Years_of_Service",
                    "LP_Count",
                    "Basic Salary",
                    "Longevity Pay",
                    "Correct_Long_Pay",
                    "LP_Status",
                ]
            ]
        )

        total_liability = (
            merged_df["Correct_Long_Pay"] - merged_df["Longevity Pay"]
        ).sum()

        if abs(total_liability) > 1:
            st.error(f"Total Organizational Longevity Variance: ₱{total_liability:,.2f}")
        else:
            st.success("No longevity discrepancies detected.")

    except Exception as e:
        st.error(f"Processing Error: {e}")

else:
    st.info("Upload both SOI and Payroll files to begin validation.")

st.markdown("---")

st.markdown("### Governance Objective")
st.markdown("""
This system cross-validates official personnel service records against payroll longevity disbursement.
It computes authorized longevity pay using statutory 10% increments per 5-year service block,
with a policy cap at 50%, and automatically flags discrepancies for control review.
""")


