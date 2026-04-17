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
const canvas = document.getElementById("canvas2d");
const ctx = canvas.getContext("2d");
const W = canvas.width, H = canvas.height;

const xMin = -15, xMax = 15, yMin = -15, yMax = 15;
const padL = 60, padR = 30, padT = 25, padB = 55;

function X(x){ return padL + (x-xMin)*(W-padL-padR)/(xMax-xMin); }
function Y(y){ return padT + (yMax-y)*(H-padT-padB)/(yMax-yMin); }

// =================== Grade + eixos ===================
function drawAxes(){
  ctx.strokeStyle="#eee";
  for(let t=-14;t<=14;t+=2){
    ctx.beginPath(); ctx.moveTo(X(t),Y(yMin)); ctx.lineTo(X(t),Y(yMax)); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(X(xMin),Y(t)); ctx.lineTo(X(xMax),Y(t)); ctx.stroke();
  }
  ctx.strokeStyle="#111"; ctx.lineWidth=2;
  ctx.beginPath();
  ctx.moveTo(X(xMin),Y(0)); ctx.lineTo(X(xMax),Y(0));
  ctx.moveTo(X(0),Y(yMin)); ctx.lineTo(X(0),Y(yMax));
  ctx.stroke();
}

// =================== Partículas ===================
function drawParticle(x,y,n,color){
  const px=X(x), py=Y(y);
  ctx.beginPath(); ctx.arc(px,py,16,0,2*Math.PI);
  ctx.fillStyle="#fafafa"; ctx.fill();
  ctx.strokeStyle=color; ctx.lineWidth=3; ctx.stroke();
  ctx.fillStyle="#111"; ctx.font="bold 16px Arial";
  ctx.textAlign="center"; ctx.textBaseline="middle";
  ctx.fillText(n,px,py);
  return {px,py};
}

// =================== Setas ===================
function drawArrow(x0,y0,dx,dy,color,label){
  const x1=x0+dx, y1=y0+dy;
  ctx.strokeStyle=color; ctx.lineWidth=3;
  ctx.beginPath(); ctx.moveTo(x0,y0); ctx.lineTo(x1,y1); ctx.stroke();
  const a=Math.atan2(dy,dx), h=10;
  ctx.beginPath();
  ctx.moveTo(x1,y1);
  ctx.lineTo(x1-h*Math.cos(a-Math.PI/6),y1-h*Math.sin(a-Math.PI/6));
  ctx.lineTo(x1-h*Math.cos(a+Math.PI/6),y1-h*Math.sin(a+Math.PI/6));
  ctx.fillStyle=color; ctx.fill();
  ctx.font="14px Arial";
  ctx.fillText(label,x1+6,y1-6);
}

// =================== ESCALA FÍSICA CORRETA ===================

// componentes físicas (vindas do Python)
const Fx13 = {{Fx13}}, Fy13 = {{Fy13}};
const Fx23 = {{Fx23}}, Fy23 = {{Fy23}};
const Fxr  = {{Fxr}},  Fyr  = {{Fyr}};

// maior componente absoluta
const Fref = Math.max(
  Math.abs(Fx13), Math.abs(Fy13),
  Math.abs(Fx23), Math.abs(Fy23),
  Math.abs(Fxr),  Math.abs(Fyr),
  1e-30
);

// comprimento máximo visual (px)
const LMAX = 200;

// fator linear N → pixel
const S = LMAX / Fref;

// =================== Desenho ===================
drawAxes();

const P1 = drawParticle({{x1}},{{y1}},1,"{{col_p1}}");
const P2 = drawParticle({{x2}},{{y2}},2,"{{col_p2}}");
const P3 = drawParticle({{x3}},{{y3}},3,"{{col_p3}}");

// vetores (ESCALA LINEAR)
drawArrow(P3.px,P3.py, S*Fx13, -S*Fy13, "#d62728", "F₁₃");
drawArrow(P3.px,P3.py, S*Fx23, -S*Fy23, "#1f77b4", "F₂₃");
drawArrow(P3.px,P3.py, S*Fxr,  -S*Fyr,  "#2ca02c", "Fᵣ");
</script>
"""
components.html(html, height=620)

# ===================== Resultados =====================
st.header("Resultados")

st.latex(rf"F_{{13x}} = {sig(Fx13,2)}\ \mathrm{{N}},\quad F_{{13y}} = {sig(Fy13,2)}\ \mathrm{{N}}")
st.latex(rf"F_{{rx}} = {sig(Fxr,2)}\ \mathrm{{N}},\quad F_{{ry}} = {sig(Fyr,2)}\ \mathrm{{N}}")
``
