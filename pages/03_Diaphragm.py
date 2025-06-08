from handcalcs.decorator import handcalc
import streamlit as st
import pandas as pd
import math
import numpy as np

class Rigid_Diaphragm():
    def __init__(self, L, H, CMx, CMy, walls, dia_angle=0, w_ecc = 0.15, eq_ecc = 0.05):
        self.L = L # Length of diaphragm EW dimension (ft)
        self.H = H # width of diaphragm NS dimension (ft)
        self.w_ecc = w_ecc # Wind load eccentricity percentage
        self.eq_ecc = eq_ecc # Seismic load eccentricity percentage
        self.CM = [CMx, CMy] # center of mass [x,y] (ft)
        self.dia_angle = dia_angle # Angle of diaphragm (degrees)     
        self.wind_pos = [self.CM, # X load applicaiton location
                         [self.CM[0], self.CM[1] + self.H * self.w_ecc], # X plus eccentricity
                         [self.CM[0], self.CM[1] - self.H * self.w_ecc], # X minus eccentricity
                          self.CM, # Y load application location
                           [self.CM[0] + self.L * self.w_ecc, self.CM[1]], # Y plus eccentricity
                           [self.CM[0] - self.L * self.w_ecc, self.CM[1]]]  # Y minus eccentricity
        self.eq_pos = [self.CM, # X load applicaiton location
                  [self.CM[0], self.CM[1] + self.H * self.eq_ecc], # X plus eccentricity
                  [self.CM[0], self.CM[1] - self.H * self.eq_ecc], # X minus eccentricity
                  self.CM, # Y load application location
                    [self.CM[0] + self.L * self.eq_ecc, self.CM[1]], # Y plus eccentricity
                    [self.CM[0] - self.L * self.eq_ecc, self.CM[1]]]  # Y minus eccentricity
        
        self.loads = ['Wind', 'Seismic']
        self.walls = {} # Dictionary to hold shear walls with their unit load values
        for wall in walls:
            if not isinstance(wall, Wood_ShearWall):
                raise TypeError("All walls must be instances of Wood_ShearWall")
            self.walls[wall.mark] = {load: None for load in self.loads}


class Wood_ShearWall():
    def __init__ (self, mark, CMx, CMy, L, wall_angle, diaphragms, wall_heights, thk = 3.5, floor_trib =  None, roof_trib = None):
        self.mark = mark # ID/mark of the shear wall
        self.L = L # Length of Shear Wall (ft)
        self.CM = [CMx, CMy] # Center of mass of shear wall [x,y] (ft)
        self.wall_angle = wall_angle # Angle of shear wall (degrees)
        self.thk = thk # Thickness of shear wall (inches)
        self.diaphragms = diaphragms # List of Rigid_Diaphragm objects that this shear wall is connected to
        self.wall_heights = np.array(wall_heights) # List of wall heights (ft) for each segment of the wall, as array
        self.floor_trib = floor_trib if floor_trib is not None else [2] * len(self.wall_heights) # Floor tributary lengths (ft)
        self.roof_trib = roof_trib if roof_trib is not None else [2] * len(self.wall_heights) # Roof tributary lengths (ft)
        self.cor = [0, 0] # Center of rigidity [x,y] (ft), initialized to zero

        # Basic attributes that contribute to rigid diaphragm analysis per shear wall
        # Calculations per spreadsheet
        self.delta = 3*self.wall_heights/self.L/self.thk # Deflection of shear wall (inches)
        self.K = 1/self.delta # Stiffness of shear wall
        self.stiffness = {
            "K": self.K,
            "Kxx": self.K * np.cos(np.radians(self.wall_angle))**2, # X Direction
            "Kyy": self.K * np.sin(np.radians(self.wall_angle))**2, # Y Direction
            "Kxy": self.K * np.sin(np.radians(self.wall_angle)) * np.cos(np.radians(self.wall_angle)), # XY Direction
            "xKyy": self.CM[0] * (self.K * np.sin(np.radians(self.wall_angle))**2),
            "yKxx": self.CM[1] * (self.K * np.cos(np.radians(self.wall_angle))**2),
            "xKxy": self.CM[0] * self.K * np.sin(np.radians(self.wall_angle)) * np.cos(np.radians(self.wall_angle)),
            "yKxy": self.CM[1] * self.K * np.sin(np.radians(self.wall_angle)) * np.cos(np.radians(self.wall_angle))
        }
        @property
        def x_bar(self):
            """Calculate the x-bar (center of mass) for the shear wall."""
            return self.CM[0] - self.cor[0]
        @property
        def y_bar(self):
            """Calculate the y-bar (center of mass) for the shear wall."""
            return self.CM[1] - self.cor[1]

        @property
        def bar_stiffness(self):
            """Calculate the bar stiffness based on the wall stiffness and center of mass."""
            return {
                "x_Kyy": self.x_bar**2 * self.stiffness["Kyy"],
                "y_Kxx": self.y_bar**2 * self.stiffness["Kxx"],
                "xy_Kxy": 2 * self.x_bar * self.y_bar * self.stiffness["Kxy"]
            }
        
        @property
        def V_matrix(self):
            """Calculate the unit shears for this shear wall."""
            vx = 0
            vy = 0
            v_dir = 0
            v_dir_abs = 0


        self.Kxx = self.K * np.cos(np.radians(self.wall_angle))**2 # Stiffness in X direction
        self.Kyy = self.K * np.sin(np.radians(self.wall_angle))**2 # Stiffness in Y direction
        self.Kxy = self.K * np.sin(np.radians(self.wall_angle)) * np.cos(np.radians(self.wall_angle)) # Stiffness in XY direction
        self.xKyy = self.CM[0] * self.Kyy # Moment of inertia in Y direction
        self.yKxx = self.CM[1] * self.Kxx # Moment of inertia in X direction


        # Calculations per pdf on Rigid Diaphragm Analysis
        self.delta_pdf = (4*(self.wall_heights/self.L)**3  + (3*self.wall_heights/self.L))/self.thk # Deflection of shear wall (inches)
        self.K_pdf = 1/self.delta_pdf # Stiffness of shear wall



st.title("Rigid Diaphragm Analysis")
st.header("Inputs")
L = st.number_input("Length (EW, ft)", value=194.75, step=0.125)
H = st.number_input("Width (NS, ft)", value=76.25, step=0.125)
CM_x = st.number_input("Center of Mass X", value=-216.897, step=0.125)
CM_y = st.number_input("Center of Mass Y", value=376.539, step=0.125)
dia_angle = st.number_input("Diaphragm Angle", value=0.0, step=0.125)
w_ecc = st.number_input("Wind Eccentricity", value=0.15, step=0.05)
eq_ecc = st.number_input("Seismic Eccentricity", value=0.05, step=0.05)


# Create an instance of the Rigid_Diaphragm class
diaphragm = Rigid_Diaphragm(L, H, CM_x, CM_y, dia_angle, w_ecc, eq_ecc)
st.header("Wind Load Positions")
st.table(pd.DataFrame(diaphragm.wind_pos, columns=['X', 'Y']))
st.header("Seismic Load Positions")
st.table(pd.DataFrame(diaphragm.eq_pos, columns=['X', 'Y']))





# @handcalc()
# def wood_beam_moment_calculation(b, d, L, w, Fb, CD, CM, Ct, CL, CF, Ci):
#     ## Inputs
#     b = b  # Beam width (inches)
#     d = d  # Beam depth (inches)
#     L = L * 12  # Beam span (inches)
#     w = w  # Distributed load (lbf/ft)
#     Fb = Fb  # Reference bending design value (psi)
    
#     ## Calculations
#     # Adjusted bending design value (NDS 2018 Section 4.3.1)
#     Fb_prime = Fb * CD * CM * Ct * CL * CF * Ci

#     # Section modulus (NDS 2018 Section 3.3.2)
#     S = (b * d**2) / 6

#     # Maximum bending moment (simple beam with uniformly distributed load)
#     M_max = (w * L**2) / (8 * 12)  # Convert to lb-in

#     # Actual bending stress (NDS 2018 Section 3.3.2)
#     fb = M_max / S

#     # Moment capacity ratio (NDS 2018 Section 3.3.1)
#     ratio = fb / Fb_prime
#     st.write(f"Locals=")
#     return locals()

# # Streamlit app
# st.title("Wood Beam Moment Calculation (NDS 2018)")

# ## Inputs
# st.header("Inputs")
# b = st.number_input("Beam width (inches)", value=3.5, step=0.125)
# d = st.number_input("Beam depth (inches)", value=9.25, step=0.125)
# L = st.number_input("Beam span (feet)", value=12.0, step=0.5)
# w = st.number_input("Distributed load (lbf/ft)", value=40.0, step=1.0)
# Fb = st.number_input("Reference bending design value (psi)", value=1000.0, step=10.0)
# CD = st.number_input("Load duration factor", value=1.0, step=0.05)
# CM = st.number_input("Wet service factor", value=1.0, step=0.05)
# Ct = st.number_input("Temperature factor", value=1.0, step=0.05)
# CL = st.number_input("Beam stability factor", value=1.0, step=0.05)
# CF = st.number_input("Size factor", value=1.0, step=0.05)
# Ci = st.number_input("Incising factor", value=1.0, step=0.05)

# # Perform calculations
# st.write(f"Inputs: b={b}, d={d}, L={L}, w={w}, Fb={Fb}, CD={CD}, CM={CM}, Ct={Ct}, CL={CL}, CF={CF}, Ci={Ci}")
# latex_code, results = wood_beam_moment_calculation(b, d, L, w, Fb, CD, CM, Ct, CL, CF, Ci)

# ## Summary
# st.header("Summary")
# st.write(f"Moment capacity ratio: {results['ratio']:.3f}")

# ## Calculations
# st.header("Calculations")
# st.latex(latex_code)

# # Additional results
# st.header("Additional Results")
# st.write(f"Adjusted bending design value (Fb'): {results['Fb_prime']:.2f} psi")
# st.write(f"Section modulus (S): {results['S']:.2f} in³")
# st.write(f"Maximum bending moment (M_max): {results['M_max']:.2f} lb-in")
# st.write(f"Actual bending stress (fb): {results['fb']:.2f} psi")
