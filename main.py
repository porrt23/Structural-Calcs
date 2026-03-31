from io import BytesIO
from PyPDF2 import PdfReader
import re
import streamlit as st

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

from handcalcs.decorator import handcalc
import streamlit as st

@handcalc()
def show_params(Wind_Speed, SS, S1, Fa, Fv, SMS, SM1, SDS, SD1, TL, PGA, PGAM, FPGA, Ie, Cv, SDC, GSL, R15, R60):
    return locals()

values = {
    "Wind_Speed": 107,
    "SS": None,
    "S1": None,
    "Fa": None,
    "Fv": None,
    "SMS": None,
    "SM1": None,
    "SDS": None,
    "SD1": None,
    "TL": None,
    "PGA": None,
    "PGAM": None,
    "FPGA": None,
    "Ie": None,
    "Cv": None,
    "SDC": None,
    "GSL": 5,
    "R15": None,
    "R60": None,
}



st.title("Upload ASCE Hazard Report")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

latex_code, _ = show_params(**values)
st.latex(latex_code)

# if uploaded_file is not None:
#     values = hazard_reader(uploaded_file)
#     st.write(values)
#     st.latex(latex_from_dict(values))
