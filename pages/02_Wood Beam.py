from handcalcs.decorator import handcalc
import streamlit as st
import math

@handcalc()
def wood_beam_moment_calculation(b, d, L, w, Fb, CD, CM, Ct, CL, CF, Ci):
    ## Inputs
    b = b  # Beam width (inches)
    d = d  # Beam depth (inches)
    L = L * 12  # Beam span (inches)
    w = w  # Distributed load (lbf/ft)
    Fb = Fb  # Reference bending design value (psi)
    
    ## Calculations
    # Adjusted bending design value (NDS 2018 Section 4.3.1)
    Fb_prime = Fb * CD * CM * Ct * CL * CF * Ci

    # Section modulus (NDS 2018 Section 3.3.2)
    S = (b * d**2) / 6

    # Maximum bending moment (simple beam with uniformly distributed load)
    M_max = (w * L**2) / (8 * 12)  # Convert to lb-in

    # Actual bending stress (NDS 2018 Section 3.3.2)
    fb = M_max / S

    # Moment capacity ratio (NDS 2018 Section 3.3.1)
    ratio = fb / Fb_prime
    st.write(f"Locals= {locals()}")
    return locals()

# Streamlit app
st.title("Wood Beam Moment Calculation (NDS 2018)")

## Inputs
st.header("Inputs")
b = st.number_input("Beam width (inches)", value=3.5, step=0.125)
d = st.number_input("Beam depth (inches)", value=9.25, step=0.125)
L = st.number_input("Beam span (feet)", value=12.0, step=0.5)
w = st.number_input("Distributed load (lbf/ft)", value=40.0, step=1.0)
Fb = st.number_input("Reference bending design value (psi)", value=1000.0, step=10.0)
CD = st.number_input("Load duration factor", value=1.0, step=0.05)
CM = st.number_input("Wet service factor", value=1.0, step=0.05)
Ct = st.number_input("Temperature factor", value=1.0, step=0.05)
CL = st.number_input("Beam stability factor", value=1.0, step=0.05)
CF = st.number_input("Size factor", value=1.0, step=0.05)
Ci = st.number_input("Incising factor", value=1.0, step=0.05)

# Perform calculations
st.write(f"Inputs: b={b}, d={d}, L={L}, w={w}, Fb={Fb}, CD={CD}, CM={CM}, Ct={Ct}, CL={CL}, CF={CF}, Ci={Ci}")
latex_code, results = wood_beam_moment_calculation(b, d, L, w, Fb, CD, CM, Ct, CL, CF, Ci)

## Summary
st.header("Summary")
st.write(f"Moment capacity ratio: {results['ratio']:.3f}")

## Calculations
st.header("Calculations")
st.latex(latex_code)

# Additional results
st.header("Additional Results")
st.write(f"Adjusted bending design value (Fb'): {results['Fb_prime']:.2f} psi")
st.write(f"Section modulus (S): {results['S']:.2f} in³")
st.write(f"Maximum bending moment (M_max): {results['M_max']:.2f} lb-in")
st.write(f"Actual bending stress (fb): {results['fb']:.2f} psi")
