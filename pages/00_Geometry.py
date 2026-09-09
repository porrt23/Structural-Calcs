# app.py
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional
import json

# === Data Models ===
@dataclass
class Point:
    x: float
    y: float
    
@dataclass
class Rectangle:
    x: float
    y: float
    width: float
    height: float
    
    def to_polygon(self):
        return [
            Point(self.x, self.y),
            Point(self.x + self.width, self.y),
            Point(self.x + self.width, self.y + self.height),
            Point(self.x, self.y + self.height)
        ]

@dataclass
class Line:
    start: Point
    end: Point

@dataclass
class GridLine:
    orientation: str  # 'horizontal' or 'vertical'
    position: float

@dataclass
class RoofSection:
    polygon: List[Point]  # footprint in plan
    roof_type: str  # 'gable', 'hip', 'shed', 'flat'
    ridge_height: float
    slope: Optional[float] = None
    orientation: Optional[float] = None  # degrees

# === Geometry Engine ===
class BuildingGeometry:
    def __init__(self):
        self.footprint = []
        self.grid_lines = []
        self.roof_sections = []
    
    def add_rectangle(self, rect: Rectangle):
        self.footprint.extend(rect.to_polygon())
    
    def add_line(self, line: Line):
        self.footprint.append(line.start)
        self.footprint.append(line.end)
    
    def add_grid(self, spacing: float, bounds: Tuple[float, float, float, float]):
        xmin, ymin, xmax, ymax = bounds
        x = xmin
        while x <= xmax:
            self.grid_lines.append(GridLine('vertical', x))
            x += spacing
        y = ymin
        while y <= ymax:
            self.grid_lines.append(GridLine('horizontal', y))
            y += spacing
    
    def generate_roof_3d(self, section: RoofSection):
        """Generate 3D coordinates for a roof section"""
        # Simplified - you'd implement proper roof generation here
        points = section.polygon
        z_base = 0
        
        if section.roof_type == 'gable':
            # Generate gable roof vertices
            # This is simplified - you'd need proper triangulation
            return self._generate_gable(points, section.ridge_height)
        elif section.roof_type == 'flat':
            return self._generate_flat(points, section.ridge_height)
        # ... other types
    
    def _generate_gable(self, points, ridge_height):
        # Implement gable roof generation
        # Returns mesh vertices and faces
        pass
    
    def _generate_flat(self, points, height):
        # Implement flat roof
        pass

# === Visualization ===
def plot_plan_view(geometry: BuildingGeometry):
    fig = go.Figure()
    
    # Plot footprint
    if geometry.footprint:
        xs = [p.x for p in geometry.footprint]
        ys = [p.y for p in geometry.footprint]
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode='lines+markers',
            name='Footprint',
            line=dict(width=2)
        ))
    
    # Plot grid
    for grid in geometry.grid_lines:
        if grid.orientation == 'vertical':
            fig.add_vline(x=grid.position, line_dash='dash', opacity=0.3)
        else:
            fig.add_hline(y=grid.position, line_dash='dash', opacity=0.3)
    
    fig.update_layout(
        title='Building Plan View',
        xaxis_title='X (m)',
        yaxis_title='Y (m)',
        width=600,
        height=600,
        showlegend=True
    )
    return fig

def plot_elevation(geometry: BuildingGeometry):
    # Implement elevation view with roof profiles
    fig = go.Figure()
    # ... plotting logic
    return fig

# === Streamlit UI ===
st.set_page_config(page_title="Building Designer", layout="wide")
st.title("🏗️ Building Geometry Designer")

# Initialize session state
if 'geometry' not in st.session_state:
    st.session_state.geometry = BuildingGeometry()
if 'mode' not in st.session_state:
    st.session_state.mode = 'select'

# Sidebar - Tools
with st.sidebar:
    st.header("🛠️ Tools")
    
    tool = st.radio(
        "Select Tool",
        ['Rectangle', 'Line', 'Grid', 'Roof', 'Select'],
        key='tool'
    )
    
    if tool == 'Rectangle':
        st.subheader("Draw Rectangle")
        col1, col2 = st.columns(2)
        with col1:
            x = st.number_input('X', value=0.0)
            y = st.number_input('Y', value=0.0)
        with col2:
            width = st.number_input('Width', value=5.0, min_value=0.1)
            height = st.number_input('Height', value=5.0, min_value=0.1)
        
        if st.button('Add Rectangle'):
            rect = Rectangle(x, y, width, height)
            st.session_state.geometry.add_rectangle(rect)
            st.success(f"Added rectangle at ({x}, {y})")
            st.rerun()
    
    elif tool == 'Grid':
        st.subheader("Add Grid")
        spacing = st.number_input('Grid Spacing (m)', value=1.0, min_value=0.1)
        if st.button('Add Grid'):
            # Get bounds from existing geometry or use defaults
            bounds = (-10, -10, 10, 10)
            st.session_state.geometry.add_grid(spacing, bounds)
            st.success(f"Added grid with {spacing}m spacing")
            st.rerun()
    
    elif tool == 'Roof':
        st.subheader("Add Roof Section")
        roof_type = st.selectbox('Roof Type', ['Gable', 'Hip', 'Shed', 'Flat'])
        ridge_height = st.number_input('Ridge/Height (m)', value=3.0)
        slope = st.number_input('Slope (°)', value=30.0, min_value=0.1, max_value=89.9)
        
        # For now, use a default polygon (you'd let user select from plan)
        st.info("Click on plan to define roof extents (coming soon)")
        
        if st.button('Add Roof'):
            # Placeholder: create roof from current footprint
            if st.session_state.geometry.footprint:
                section = RoofSection(
                    polygon=st.session_state.geometry.footprint.copy(),
                    roof_type=roof_type.lower(),
                    ridge_height=ridge_height,
                    slope=slope
                )
                st.session_state.geometry.roof_sections.append(section)
                st.success(f"Added {roof_type} roof")
                st.rerun()
            else:
                st.warning("Define building footprint first!")

# Main area - two columns
col1, col2 = st.columns([2, 1])

with col1:
    # Plan View
    st.subheader("📐 Plan View")
    fig_plan = plot_plan_view(st.session_state.geometry)
    st.plotly_chart(fig_plan, use_container_width=True)
    
    # Elevation View (if roofs exist)
    if st.session_state.geometry.roof_sections:
        st.subheader("📏 Elevation View")
        # Simplified elevation view
        fig_elev = plot_elevation(st.session_state.geometry)
        st.plotly_chart(fig_elev, use_container_width=True)

with col2:
    st.subheader("📋 Building Data")
    
    # Show geometry summary
    with st.expander("Footprint", expanded=True):
        st.write(f"Points: {len(st.session_state.geometry.footprint)}")
        if st.session_state.geometry.footprint:
            st.json({
                'points': [
                    {'x': p.x, 'y': p.y} 
                    for p in st.session_state.geometry.footprint[-5:]  # Show last 5
                ]
            })
    
    with st.expander("Grid Lines"):
        st.write(f"Grid lines: {len(st.session_state.geometry.grid_lines)}")
    
    with st.expander("Roof Sections"):
        for i, roof in enumerate(st.session_state.geometry.roof_sections):
            st.write(f"Section {i+1}: {roof.roof_type}")
            st.write(f"  Ridge height: {roof.ridge_height}m")
    
    # Actions
    if st.button('🗑️ Clear All'):
        st.session_state.geometry = BuildingGeometry()
        st.rerun()
    
    if st.button('💾 Export JSON'):
        # Convert to JSON
        data = {
            'footprint': [{'x': p.x, 'y': p.y} for p in st.session_state.geometry.footprint],
            'grid_lines': [{'orientation': g.orientation, 'position': g.position} 
                            for g in st.session_state.geometry.grid_lines],
            'roof_sections': [
                {
                    'type': r.roof_type,
                    'ridge_height': r.ridge_height,
                    'slope': r.slope
                } for r in st.session_state.geometry.roof_sections
            ]
        }
        st.download_button(
            'Download JSON',
            data=json.dumps(data, indent=2),
            file_name='building.json',
            mime='application/json'
        )