from math import sqrt
from handcalcs.decorator import handcalc
import streamlit as st

tab1, tab2 = st.tabs(["Inputs", "Outputs"])

with tab1:
    value = st.number_input("Enter value")
    unit = st.selectbox("Select unit", ["m", "ft", "in"])
    quantity = f"{value} {unit}"  # or convert to a unit-aware object


with tab2:
    st.write(f"Qty: {quantity}")
