from math import sqrt
from handcalcs.decorator import handcalc
import streamlit as st

@handcalc(override='latex', jupyter_display=False)
def my_calc():
    a = 2
    b = 3
    c = 2*a + b/3
    return c

a = st.slider("Value for a:", 1, 5, 5)
b = st.slider("Value for b:", -10, 10, -5)
c = st.slider("Value for c:", -20, 0, -5)

st.write("Quadratic equation in x:")
st.latex(f"{a}x^2 + {b}x + {c} = 0")

latex_code, vals = my_calc(a,b,c)
st.latex(latex_code)


# @handcalc()
# def quadratic(a,b,c):
#     x_1 = (-b + sqrt(b**2 - 4*a*c)) / (2*a)
#     x_2 = (-b - sqrt(b**2 - 4*a*c)) / (2*a)
#     return x_1

# a = st.slider("Value for a:", 1, 5, 5)
# b = st.slider("Value for b:", -10, 10, -5)
# c = st.slider("Value for c:", -20, 0, -5)

# st.write("Quadratic equation in x:")
# st.latex(f"{a}x^2 + {b}x + {c} = 0")

# latex_code, vals = quadratic(a,b,c)
# st.latex(latex_code)
