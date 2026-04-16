import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Simulador Força Eletrostática 2D", layout="wide")

K = 9e9

# ===================== Funções =====================

def sig(x, n=2):
    if x == 0:
        return 0.0
    return float(f"{x:.{n}g}")

def coulomb_force_2d(qi, qj, xi, yi, xj, yj):
    dx = xi - xj
    dy = yi - yj
    r = math.hypot(dx, dy)
    Fx = K * qi * qj * dx / r**3
    Fy = K * qi * qj * dy / r**3
    F = math.hypot(Fx, Fy)
    theta = math.degrees(math.atan2(Fy, Fx))
    return Fx, Fy, F, theta

def sci(x):
    if x == 0:
        return "0"
    exp = int(math.floor(math.log10(abs(x))))
    mant = x / 10**exp
    return f"{mant:.2f}".replace(".", ",") + f"×10{str(exp).translate(str.maketrans('0123456789-','⁰¹²³⁴⁵⁶⁷⁸⁹⁻'))}"

# ===================== Cabeçalho =====================

st.title("Simulador de Força Eletrostática Bidimensional")
st.markdown("Interações entre três partículas carregadas no **plano x–y**.")

# ===================== Controles =====================

st.header("Definições das Partículas")

cols = st.columns(3)
qmin, qmax = -5.0, 5.0
xmin, xmax = -10.0, 10.0

with cols[0]:
    st.subheader("Partícula 1")
    x1 = st.slider("x₁ (m)", xmin, xmax, -4.0, 0.1)
    y1 = st.slider("y₁ (m)", xmin, xmax, 0.0, 0.1)
    q1 = st.slider("q₁ (µC)", qmin, qmax, 2.0, 0.05) * 1e-6

with cols[1]:
    st.subheader("Partícula 2")
    x2 = st.slider("x₂ (m)", xmin, xmax, 4.0, 0.1)
    y2 = st.slider("y₂ (m)", xmin, xmax, 0.0, 0.1)
    q2 = st.slider("q₂ (µC)", qmin, qmax, -2.0, 0.05) * 1e-6

with cols[2]:
    st.subheader("Partícula 3")
    x3 = st.slider("x₃ (m)", xmin, xmax, 0.0, 0.1)
    y3 = st.slider("y₃ (m)", xmin, xmax, 2.0, 0.1)
    q3 = st.slider("q₃ (µC)", qmin, qmax, 1.0, 0.05) * 1e-6

# ===================== Física =====================

Fx13, Fy13, F13, th13 = coulomb_force_2d(q3, q1, x3, y3, x1, y1)
Fx23, Fy23, F23, th23 = coulomb_force_2d(q3, q2, x3, y3, x2, y2)

Fxr = Fx13 + Fx23
Fyr = Fy13 + Fy23
Fr = math.hypot(Fxr, Fyr)
thr = math.degrees(math.atan2(Fyr, Fxr))

# ===================== Figura =====================

st.header("Figura – Sistema Bidimensional")

html = f"""
<canvas id="c" width="700" height="700" style="border:1px solid #ddd"></canvas>
<script>
const c = document.getElementById("c");
const ctx = c.getContext("2d");

const W = c.width, H = c.height;
const xmin = -10, xmax = 10, ymin = -10, ymax = 10;

function X(x) {{ return (x - xmin)/(xmax-xmin)*W; }}
function Y(y) {{ return H - (y - ymin)/(ymax-ymin)*H; }}

ctx.clearRect(0,0,W,H);

// eixos
ctx.strokeStyle="#000";
ctx.beginPath();
ctx.moveTo(X(xmin), Y(0));
ctx.lineTo(X(xmax), Y(0));
ctx.moveTo(X(0), Y(ymin));
ctx.lineTo(X(0), Y(ymax));
ctx.stroke();

// partículas
function part(x,y,n,color){{
 ctx.beginPath();
 ctx.arc(X(x),Y(y),10,0,2*Math.PI);
 ctx.fillStyle="#fff"; ctx.fill();
 ctx.strokeStyle=color; ctx.lineWidth=3; ctx.stroke();
 ctx.fillStyle="#000"; ctx.fillText(n,X(x)-3,Y(y)+4);
}}

part({x1},{y1},"1","red");
part({x2},{y2},"2","blue");
part({x3},{y3},"3","black");

// vetor
function arrow(x,y,dx,dy,color,label){{
 ctx.strokeStyle=color; ctx.fillStyle=color; ctx.lineWidth=3;
 ctx.beginPath(); ctx.moveTo(X(x),Y(y)); ctx.lineTo(X(x+dx),Y(y+dy)); ctx.stroke();
 ctx.setLineDash([5,5]);
 ctx.beginPath(); ctx.moveTo(X(x+dx),Y(y)); ctx.lineTo(X(x+dx),Y(y+dy)); ctx.stroke();
 ctx.beginPath(); ctx.moveTo(X(x),Y(y)); ctx.lineTo(X(x+dx),Y(y)); ctx.stroke();
 ctx.setLineDash([]);
 ctx.fillText(label,X(x+dx)+5,Y(y+dy)+5);
}}

arrow({x3},{y3},{Fx13/Fr*2},{Fy13/Fr*2},"red","F13");
arrow({x3},{y3},{Fx23/Fr*2},{Fy23/Fr*2},"blue","F23");
arrow({x3},{y3},{Fxr/Fr*2},{Fyr/Fr*2},"green","Fr");
</script>
"""
components.html(html, height=720)

# ===================== Resultados =====================

st.header("Forças e Componentes")

def bloco(titulo, Fx, Fy, F, th):
    st.markdown(f"""
**{titulo}**

- \\(F = {sci(F)}\\,\\text{{N}}\\)
- \\(F_x = {sci(Fx)}\\,\\text{{N}}\\)
- \\(F_y = {sci(Fy)}\\,\\text{{N}}\\)
- \\(\\theta = {th:.1f}^\\circ\\)
""")

c1, c2, c3 = st.columns(3)
with c1: bloco("Força F₁₃", Fx13, Fy13, F13, th13)
with c2: bloco("Força F₂₃", Fx23, Fy23, F23, th23)
with c3: bloco("Força Resultante", Fxr, Fyr, Fr, thr)
