from io import BytesIO
from PyPDF2 import PdfReader
import re
import streamlit as st

def get_text_from_pdf(uploaded_file):
    pdf_bytes = uploaded_file.read()
    reader = PdfReader(BytesIO(pdf_bytes))
    return "\n".join((page.extract_text() or "") for page in reader.pages)

def extract_value(text, pattern, default=None, cast=float):
    m = re.search(pattern, text, flags=re.I | re.S)
    if not m:
        return default
    value = m.group(1)
    if cast is None:
        return value
    try:
        return cast(value)
    except Exception:
        return default

def hazard_reader(uploaded_file):
    text = get_text_from_pdf(uploaded_file)

    values = {
        "Wind Speed": extract_value(text, r"Wind Speed\s+(\d+(?:\.\d+)?)"),
        "SS": extract_value(text, r"\bSS\s+(\d+(?:\.\d+)?)"),
        "S1": extract_value(text, r"\bS1\s+(\d+(?:\.\d+)?)"),
        "Fa": extract_value(text, r"\bFa\s+(\d+(?:\.\d+)?)"),
        "Fv": extract_value(text, r"\bFv\s+(\d+(?:\.\d+)?)"),
        "SMS": extract_value(text, r"\bSMS\s+(\d+(?:\.\d+)?)"),
        "SM1": extract_value(text, r"\bSM1\s+(\d+(?:\.\d+)?)"),
        "SDS": extract_value(text, r"\bSDS\s+(\d+(?:\.\d+)?)"),
        "SD1": extract_value(text, r"\bSD1\s+(\d+(?:\.\d+)?)"),
        "TL": extract_value(text, r"\bTL\s+(\d+(?:\.\d+)?)"),
        "PGA": extract_value(text, r"\bPGA\s+(\d+(?:\.\d+)?)"),
        "PGAM": extract_value(text, r"\bPGA M\s+(\d+(?:\.\d+)?)"),
        "FPGA": extract_value(text, r"\bFPGA\s+(\d+(?:\.\d+)?)"),
        "Ie": extract_value(text, r"\bIe\s+(\d+(?:\.\d+)?)"),
        "Cv": extract_value(text, r"\bCv\s+(\d+(?:\.\d+)?)"),
        "Seismic Design Category": extract_value(text, r"Seismic Design Category\s+([A-F])", cast=None),
        "Ground Snow Load": extract_value(text, r"Ground Snow Load.*?(\d+(?:\.\d+)?)\s+lb", cast=float),
        "15-minute Precipitation Intensity": extract_value(text, r"15-minute Precipitation Intensity\s+(\d+(?:\.\d+)?)"),
        "60-minute Precipitation Intensity": extract_value(text, r"60-minute Precipitation Intensity\s+(\d+(?:\.\d+)?)"),
    }

    return values

def build_latex(values):
    return rf"""
\begin{{aligned}}
\text{{Wind Speed}} &= {values["Wind Speed"]} \ \text{{mph}} \\
S_S &= {values["SS"]} \\
S_1 &= {values["S1"]} \\
F_a &= {values["Fa"]} \\
F_v &= {values["Fv"]} \\
S_{{MS}} &= {values["SMS"]} \\
S_{{M1}} &= {values["SM1"]} \\
S_{{DS}} &= {values["SDS"]} \\
S_{{D1}} &= {values["SD1"]} \\
T_L &= {values["TL"]} \\
PGA &= {values["PGA"]} \\
PGA_m &= {values["PGAM"]} \\
F_PGA &= {values["FPGA"]} \\
I_e &= {values["Ie"]} \\
C_v &= {values["Cv"]} \\
\text{{Seismic Design Category}} &= {values["Seismic Design Category"]} \\
\text{{Ground Snow Load}} &= {values["Ground Snow Load"]} \ \text{{psf}} \\
\text{{15-min Rain}} &= {values["15-minute Precipitation Intensity"]} \ \text{{in.}} \\
\text{{60-min Rain}} &= {values["60-minute Precipitation Intensity"]} \ \text{{in.}}
\end{{aligned}}
"""

st.title("Upload ASCE Hazard Report")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    pdf_values = hazard_reader(uploaded_file)
    st.write(pdf_values)
    st.latex(build_latex(pdf_values))
