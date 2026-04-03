from pathlib import Path
code = r'''import streamlit as st
from streamlit_drawable_canvas import st_canvas
import json

st.set_page_config(page_title="Wall Bracing Canvas", layout="wide")
st.title("Wall Bracing Canvas Prototype")
st.caption("Draw wall lines and bracing lines. Geometry is stored in session state.")

if "saved_state" not in st.session_state:
    st.session_state.saved_state = {
        "version": "4.6.0",
        "objects": [
            {"type": "line", "x1": 120, "y1": 180, "x2": 920, "y2": 180, "stroke": "#111111", "strokeWidth": 4},
            {"type": "line", "x1": 120, "y1": 380, "x2": 920, "y2": 380, "stroke": "#111111", "strokeWidth": 4},
            {"type": "line", "x1": 200, "y1": 180, "x2": 200, "y2": 380, "stroke": "#0000ff", "strokeWidth": 3},
            {"type": "line", "x1": 420, "y1": 180, "x2": 420, "y2": 380, "stroke": "#0000ff", "strokeWidth": 3},
            {"type": "line", "x1": 700, "y1": 180, "x2": 700, "y2": 380, "stroke": "#0000ff", "strokeWidth": 3},
        ],
    }

with st.sidebar:
    st.header("Canvas Controls")
    drawing_mode = st.selectbox("Tool", ["line", "freedraw", "rect", "transform", "point"], index=0)
    stroke_width = st.slider("Stroke width", 1, 12, 3)
    stroke_color = st.color_picker("Stroke color", "#0000ff")
    fill_color = st.color_picker("Fill color", "#ffffff")
    bg_color = st.color_picker("Background", "#f7f7f7")
    update_streamlit = st.checkbox("Live update", value=True)
    display_toolbar = st.checkbox("Show toolbar", value=True)
    height = st.slider("Canvas height", 300, 900, 520, 20)
    width = st.slider("Canvas width", 600, 1400, 1100, 20)

col1, col2 = st.columns([1.5, 1.0], gap="large")

with col1:
    canvas_result = st_canvas(
        fill_color=fill_color,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        width=width,
        height=height,
        drawing_mode=drawing_mode,
        update_streamlit=update_streamlit,
        display_toolbar=display_toolbar,
        initial_drawing=st.session_state.saved_state,
        key="wall_canvas",
    )
    if canvas_result.json_data is not None:
        st.session_state.saved_state = canvas_result.json_data

with col2:
    st.subheader("Current Geometry")
    objects = []
    if canvas_result.json_data and "objects" in canvas_result.json_data:
        objects = canvas_result.json_data["objects"]
    st.metric("Objects", len(objects))

    wall_lines = []
    brace_lines = []
    for obj in objects:
        if obj.get("type") == "line":
            row = {
                "x1": obj.get("x1"), "y1": obj.get("y1"),
                "x2": obj.get("x2"), "y2": obj.get("y2"),
                "stroke": obj.get("stroke"),
                "strokeWidth": obj.get("strokeWidth"),
            }
            if obj.get("stroke") == "#111111":
                wall_lines.append(row)
            else:
                brace_lines.append(row)

    st.markdown("### Wall lines")
    st.dataframe(wall_lines or [{"x1": None, "y1": None, "x2": None, "y2": None, "stroke": None, "strokeWidth": None}], use_container_width=True, hide_index=True)
    st.markdown("### Bracing lines")
    st.dataframe(brace_lines or [{"x1": None, "y1": None, "x2": None, "y2": None, "stroke": None, "strokeWidth": None}], use_container_width=True, hide_index=True)

    st.markdown("### JSON")
    st.code(json.dumps(st.session_state.saved_state, indent=2), language="json")

    if st.button("Reset to example layout"):
        del st.session_state.saved_state
        st.rerun()
'''
Path('output').mkdir(exist_ok=True)
Path('output/wall_bracing_canvas_app.py').write_text(code)
Path('output/wall_bracing_canvas_app.py').exists()