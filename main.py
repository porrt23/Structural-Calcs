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

from PyPDF2 import PdfReader
import re


#%% Test Plot
def test_plot(x, s_title):
    st.title(f"Matplotlib Plot #{x}")
    st.header(f"Line = {s_title}")
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4, 5])
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_title("Simple Line Plot")

    st.pyplot(fig)


#%% Overall Panel geometry generation
def panel_geom(pnl_data, p_fig):
    # Prep the panel outline XY points to use rectangle patch and add to figure
    xp = 0
    wp = float(pnl_data['PanelLength'])
    yp = -float(pnl_data['BottomPanelHeight'])
    hp = -yp + float(pnl_data['ParapetHeight']) + float(pnl_data['PanelHeight'])
    panel_out = Rectangle((xp,yp), wp, hp, edgecolor = 'black', fill=False, lw=5)
    p_fig.add_patch(panel_out)

    # Plot the openings on both graphs based on what is provided in the Openings section of the dataframe
    i_open = int(pnl_data['Openings'].split(';')[0])
    for i in range(0, i_open*5, 5):
        if i_open == 0:
            continue
        # for i opening, get reference corner, x/y, width, height. Then use the reference to adjust the x/y values and plot with color and dashed

        refer = int(pnl_data['Openings'].split(';')[1+i])
        x = float(pnl_data['Openings'].split(';')[2+i])
        y = float(pnl_data['Openings'].split(';')[3+i])
        w = float(pnl_data['Openings'].split(';')[4+i])
        h = float(pnl_data['Openings'].split(';')[5+i])

        match refer:
            case 1:  # Lower Right Corner
                x = wp - x
                w = -w
            case 2:  # Upper left corner
                h = -h
                y = float(pnl_data['PanelHeight']) - y
            case 3:  # Upper right corner
                x = wp - x
                w = -w
                h = -h
                y = float(pnl_data['PanelHeight']) - y
            case _:  # Lower left corner
                x = x
                y = y

        p_fig.add_patch(Rectangle((x,y), w, h, edgecolor = 'blue', fill=False, lw=2, ls='--'))

#%% Rebar areas
def r_areas(rbr):
    rbrcheck_var = 0
    if rbrcheck_var == 1:
        rebar_areas = {
            2: 0.05,
            3: 0.11,
            4: 0.2,
            5: 0.31,
            6: 0.44,
            7: 0.6,
            8: 0.79,
            9: 1.00,
            10: 1.27
        }  
        r_sze = int(rbr[2])+2
        reb_area = f'\n({round(int(rbr[1])*rebar_areas[r_sze],2)} in2)'
    else:
        reb_area = ''
    return reb_area


#%% How to plot the vertical rebar
def plot_verticals(v_data, v_fig, l_size=10, f_size=12):
    panel_geom(v_data, v_fig)

    # Plot Vertical and Horizontal Rebar
    x_values = set()
    y_values = set()
    y_values.add(0)
    # Get the XY values of the rectangles in order to find the strip locations
    for patch in v_fig.patches:
        if isinstance(patch, plt.Rectangle):
            x_values.add(round(patch.get_x(), 2))
            x_values.add(round(patch.get_x() + patch.get_width(), 2))
            y_values.add(round(patch.get_y(), 2))
            y_values.add(round(patch.get_y() + patch.get_height(), 2))
    x_values = list(x_values)
    y_values = list(y_values)
    x_values.sort()
    y_values.sort()
    if y_values[0]==0:
        h_offset = 0
    else:
        h_offset = 1
        
    # Section for Vertical rebar
    n = int(v_data['DataVBarsCount'])
    if n != 0:
        # Split the string into a list
        parts = str(v_data['DataVBarsVBars']).split(';')
        groups = [parts[i:i+n] for i in range(0, len(parts), n)]
        output_list = [[] for _ in range(n)]

        #strip, bar qty, bar size, level, spacing, end1, end2
        for i, item in enumerate(parts):
            output_list[i % n].append(float(item))

        for i in range(0, n):
            rebar = output_list[i]
            x = (x_values[int(rebar[0])+1] - x_values[int(rebar[0])])/2 + x_values[int(rebar[0])]
            r_size = int(rebar[2])+2
            r_area = r_areas(rebar)
            line = v_fig.plot([x,x],[rebar[5],rebar[6]], ls='-', label=f'({int(rebar[1])}) #{r_size} @ {round(rebar[4]*12)} in {r_area}')
            xdata, ydata = line[0].get_data()
            v_fig.annotate('',xy=(x_values[int(rebar[0])+1], mean(ydata)), xytext=(x_values[int(rebar[0])], mean(ydata)), arrowprops=dict(color=line[0].get_color(),arrowstyle='|-|'))
            v_fig.annotate(line[0].get_label().replace('@','\n@'), xy=(xdata[0], mean(ydata)), rotation=90, fontsize = f_size, ha='center', va='center', bbox=dict(facecolor='white', edgecolor=line[0].get_color()))


        
#%% How to plot horizontal rebar
def plot_horizontals(h_data, h_fig,  f_size=12):
    panel_geom(h_data, h_fig)
    
    # Plot Vertical and Horizontal Rebar
    x_values = set()
    y_values = set()
    y_values.add(0)
    # Get the XY values of the rectangles in order to find the strip locations
    for patch in h_fig.patches:
        if isinstance(patch, plt.Rectangle):
            x_values.add(round(patch.get_x(), 2))
            x_values.add(round(patch.get_x() + patch.get_width(), 2))
            y_values.add(round(patch.get_y(), 2))
            y_values.add(round(patch.get_y() + patch.get_height(), 2))
    x_values = list(x_values)
    y_values = list(y_values)
    x_values.sort()
    y_values.sort()
    if y_values[0]==0:
        h_offset = 0
    else:
        h_offset = 1
        
    # Section for Horizontal rebar
    n = int(h_data['DataHBarsCount'])
    if n != 0:
        # Split the string into a list
        parts = str(h_data['DataHBarsHBars']).split(';')
        groups = [parts[i:i+n] for i in range(0, len(parts), n)]
        output_list = [[] for _ in range(n)]

        #Qty, rebar size, Layer, Spacing, Closed, Axis(starting vertical strip), Distance1 (useless), Distance2(length), horizontal strip
        for i, item in enumerate(parts):
            output_list[i % n].append(float(item))

        for i in range(0, len(output_list)):
            rebar = output_list[i]
            x1 = x_values[int(rebar[5])]
            x2 = x1+rebar[7]
            y1 = y_values[int(rebar[8])+h_offset]
            y2 = y_values[int(rebar[8])+h_offset+1]
            y = mean([y1, y2])
            r_size = int(rebar[1])+2
            match (x2-x1):
                case _ if (x2-x1) <= 4:
                    h_label = f'#3 Ties @7 in'
                case _:
                    h_label = f'({int(rebar[0])}) #{r_size} @ {round(rebar[3]*12)} in {r_areas(rebar)}'

            line = h_fig.plot([x1,x2],[y,y], ls='-', label=h_label)
            if f'#{4} @ {18} in' not in h_label:
                xdata, ydata = line[0].get_data()
                h_fig.annotate('',xy=(mean([x1,x2]), y1), xytext=(mean([x1,x2]), y2), arrowprops=dict(color=line[0].get_color(),arrowstyle='|-|'))
                h_fig.annotate(line[0].get_label().replace('@','\n@'), xy=(mean([x1,x2]), y), fontsize = f_size, ha='center', va='center', bbox=dict(facecolor='white', edgecolor=line[0].get_color()))

#%% File uploader, that accepts only pdf files to get the ASCE Hazard report.
accepted_ftype = ['pdf']
folder_title = st.title("Upload ASCE Hazard Report:")

uploaded_file = st.file_uploader("Choose ASCE Hazard Report", type=accepted_ftype)

if uploaded_file is not None:
    file_name = uploaded_file.name
    st.write("Uploaded File Name:", file_name)

    # Open the PDF report and extract the text
    reader = PdfReader(uploaded_file)
    design_values = {
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

    # Open the PDF report and extract design values
    for i in range(0, len(reader.pages)):
        page = reader.pages[i]
        lines = page.extract_text().split('\n')
        for line in lines:
            for search_string in design_values.keys():
                if search_string in line:
                    edits = line.replace(search_string, "")
                    test = float(re.findall(r'\d+\.?\d*', edits)[0])
                    design_values[search_string] = test
    
    design_values