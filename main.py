#%%Import libraries
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import os
import io
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from statistics import mean
from handcalcs.decorator import handcalc

from PyPDF2 import PdfReader
import re

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

    return 5

#%% File uploader, that accepts only pdf files to get the ASCE Hazard report.
accepted_ftype = ['pdf']
folder_title = st.title("Upload ASCE Hazard Report:")

uploaded_file = st.file_uploader("Choose ASCE Hazard Report", type=accepted_ftype)

if uploaded_file is not None:
    file_name = uploaded_file.name
    st.write("Uploaded File Name:", file_name)
    results = hazard_reader(uploaded_file)
    results