import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Simulador Força Eletrostática 2D", layout="wide")

K = 9e9

# ===================== Física =====================
def coulomb_force_2d(qi, qj, xi, yi, xj, yj):
    dx = xi - xj
    dy = yi - yj
    r = math.hypot(dx, dy)
    Fx = K * qi * qj * dx / r**3
    Fy = K * qi * qj * dy / r**3
    F = math.hypot(Fx, Fy)
    theta = math.degrees(math.atan2(Fy, Fx))
    return Fx, Fy, F, theta, r

def sig(x, n=2):
    if x == 0:
        return 0.0
    return float(f"{x:.{n}g}")

# ===================== Interface =====================
st.title("Simulador de Força Eletrostática Bidimensional (2D)")

c1, c2, c3 = st.columns(3)

with c1:
    x1 = st.slider("x₁ (m)", -10.0, 10.0, -4.0, 0.1)
    y1 = st.slider("y₁ (m)", -10.0, 10.0, 0.0, 0.1)
    q1 = st.slider("q₁ (µC)", -5.0, 5.0, 2.0, 0.05) * 1e-6

with c2:
    x2 = st.slider("x₂ (m)", -10.0, 10.0, 4.0, 0.1)
    y2 = st.slider("y₂ (m)", -10.0, 10.0, 0.0, 0.1)
    q2 = st.slider("q₂ (µC)", -5.0, 5.0, -2.0, 0.05) * 1e-6

with c3:
    x3 = st.slider("x₃ (m)", -10.0, 10.0, 0.0, 0.1)
    y3 = st.slider("y₃ (m)", -10.0, 10.0, 2.0, 0.1)
    q3 = st.slider("q₃ (µC)", -5.0, 5.0, 1.0, 0.05) * 1e-6

# ===================== Forças =====================
Fx13, Fy13, F13, th13, _ = coulomb_force_2d(q3, q1, x3, y3, x1, y1)
Fx23, Fy23, F23, th23, _ = coulomb_force_2d(q3, q2, x3, y3, x2, y2)

Fxr = Fx13 + Fx23
Fyr = Fy13 + Fy23
Fr = math.hypot(Fxr, Fyr)

# ===================== Escala FÍSICA ÚNICA =====================
Fmax = max(abs(F13), abs(F23), abs(Fr), 1e-30)

html = f"""
<canvas id="c" width="900" height="600" style="border:1px solid #ddd;"></canvas>
<script>
const c = document.getElementById("c");
const ctx = c.getContext("2d");

const W = c.width, H = c.height;
const xmin = -15, xmax = 15, ymin = -15, ymax = 15;
const pad = 60;

function X(x) {{
  return pad + (x-xmin)/(xmax-xmin)*(W-2*pad);
}}
function Y(y) {{
  return pad + (ymax-y)/(ymax-ymin)*(H-2*pad);
}}

ctx.clearRect(0,0,W,H);

// eixos
ctx.beginPath();
ctx.moveTo(X(xmin), Y(0));
ctx.lineTo(X(xmax), Y(0));
ctx.moveTo(X(0), Y(ymin));
ctx.lineTo(X(0), Y(ymax));
ctx.stroke();

// partículas
function particle(x,y,n,color) {{
  ctx.beginPath();
  ctx.arc(X(x),Y(y),14,0,2*Math.PI);
  ctx.fillStyle="#fff"; ctx.fill();
  ctx.strokeStyle=color; ctx.lineWidth=3; ctx.stroke();
  ctx.fillStyle="#000"; ctx.fillText(n,X(x)-4,Y(y)+4);
}}

particle({x1},{y1},"1","blue");
particle({x2},{y2},"2","blue");
particle({x3},{y3},"3","red");

// ESCALA ÚNICA (a chave da correção)
const Lmax = 0.4*(W-2*pad);
const scale = Lmax / {Fmax};

// vetor genérico
function drawVector(Fx,Fy,color,label) {{
  const dx = Fx*scale;
  const dy = -Fy*scale;

  const x0 = X({x3});
  const y0 = Y({y3});

  ctx.strokeStyle=color;
  ctx.lineWidth=3;
  ctx.beginPath();
  ctx.moveTo(x0,y0);
  ctx.lineTo(x0+dx,y0+dy);
  ctx.stroke();

  // componentes (corretas!)
  ctx.setLineDash([6,5]);
  ctx.beginPath();
  ctx.moveTo(x0,y0);
  ctx.lineTo(x0+dx,y0);
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(x0+dx,y0);
  ctx.lineTo(x0+dx,y0+dy);
  ctx.stroke();
  ctx.setLineDash([]);
}}

drawVector({Fx13},{Fy13},"red","F13");
drawVector({Fx23},{Fy23},"blue","F23");
drawVector({Fxr},{Fyr},"green","Fr");
</script>
"""
components.html(html, height=620)

# ===================== Resultados =====================
st.header("Resultados")

st.latex(rf"F_{{13x}} = {sig(Fx13,2)}\ \mathrm{{N}},\quad F_{{13y}} = {sig(Fy13,2)}\ \mathrm{{N}}")
st.latex(rf"F_{{rx}} = {sig(Fxr,2)}\ \mathrm{{N}},\quad F_{{ry}} = {sig(Fyr,2)}\ \mathrm{{N}}")
``
