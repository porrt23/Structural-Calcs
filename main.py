from PyPDF2 import PdfReader
import re
import streamlit as st
from handcalcs.decorator import handcalc

@handcalc(jupyter_display=True)
def hazard_reader(pdf_file):
    # Open the PDF report and extract the text
    reader = PdfReader(pdf_file)
    pdf_values = {
        'Wind Speed': 0,  # mph
        'SS': 0,
        'S1': 0,
        'Fa': 0,
        'Fv': 0,
        'SMS': 0,
        'SM1': 0,
        'SDS': 0,
        'SD1': 0,
        'TL': 0,
        'PGA': 0,
        'PGAM': 0,
        'FPGA': 0,
        'Ie': 0,
        'Cv': 0,
        'Seismic Design Category': 0,  # Probably need to actually calculate some of these values from the equations
        'Ground Snow Load': 0,  # Ground snow (pg) in psf
        '15-minute Precipitation Intensity': 0,  # 15 minute rain value
        '60-minute Precipitation Intensity': 0  # 1 hour rain value
    }
    
    # # Open the PDF report and extract design values
    # for i in range(0, len(reader.pages)):
    #     page = reader.pages[i]
    #     lines = page.extract_text().split('\n')
    #     for line in lines:
    #         for search_string in pdf_values.keys():
    #             if search_string in line:
    #                 edits = line.replace(search_string, "")
    #                 found_val = float(re.findall(r'\d+\.?\d*', edits)[0])
    #                 pdf_values[search_string] = found_val

    return pdf_values

#%% File uploader, that accepts only pdf files to get the ASCE Hazard report.
accepted_ftype = ['pdf']
folder_title = st.title("Upload ASCE Hazard Report:")

uploaded_file = st.file_uploader("Choose a PDF file", type=accepted_ftype)
if uploaded_file is not None:
    pdf_values, latex_code = hazard_reader(uploaded_file)
    st.write(pdf_values)
    # Display the LaTeX code using Streamlit
    st.latex(latex_code)