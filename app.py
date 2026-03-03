import streamlit as st
from datetime import date

st.set_page_config(page_title="Integrated Longevity Pay System", layout="wide")

st.title("Integrated Personnel–Finance Longevity Pay Management System")
st.markdown("### Automated Tenure-Based Compensation & Reconciliation Engine")

st.markdown("---")

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
