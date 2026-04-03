import streamlit as st
from dataclasses import dataclass, field

st.set_page_config(
    page_title="Wall Bracing Tool",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("IRC Wall Bracing Tool")
st.caption("UI prototype for wall line layout, bracing entry, and compliance results.")

# -----------------------------
# Sidebar: Project / Code Inputs
# -----------------------------
with st.sidebar:
    st.header("Project Setup")

    project_name = st.text_input("Project name", value="Residential Project A")
    job_number = st.text_input("Job number", value="2026-001")
    address = st.text_input("Project address", value="")

    st.subheader("Code Selection")
    code_version = st.selectbox(
        "IRC version",
        ["2021 IRC", "2018 IRC", "2015 IRC", "2024 IRC / Local Amendments"],
        index=0,
    )
    design_method = st.selectbox(
        "Design method",
        ["Wind", "Seismic", "Wind + Seismic"],
        index=0,
    )

    st.subheader("Load Inputs")
    wind_speed = st.number_input("Basic wind speed (mph)", min_value=0, value=115, step=5)
    exposure = st.selectbox("Exposure category", ["B", "C", "D"], index=1)
    seismic = st.number_input("Seismic factor placeholder", min_value=0.0, value=1.0, step=0.1)

    st.subheader("Options")
    interior_gypsum = st.checkbox("Interior gypsum included", value=True)
    blocking_omitted = st.checkbox("Blocking omitted", value=False)
    veneer = st.checkbox("Stone / masonry veneer", value=False)
    continuous_sheathing = st.checkbox("Continuous sheathing", value=False)

    st.divider()
    st.button("Run check", type="primary")
    st.button("Export report")

# -----------------------------
# Main Layout
# -----------------------------
col_left, col_right = st.columns([1.4, 1.0], gap="large")

with col_left:
    st.subheader("Wall Layout")

    layout_tab1, layout_tab2, layout_tab3 = st.tabs(["Canvas", "Wall Lines", "Notes"])

    with layout_tab1:
        st.info("Placeholder for a drawing canvas, SVG import, or drag-and-drop wall line editor.")
        canvas_placeholder = st.container(border=True)
        with canvas_placeholder:
            st.markdown("### Plan View Placeholder")
            st.write("Use this area for a schematic, uploaded plan image, or future interactive canvas.")

    with layout_tab2:
        st.markdown("#### Wall Lines")
        wall_lines = [
            {"Line": "WL-1", "Length": 28, "Braced": "Yes", "Status": "Pending"},
            {"Line": "WL-2", "Length": 16, "Braced": "No", "Status": "Pending"},
            {"Line": "WL-3", "Length": 24, "Braced": "Yes", "Status": "Pending"},
        ]
        st.dataframe(wall_lines, use_container_width=True, hide_index=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.button("Add wall line")
        with c2:
            st.button("Edit selected line")
        with c3:
            st.button("Delete line")

    with layout_tab3:
        st.text_area(
            "Project notes",
            value="Enter design assumptions, special conditions, and reviewer notes here.",
            height=180,
        )

with col_right:
    st.subheader("Selected Line / Panel")

    panel_tab1, panel_tab2, panel_tab3 = st.tabs(["Properties", "Bracing Segments", "Status"])

    with panel_tab1:
        selected_line = st.selectbox("Selected wall line", ["WL-1", "WL-2", "WL-3"])
        st.number_input("Wall line length (ft)", min_value=0.0, value=24.0, step=1.0)
        st.number_input("Wall line height (ft)", min_value=0.0, value=8.0, step=0.5)
        st.selectbox(
            "Bracing method",
            ["WSP", "CS-WSP", "Portal frame", "Gypsum board", "Let-in brace"],
            index=0,
        )
        st.selectbox("Wall orientation", ["North", "South", "East", "West"], index=0)

    with panel_tab2:
        st.markdown("#### Bracing Segments")
        segments = [
            {"Segment": "B1", "Type": "WSP", "Length": 4.0, "Start": 2.0, "End": 6.0},
            {"Segment": "B2", "Type": "WSP", "Length": 4.0, "Start": 12.0, "End": 16.0},
        ]
        st.dataframe(segments, use_container_width=True, hide_index=True)
        st.button("Add bracing segment")
        st.button("Edit segment")

    with panel_tab3:
        st.metric("Required bracing", "TBD")
        st.metric("Provided bracing", "TBD")
        st.metric("Compliance", "Pending")
        st.warning("Calculation engine not connected yet.")

st.divider()

# -----------------------------
# Results / Summary
# -----------------------------
st.subheader("Project Summary")
sum1, sum2, sum3, sum4 = st.columns(4)
sum1.metric("Wall lines", "3")
sum2.metric("Segments", "2")
sum3.metric("Warnings", "0")
sum4.metric("Status", "Draft")

st.subheader("Output Preview")
preview_tab1, preview_tab2 = st.tabs(["Compliance Summary", "Report Preview"])

with preview_tab1:
    st.write("This section will show required vs provided bracing, governing loads, and pass/fail status.")
    st.dataframe(
        [
            {"Wall Line": "WL-1", "Required": "TBD", "Provided": "TBD", "Status": "Pending"},
            {"Wall Line": "WL-2", "Required": "TBD", "Provided": "TBD", "Status": "Pending"},
            {"Wall Line": "WL-3", "Required": "TBD", "Provided": "TBD", "Status": "Pending"},
        ],
        use_container_width=True,
        hide_index=True,
    )

with preview_tab2:
    st.info("Placeholder for PDF/report preview and export controls.")
    st.button("Generate PDF")
    st.button("Download CSV")