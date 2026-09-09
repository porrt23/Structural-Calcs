# geometry_engine.py
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Union
import json
from enum import Enum
import math
from shapely.geometry import Polygon as ShapelyPolygon, MultiPolygon, box
from shapely.ops import unary_union, polygonize
from shapely.affinity import translate, rotate
import geopandas as gpd
from matplotlib.path import Path

# === Data Models with Shapely ===
@dataclass
class Point:
    x: float
    y: float
    
    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

@dataclass
class BuildingFootprint:
    """Represents a building footprint with shapely polygon support"""
    name: str
    polygon: ShapelyPolygon
    color: str = "#4A90E2"
    
    def area(self) -> float:
        return self.polygon.area
    
    def perimeter(self) -> float:
        return self.polygon.length
    
    def centroid(self) -> Point:
        centroid = self.polygon.centroid
        return Point(centroid.x, centroid.y)
    
    def bounding_box(self) -> Tuple[float, float, float, float]:
        bounds = self.polygon.bounds
        return bounds  # (minx, miny, maxx, maxy)
    
    def to_plotly_points(self) -> Tuple[List[float], List[float]]:
        """Convert to plotly format (closed polygon)"""
        coords = list(self.polygon.exterior.coords)
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        return xs, ys

class GeometryOperations:
    """Handles boolean operations on building footprints"""
    
    @staticmethod
    def add_rectangle(x: float, y: float, width: float, height: float) -> ShapelyPolygon:
        """Create a rectangle polygon"""
        return box(x, y, x + width, y + height)
    
    @staticmethod
    def add_circle(cx: float, cy: float, radius: float, segments: int = 36) -> ShapelyPolygon:
        """Create a circle polygon"""
        angles = np.linspace(0, 2*np.pi, segments)
        points = [(cx + radius * np.cos(a), cy + radius * np.sin(a)) for a in angles]
        return ShapelyPolygon(points)
    
    @staticmethod
    def union(geometries: List[ShapelyPolygon]) -> ShapelyPolygon:
        """Union multiple polygons"""
        result = unary_union(geometries)
        if result.geom_type == 'MultiPolygon':
            # Merge multipolygon into single polygon if possible
            return unary_union(result.geoms)
        return result
    
    @staticmethod
    def subtract(base: ShapelyPolygon, to_subtract: ShapelyPolygon) -> ShapelyPolygon:
        """Subtract one polygon from another"""
        result = base.difference(to_subtract)
        if result.is_empty:
            return None
        if result.geom_type == 'MultiPolygon':
            # Return the largest component or union
            areas = [p.area for p in result.geoms]
            return result.geoms[np.argmax(areas)]
        return result
    
    @staticmethod
    def intersect(poly1: ShapelyPolygon, poly2: ShapelyPolygon) -> ShapelyPolygon:
        """Intersection of two polygons"""
        result = poly1.intersection(poly2)
        if result.is_empty:
            return None
        return result

# === Building Manager ===
class BuildingManager:
    def __init__(self):
        self.footprints: List[BuildingFootprint] = []
        self.operations_history: List[Dict] = []
        self.current_footprint: Optional[BuildingFootprint] = None
        self.grid_lines: List[Dict] = []
        self.roof_sections: List[Dict] = []
        self.brace_lines: Dict[str, List] = {'NS': [], 'EW': []}
        
    def add_shape(self, polygon: ShapelyPolygon, name: str = "") -> BuildingFootprint:
        """Add a shape to the building"""
        if not name:
            name = f"Footprint {len(self.footprints) + 1}"
        
        footprint = BuildingFootprint(name, polygon)
        self.footprints.append(footprint)
        self.current_footprint = footprint
        
        # Add to history
        self.operations_history.append({
            'type': 'add',
            'name': name,
            'polygon': polygon
        })
        
        return footprint
    
    def subtract_shape(self, base_index: int, subtract_polygon: ShapelyPolygon) -> Optional[BuildingFootprint]:
        """Subtract a shape from an existing footprint"""
        if base_index >= len(self.footprints):
            return None
        
        base = self.footprints[base_index]
        result = GeometryOperations.subtract(base.polygon, subtract_polygon)
        
        if result is None or result.is_empty:
            return None
        
        # Update the footprint
        new_footprint = BuildingFootprint(
            f"{base.name} (modified)",
            result,
            base.color
        )
        self.footprints[base_index] = new_footprint
        self.current_footprint = new_footprint
        
        # Add to history
        self.operations_history.append({
            'type': 'subtract',
            'base': base.name,
            'result': result
        })
        
        return new_footprint
    
    def union_all(self) -> BuildingFootprint:
        """Union all footprints into one"""
        if not self.footprints:
            return None
        
        polygons = [f.polygon for f in self.footprints]
        unioned = GeometryOperations.union(polygons)
        
        footprint = BuildingFootprint("United Building", unioned)
        self.footprints = [footprint]
        self.current_footprint = footprint
        
        return footprint
    
    def get_combined_polygon(self) -> Optional[ShapelyPolygon]:
        """Get the combined polygon of all footprints"""
        if not self.footprints:
            return None
        
        if len(self.footprints) == 1:
            return self.footprints[0].polygon
        
        polygons = [f.polygon for f in self.footprints]
        return GeometryOperations.union(polygons)
    
    def get_bounding_box(self) -> Tuple[float, float, float, float]:
        """Get bounding box of all footprints"""
        combined = self.get_combined_polygon()
        if combined is None:
            return (-10, -10, 10, 10)
        return combined.bounds
    
    def get_max_height(self) -> float:
        """Get max roof height"""
        heights = [r.get('ridge_height', 0) for r in self.roof_sections]
        return max(heights) if heights else 10.0
    
    def to_dict(self) -> Dict:
        """Export building data to dictionary"""
        return {
            'footprints': [
                {
                    'name': f.name,
                    'coordinates': list(f.polygon.exterior.coords),
                    'area': f.area(),
                    'perimeter': f.perimeter()
                }
                for f in self.footprints
            ],
            'grid_lines': self.grid_lines,
            'roof_sections': self.roof_sections,
            'brace_lines': self.brace_lines
        }
    
    def from_dict(self, data: Dict):
        """Import building data from dictionary"""
        self.footprints = []
        for fp_data in data.get('footprints', []):
            polygon = ShapelyPolygon(fp_data['coordinates'])
            footprint = BuildingFootprint(fp_data['name'], polygon)
            self.footprints.append(footprint)
        
        self.grid_lines = data.get('grid_lines', [])
        self.roof_sections = data.get('roof_sections', [])
        self.brace_lines = data.get('brace_lines', {'NS': [], 'EW': []})

# === Visualization ===
def plot_building_plan(building: BuildingManager, show_grid: bool = True, show_brace: bool = True):
    """Plot building plan with all features"""
    fig = go.Figure()
    
    # Color palette
    colors = ['#4A90E2', '#50C878', '#FF6B6B', '#FFD93D', '#6C5CE7']
    
    # Plot each footprint
    for i, footprint in enumerate(building.footprints):
        xs, ys = footprint.to_plotly_points()
        
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode='lines+markers',
            name=footprint.name,
            fill='toself',
            fillcolor=colors[i % len(colors)] + '40',  # Add transparency
            line=dict(width=3, color=colors[i % len(colors)]),
            marker=dict(size=6, color=colors[i % len(colors)]),
            hovertemplate=f'<b>{footprint.name}</b><br>' +
                         f'Area: {footprint.area():.1f} ft²<br>' +
                         f'Perimeter: {footprint.perimeter():.1f} ft<br>' +
                         '<extra></extra>'
        ))
        
        # Add area label at centroid
        centroid = footprint.centroid()
        fig.add_annotation(
            x=centroid.x,
            y=centroid.y,
            text=f'{footprint.area():.0f} ft²',
            showarrow=False,
            font=dict(size=10, color='black'),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='gray',
            borderwidth=1
        )
    
    # Plot grid
    if show_grid:
        bbox = building.get_bounding_box()
        for grid in building.grid_lines:
            if grid.get('orientation') == 'vertical':
                fig.add_vline(
                    x=grid['position'],
                    line_dash='dash',
                    opacity=0.3,
                    line_color='gray',
                    annotation_text=grid.get('label', '')
                )
            else:
                fig.add_hline(
                    y=grid['position'],
                    line_dash='dash',
                    opacity=0.3,
                    line_color='gray',
                    annotation_text=grid.get('label', '')
                )
    
    # Plot brace lines
    if show_brace:
        for direction, lines in building.brace_lines.items():
            for bl in lines:
                x1, y1 = bl['start']
                x2, y2 = bl['end']
                
                fig.add_trace(go.Scatter(
                    x=[x1, x2],
                    y=[y1, y2],
                    mode='lines+markers',
                    name=f"{bl.get('name', 'BL')} ({direction})",
                    line=dict(width=4, color='red' if direction == 'NS' else 'orange'),
                    marker=dict(size=10, symbol='diamond'),
                    hovertemplate=f'<b>{bl.get("name", "Brace Line")}</b><br>' +
                                 f'Direction: {direction}<br>' +
                                 f'Length: {bl.get("length", 0):.1f} ft<br>' +
                                 '<extra></extra>'
                ))
                
                # Add label
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                fig.add_annotation(
                    x=mid_x,
                    y=mid_y,
                    text=bl.get('name', ''),
                    showarrow=True,
                    arrowhead=1,
                    ax=20,
                    ay=-20,
                    font=dict(size=11, color='darkred')
                )
    
    # Set layout
    bbox = building.get_bounding_box()
    padding = max(5, (bbox[2] - bbox[0]) * 0.1)
    
    fig.update_layout(
        title='Building Plan View',
        xaxis_title='X (ft)',
        yaxis_title='Y (ft)',
        width=700,
        height=700,
        showlegend=True,
        hovermode='closest',
        xaxis=dict(
            range=[bbox[0] - padding, bbox[2] + padding],
            scaleanchor='y',
            scaleratio=1,
            gridcolor='lightgray',
            gridwidth=1
        ),
        yaxis=dict(
            range=[bbox[1] - padding, bbox[3] + padding],
            gridcolor='lightgray',
            gridwidth=1
        ),
        plot_bgcolor='white',
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return fig

def plot_3d_building(building: BuildingManager):
    """3D visualization of the building"""
    fig = go.Figure()
    
    # This is a placeholder for 3D visualization
    # You'd need to extrude the footprints with roof geometry
    
    combined = building.get_combined_polygon()
    if combined is None:
        return fig
    
    # Simple 3D extrusion (placeholder)
    xs, ys = combined.exterior.xy
    
    # Create a simple 3D box
    height = building.get_max_height()
    
    # Bottom
    fig.add_trace(go.Mesh3d(
        x=list(xs),
        y=list(ys),
        z=[0]*len(xs),
        color='lightblue',
        opacity=0.7,
        name='Building'
    ))
    
    # Top (simplified)
    fig.add_trace(go.Mesh3d(
        x=list(xs),
        y=list(ys),
        z=[height]*len(xs),
        color='lightcoral',
        opacity=0.5,
        name='Roof'
    ))
    
    fig.update_layout(
        title='3D Building View',
        scene=dict(
            xaxis_title='X (ft)',
            yaxis_title='Y (ft)',
            zaxis_title='Height (ft)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.0)
            )
        ),
        width=700,
        height=600
    )
    
    return fig

# === Streamlit UI ===
def main():
    st.set_page_config(
        page_title="Building Geometry Designer",
        page_icon="🏗️",
        layout="wide"
    )
    
    st.title("🏗️ Advanced Building Geometry Designer")
    st.markdown("### With Boolean Operations (Union, Subtract)")
    
    # Initialize building manager
    if 'building' not in st.session_state:
        st.session_state.building = BuildingManager()
    if 'temp_shapes' not in st.session_state:
        st.session_state.temp_shapes = []
    
    building = st.session_state.building
    
    # Sidebar
    with st.sidebar:
        st.header("🛠️ Drawing Tools")
        
        tool = st.radio(
            "Select Tool",
            ['Rectangle', 'Circle', 'Subtract Shape', 'Union All', 'Grid', 'Brace Lines'],
            key='tool'
        )
        
        if tool == 'Rectangle':
            st.subheader("➕ Add Rectangle")
            col1, col2 = st.columns(2)
            with col1:
                x = st.number_input('X (ft)', value=0.0, step=1.0)
                y = st.number_input('Y (ft)', value=0.0, step=1.0)
            with col2:
                width = st.number_input('Width (ft)', value=20.0, min_value=1.0, step=1.0)
                height = st.number_input('Height (ft)', value=40.0, min_value=1.0, step=1.0)
            
            name = st.text_input('Name (optional)', value="")
            
            if st.button('Add Rectangle', use_container_width=True, type='primary'):
                polygon = GeometryOperations.add_rectangle(x, y, width, height)
                building.add_shape(polygon, name if name else f"Rect {len(building.footprints)+1}")
                st.success(f"Added rectangle: {width}' x {height}'")
                st.rerun()
        
        elif tool == 'Circle':
            st.subheader("➕ Add Circle")
            cx = st.number_input('Center X (ft)', value=10.0)
            cy = st.number_input('Center Y (ft)', value=20.0)
            radius = st.number_input('Radius (ft)', value=10.0, min_value=1.0)
            segments = st.slider('Segments', 6, 48, 24)
            
            if st.button('Add Circle', use_container_width=True, type='primary'):
                polygon = GeometryOperations.add_circle(cx, cy, radius, segments)
                building.add_shape(polygon, f"Circle {len(building.footprints)+1}")
                st.success(f"Added circle: r={radius}'")
                st.rerun()
        
        elif tool == 'Subtract Shape':
            st.subheader("✂️ Subtract Shape")
            
            if not building.footprints:
                st.warning("No footprints to subtract from!")
            else:
                # Select base shape
                base_options = [f"{i}: {f.name}" for i, f in enumerate(building.footprints)]
                base_idx = st.selectbox('Select base footprint', range(len(base_options)), format_func=lambda x: base_options[x])
                
                st.markdown("---")
                st.markdown("**Subtract this shape:**")
                
                sub_x = st.number_input('Subtract - X (ft)', value=5.0)
                sub_y = st.number_input('Subtract - Y (ft)', value=5.0)
                sub_w = st.number_input('Subtract - Width (ft)', value=10.0, min_value=1.0)
                sub_h = st.number_input('Subtract - Height (ft)', value=15.0, min_value=1.0)
                
                if st.button('Subtract', use_container_width=True, type='primary'):
                    subtract_poly = GeometryOperations.add_rectangle(sub_x, sub_y, sub_w, sub_h)
                    result = building.subtract_shape(base_idx, subtract_poly)
                    
                    if result:
                        st.success(f"Subtracted shape! New area: {result.area():.1f} ft²")
                        st.rerun()
                    else:
                        st.error("Subtraction resulted in empty shape!")
        
        elif tool == 'Union All':
            st.subheader("🔗 Union All Shapes")
            
            if len(building.footprints) < 2:
                st.warning("Need at least 2 footprints to union!")
            else:
                st.info(f"Will union {len(building.footprints)} footprints")
                
                if st.button('Union All', use_container_width=True, type='primary'):
                    result = building.union_all()
                    if result:
                        st.success(f"United! Total area: {result.area():.1f} ft²")
                        st.rerun()
        
        elif tool == 'Grid':
            st.subheader("📏 Add Grid Lines")
            
            spacing = st.number_input('Grid Spacing (ft)', value=10.0, min_value=1.0)
            
            col1, col2 = st.columns(2)
            with col1:
                add_vertical = st.checkbox('Vertical lines', value=True)
            with col2:
                add_horizontal = st.checkbox('Horizontal lines', value=True)
            
            if st.button('Add Grid', use_container_width=True):
                bbox = building.get_bounding_box()
                xmin, ymin, xmax, ymax = bbox
                
                if add_vertical:
                    x = math.ceil(xmin / spacing) * spacing
                    while x <= xmax:
                        building.grid_lines.append({
                            'orientation': 'vertical',
                            'position': x,
                            'label': f'Grid {x:.0f}'
                        })
                        x += spacing
                
                if add_horizontal:
                    y = math.ceil(ymin / spacing) * spacing
                    while y <= ymax:
                        building.grid_lines.append({
                            'orientation': 'horizontal',
                            'position': y,
                            'label': f'Grid {y:.0f}'
                        })
                        y += spacing
                
                st.success(f"Added grid lines")
                st.rerun()
        
        elif tool == 'Brace Lines':
            st.subheader("📐 Brace Lines")
            
            direction = st.selectbox('Direction', ['NS', 'EW'])
            
            bbox = building.get_bounding_box()
            xmin, ymin, xmax, ymax = bbox
            
            if direction == 'NS':
                position = st.slider('Position X (ft)', float(xmin), float(xmax), 0.0)
                y1 = st.number_input('Start Y (ft)', value=float(ymin))
                y2 = st.number_input('End Y (ft)', value=float(ymax))
            else:
                position = st.slider('Position Y (ft)', float(ymin), float(ymax), 0.0)
                x1 = st.number_input('Start X (ft)', value=float(xmin))
                x2 = st.number_input('End X (ft)', value=float(xmax))
            
            name = st.text_input('Brace Line Name', value=f"BL-{len(building.brace_lines[direction])+1}")
            
            if st.button('Add Brace Line', use_container_width=True, type='primary'):
                if direction == 'NS':
                    bl = {
                        'name': name,
                        'start': (position, y1),
                        'end': (position, y2),
                        'length': abs(y2 - y1)
                    }
                else:
                    bl = {
                        'name': name,
                        'start': (x1, position),
                        'end': (x2, position),
                        'length': abs(x2 - x1)
                    }
                
                building.brace_lines[direction].append(bl)
                st.success(f"Added brace line: {name}")
                st.rerun()
            
            # Show existing brace lines
            st.divider()
            st.subheader("Existing Brace Lines")
            for direction, lines in building.brace_lines.items():
                for bl in lines:
                    st.text(f"• {bl['name']}: {direction} (Length: {bl['length']:.1f}ft)")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Plan View
        fig_plan = plot_building_plan(building)
        st.plotly_chart(fig_plan, use_container_width=True)
        
        # 3D View (optional)
        if st.checkbox("Show 3D View"):
            fig_3d = plot_3d_building(building)
            st.plotly_chart(fig_3d, use_container_width=True)
    
    with col2:
        st.subheader("📊 Building Information")
        
        # Metrics
        combined = building.get_combined_polygon()
        if combined:
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Total Area", f"{combined.area:.1f} ft²")
            with col_b:
                st.metric("Perimeter", f"{combined.length:.1f} ft")
        
        st.metric("Number of Footprints", len(building.footprints))
        
        # Operations History
        with st.expander("📜 Operations History", expanded=False):
            if building.operations_history:
                for op in building.operations_history[-10:]:
                    st.text(f"• {op['type']}: {op.get('name', '')}")
            else:
                st.text("No operations yet")
        
        # Shape List
        with st.expander("📋 Shape List", expanded=True):
            for i, fp in enumerate(building.footprints):
                st.text(f"{i+1}. {fp.name}")
                st.text(f"   Area: {fp.area():.1f} ft²")
                st.text(f"   Vertices: {len(fp.polygon.exterior.coords)}")
        
        # Export/Import
        st.divider()
        col_export, col_import = st.columns(2)
        
        with col_export:
            if st.button("💾 Export JSON", use_container_width=True):
                data = building.to_dict()
                json_str = json.dumps(data, indent=2)
                st.download_button(
                    "Download",
                    json_str,
                    file_name="building_geometry.json",
                    mime="application/json"
                )
        
        with col_import:
            uploaded_file = st.file_uploader("Import JSON", type=['json'])
            if uploaded_file:
                data = json.load(uploaded_file)
                building.from_dict(data)
                st.success("Imported successfully!")
                st.rerun()
        
        # Clear all
        if st.button("🗑️ Clear All", use_container_width=True, type='secondary'):
            st.session_state.building = BuildingManager()
            st.rerun()

if __name__ == '__main__':
    # Install required packages if not present
    try:
        import shapely
    except ImportError:
        st.error("Please install shapely: pip install shapely")
        st.stop()
    
    main()