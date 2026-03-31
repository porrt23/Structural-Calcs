from io import BytesIO
from PyPDF2 import PdfReader
import re
from handcalcs.decorator import handcalc
import streamlit as st
import pandas as pd
import forallpeople as fp

fp.environment('structural')

def get_pdf_text(uploaded_file):
    reader = PdfReader(BytesIO(uploaded_file.read()))
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def find(text, pattern, cast=float, default=None):
    m = re.search(pattern, text, flags=re.I | re.S)
    if not m:
        return default
    v = m.group(1).strip()
    if cast is None:
        return v
    try:
        return cast(v)
    except:
        return default

def hazard_reader(uploaded_file):
    text = get_pdf_text(uploaded_file)

    patterns = {
        "Wind Speed": (r"Wind Speed\s+(\d+(?:\.\d+)?)", float),
        "SS": (r"\bSS\s+(\d+(?:\.\d+)?)", float),
        "S1": (r"\bS1\s+(\d+(?:\.\d+)?)", float),
        "Fa": (r"\bFa\s+(\d+(?:\.\d+)?)", float),
        "Fv": (r"\bFv\s+(\d+(?:\.\d+)?)", float),
        "SMS": (r"\bSMS\s+(\d+(?:\.\d+)?)", float),
        "SM1": (r"\bSM1\s+(\d+(?:\.\d+)?)", float),
        "SDS": (r"\bSDS\s+(\d+(?:\.\d+)?)", float),
        "SD1": (r"\bSD1\s+(\d+(?:\.\d+)?)", float),
        "TL": (r"\bTL\s+(\d+(?:\.\d+)?)", float),
        "PGA": (r"\bPGA\s+(\d+(?:\.\d+)?)", float),
        "PGAM": (r"\bPGA M\s+(\d+(?:\.\d+)?)", float),
        "FPGA": (r"\bFPGA\s+(\d+(?:\.\d+)?)", float),
        "Ie": (r"\bIe\s+(\d+(?:\.\d+)?)", float),
        "Cv": (r"\bCv\s+(\d+(?:\.\d+)?)", float),
        "Seismic Design Category": (r"Seismic Design Category\s+([A-F])", None),
        "Ground Snow Load": (r"Ground Snow Load.*?(\d+(?:\.\d+)?)\s+lb", float),
        "15-minute Precipitation Intensity": (r"15-minute Precipitation Intensity\s+(\d+(?:\.\d+)?)", float),
        "60-minute Precipitation Intensity": (r"60-minute Precipitation Intensity\s+(\d+(?:\.\d+)?)", float),
    }

    values = {}
    for key, (pattern, cast) in patterns.items():
        values[key] = find(text, pattern, cast=cast)

    return values

def latex_from_dict(values):
    lines = []
    for k, v in values.items():
        v = "NULL" if v is None else v
        if isinstance(v, str):
            v = v.replace("_", r"\_")
        lines.append(rf"\text{{{k}}} &= {v} \\")
    return r"\begin{aligned}" + "\n" + "\n".join(lines) + "\n" + r"\end{aligned}"

@handcalc(override="params")
def show_params(Wind_Speed, SS, S1, Fa, Fv, SMS, SM1, SDS, SD1, TL, PGA, PGAM, FPGA, Ie, Cv, SDC, GSL, R15, R60):
    Wind_Speed = Wind_Speed * fp.kip
    SS = SS
    S1 = S1
    Fa = Fa
    Fv = Fv
    SMS = SMS
    SM1 = SM1
    SDS = SDS
    SD1 = SD1
    TL = TL
    PGA = PGA
    PGAM = PGAM
    FPGA = FPGA
    Ie = Ie
    Cv = Cv
    SDC = SDC
    GSL = GSL
    R15 = R15
    R60 = R60
    return locals()

values = {
    "Wind_Speed": 107,
    "SS": 5,
    "S1": 1,
    "Fa": 1,
    "Fv": 1,
    "SMS": 1,
    "SM1": 1,
    "SDS": 1,
    "SD1": 1,
    "TL": 1,
    "PGA": 1,
    "PGAM": 1,
    "FPGA": 1,
    "Ie": 1,
    "Cv": 1,
    "SDC": 1,
    "GSL": 5,
    "R15": 1,
    "R60": 1,
}
st.set_page_config(layout="wide")
test = fp.environment()
st.write(test)
st.title("Upload ASCE Hazard Report")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

latex_code, vals = show_params(**values)
st.write(latex_code)

# if uploaded_file is not None:
#     values = hazard_reader(uploaded_file)
#     st.write(values)
#     st.latex(latex_from_dict(values))
