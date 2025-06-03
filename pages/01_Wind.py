from math import sqrt
from handcalcs.decorator import handcalc
import streamlit as st

# @handcalc(override='latex', jupyter_display=False)
# def my_calc():
#     a = 2
#     b = 3
#     c = 2*a + b/3
#     return c
# result, latex = my_calc()

# @handcalc()
# @handcalc(override='latex', jupyter_display=False)
# def quadratic(a,b,c):
#     x_1 = (-b + sqrt(b**2 - 4*a*c)) / (2*a)
#     x_5 = (-b - sqrt(b**2 - 4*a*c)) / (2*a)
#     return locals()

# a = st.slider("Value for a:", 1, 5, 5)
# b = st.slider("Value for b:", -10, 10, -5)
# c = st.slider("Value for c:", -20, 0, -5)

# st.write("Quadratic equation in x:")
# st.latex(f"{a}x^2 + {b}x + {c} = 0")
# latex_code, vals = quadratic(a,b,c)
# st.write(f"Latex={latex_code}")
# st.latex(latex_code)


class MyClass:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    @handcalc(override='latex', jupyter_display=False)
    def my_method(self):
        a = self.a  # Assign instance to local variable
        b = self.b
        c = a + b
        return c


st.title("Wind Calculation Example")
a = st.slider("Value for a:", 1, 5, 5)
b = st.slider("Value for b:", -10, 10, -5)
my_instance = MyClass(a, b)
latex, result = my_instance.my_method()
st.write("Result of my_method:")
st.write(result)
st.write("Latex representation:")
st.latex(latex)