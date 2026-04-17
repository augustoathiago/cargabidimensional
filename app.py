import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Simulador Força Eletrostática 2D", layout="wide")

# ===================== Constantes =====================
K = 9.0e9  # N·m²/C²

# ===================== Helpers =====================
def sig(x, n=2):
    """Retorna x com n algarismos significativos (float)."""
    if x == 0 or math.isclose(x, 0.0, abs_tol=0.0):
        return 0.0
    return float(f"{x:.{n}g}")

def sci_parts(x, n=2):
    """Retorna (mantissa, expoente) com n algarismos significativos na mantissa."""
    if x == 0:
        return 0.0, 0
    exp = int(math.floor(math.log10(abs(x))))
    mant = x / (10 ** exp)
    mant = float(f"{mant:.{n}g}")
    if abs(mant) >= 10:
        mant /= 10
        exp += 1
    return mant, exp

def latex_sci(x, n=2, unit=r"\mathrm{N}"):
    """Notação científica LaTeX com vírgula e unidade."""
    if x == 0 or math.isclose(x, 0.0, abs_tol=0.0):
        return rf"0\,{unit}"
    mant, exp = sci_parts(x, n=n)
    mant_s = f"{mant:.{n}g}".replace(".", "{,}")
    return rf"{mant_s}\times10^{{{exp}}}\,{unit}"

def latex_sci_no_unit(x, n=2):
    """Notação científica LaTeX com vírgula, sem unidade."""
    if x == 0 or math.isclose(x, 0.0, abs_tol=0.0):
        return r"0"
    mant, exp = sci_parts(x, n=n)
    mant_s = f"{mant:.{n}g}".replace(".", "{,}")
    return rf"{mant_s}\times10^{{{exp}}}"

def latex_charge_C_from_uC(q_uC: float) -> str:
    """Exibe exatamente o valor do slider (2 casas) como mantissa × 10^{-6} em Coulomb."""
    if math.isclose(q_uC, 0.0, abs_tol=0.0):
        return r"0"
    mant = f"{round(q_uC, 2):.2f}".replace(".", "{,}")
    return rf"{mant}\times10^{{-6}}"

def arrow_x(val, tol=0.0):
    if abs(val) <= tol:
        return r"\leftrightarrow"
    return r"\rightarrow" if val > 0 else r"\leftarrow"

def arrow_y(val, tol=0.0):
    if abs(val) <= tol:
        return r"\updownarrow"
    return r"\uparrow" if val > 0 else r"\downarrow"

def coulomb_force_2d(qi, qj, xi, yi, xj, yj, K=9e9):
    """
    Força em i devido a j:
    F = k*qi*qj*(ri-rj)/|ri-rj|^3
    Retorna Fx, Fy, |F|, theta (graus), r
    """
    dx = xi - xj
    dy = yi - yj
    r = math.hypot(dx, dy)
    Fx = K * qi * qj * dx / (r**3)
    Fy = K * qi * qj * dy / (r**3)
    F = math.hypot(Fx, Fy)
    theta = math.degrees(math.atan2(Fy, Fx)) if F != 0 else 0.0
    return Fx, Fy, F, theta, r

def color_charge(q):
    eps = 1e-15
    if q > eps:
        return "#d62728"  # vermelho
    if q < -eps:
        return "#1f77b4"  # azul
    return "#111111"

# ===================== Cabeçalho =====================
col_logo, col_title = st.columns([1, 5], vertical_alignment="center")
with col_logo:
    try:
        st.image("logo_maua.png", use_container_width=True)
    except Exception:
        st.caption("logo_maua.png (opcional)")
with col_title:
    st.title("Simulador de Força Eletrostática Bidimensional (2D)")
    st.write(
        "Veja as forças aplicadas na partícula carregada **3** quando posicionada no plano **x–y** "
        "próxima às partículas carregadas **1** e **2**."
    )

# ===================== Controles =====================
st.header("Definições das Partículas (x, y e carga)")

qmin_uC, qmax_uC, qstep_uC = -5.0, 5.0, 0.05
xmin_slider, xmax_slider = -10.0, 10.0
ymin_slider, ymax_slider = -10.0, 10.0

c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("Partícula 1")
    x1 = st.slider("x₁ (m)", xmin_slider, xmax_slider, -4.0, 0.1, format="%.1f")
    y1 = st.slider("y₁ (m)", ymin_slider, ymax_slider,  0.0, 0.1, format="%.1f")
    q1_uC = st.slider("q₁ (µC)", qmin_uC, qmax_uC, 2.0, qstep_uC, format="%.2f")
    q1 = q1_uC * 1e-6

with c2:
    st.subheader("Partícula 2")
    x2 = st.slider("x₂ (m)", xmin_slider, xmax_slider,  4.0, 0.1, format="%.1f")
    y2 = st.slider("y₂ (m)", ymin_slider, ymax_slider,  0.0, 0.1, format="%.1f")
    q2_uC = st.slider("q₂ (µC)", qmin_uC, qmax_uC, -2.0, qstep_uC, format="%.2f")
    q2 = q2_uC * 1e-6

with c3:
    st.subheader("Partícula 3")
    x3 = st.slider("x₃ (m)", xmin_slider, xmax_slider,  0.0, 0.1, format="%.1f")
    y3 = st.slider("y₃ (m)", ymin_slider, ymax_slider,  2.0, 0.1, format="%.1f")
    q3_uC = st.slider("q₃ (µC)", qmin_uC, qmax_uC,  1.0, qstep_uC, format="%.2f")
    q3 = q3_uC * 1e-6

# ===================== Restrição: não permitir mesma posição =====================
p1 = (round(x1, 1), round(y1, 1))
p2 = (round(x2, 1), round(y2, 1))
p3 = (round(x3, 1), round(y3, 1))
if len({p1, p2, p3}) < 3:
    st.error("❌ As partículas **não podem** estar na mesma posição (x, y). Ajuste os sliders.")
    st.stop()

# ===================== Física =====================
Fx13, Fy13, F13, th13, r13 = coulomb_force_2d(q3, q1, x3, y3, x1, y1, K=K)
Fx23, Fy23, F23, th23, r23 = coulomb_force_2d(q3, q2, x3, y3, x2, y2, K=K)

Fxr = Fx13 + Fx23
Fyr = Fy13 + Fy23
Fr  = math.hypot(Fxr, Fyr)
thr = math.degrees(math.atan2(Fyr, Fxr)) if Fr != 0 else 0.0

# versão didática 2 AS (para exibir nos resultados)
Fx13_d, Fy13_d, F13_d = sig(Fx13, 2), sig(Fy13, 2), sig(F13, 2)
Fx23_d, Fy23_d, F23_d = sig(Fx23, 2), sig(Fy23, 2), sig(F23, 2)
Fxr_d,  Fyr_d,  Fr_d  = sig(Fxr,  2), sig(Fyr,  2), sig(Fr,  2)

# produtos para sentido (atração/repulsão) na direção central
prod13 = q1 * q3
prod23 = q2 * q3

# ===================== Figura (Canvas) =====================
st.header("Figura – Sistema Bidimensional")

xMin, xMax = -15, 15
yMin, yMax = -15, 15
ticks = list(range(-14, 15, 2))  # ticks de 2 em 2 (inclui 0)

col_p1 = color_charge(q1)
col_p2 = color_charge(q2)
col_p3 = color_charge(q3)  # partícula 3 com borda por carga

maxF = max(abs(F13), abs(F23), abs(Fr), 1e-30)

html = f"""
<div style="background:white;padding:6px;border-radius:14px;border:1px solid #eee;">
  <canvas id="canvas2d" width="920" height="620"
    style="background:white;border:1px solid #e9e9e9;display:block;border-radius:12px;"></canvas>
</div>

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
``
"""
components.html(html, height=650)

# ===================== Distâncias (só valores) =====================
st.header("Distâncias")
d1, d2 = st.columns(2)
with d1:
    st.latex(rf"r_{{13}} = {latex_sci(r13, 2, r'\mathrm{{m}}')}")
with d2:
    st.latex(rf"r_{{23}} = {latex_sci(r23, 2, r'\mathrm{{m}}')}")

# ===================== Forças Eletrostáticas (2D) =====================
st.header("Forças Eletrostáticas")

st.latex(r"F_{13}=K\frac{|q_1q_3|}{r_{13}^2}")
st.latex(r"F_{23}=K\frac{|q_2q_3|}{r_{23}^2}")
st.latex(r"K = 9{,}0\times10^9\ \mathrm{N\,m^2/C^2}")
st.markdown("onde **q** são as cargas das partículas, **r** são as distâncias entre elas e **K** é a constante de Coulomb.")

st.subheader("Substituição numérica (módulos)")

q1_ltx = latex_charge_C_from_uC(q1_uC)
q2_ltx = latex_charge_C_from_uC(q2_uC)
q3_ltx = latex_charge_C_from_uC(q3_uC)

r13_ltx = latex_sci_no_unit(r13, 2)
r23_ltx = latex_sci_no_unit(r23, 2)

st.latex(rf"F_{{13}} = (9{{,}}0\times10^9)\cdot\frac{{\left|({q1_ltx})({q3_ltx})\right|}}{{({r13_ltx})^2}}")
st.latex(rf"F_{{13}} = {latex_sci(abs(sig(F13,2)), 2, r'\mathrm{{N}}')}")

st.latex(rf"F_{{23}} = (9{{,}}0\times10^9)\cdot\frac{{\left|({q2_ltx})({q3_ltx})\right|}}{{({r23_ltx})^2}}")
st.latex(rf"F_{{23}} = {latex_sci(abs(sig(F23,2)), 2, r'\mathrm{{N}}')}")

# ===================== Resultados =====================
st.header("Resultados (módulo, componentes e direção)")

def results_block(title, color, Fmag, Fx, Fy, theta, label_main):
    mag_s = latex_sci(sig(Fmag, 2), 2, r"\mathrm{N}")
    fx_s  = latex_sci(sig(Fx,   2), 2, r"\mathrm{N}")
    fy_s  = latex_sci(sig(Fy,   2), 2, r"\mathrm{N}")
    th_s  = f"{theta:.1f}".replace(".", "{,}")

    st.markdown(
        f"""
        <div style="background:#ffffff;border:1px solid #eee;border-radius:14px;
                    padding:12px 14px; box-shadow:0 1px 8px rgba(0,0,0,0.06);">
          <div style="font-size:14px;color:#333;">
            <b style="color:{color};">●</b> <b>{title}</b>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.latex(rf"{label_main} = {mag_s}")

    # componentes + setas (com correção do \qquad para não "grudar" no F)
    st.latex(
        rf"{label_main}x = {fx_s}\ {arrow_x(sig(Fx,2))}"
        rf"\qquad,\qquad "
        rf"{label_main}y = {fy_s}\ {arrow_y(sig(Fy,2))}"
    )

    st.latex(rf"\theta = {th_s}^\circ")

colA, colB, colC = st.columns(3)
with colA:
    results_block("Força na partícula 3 devido à partícula 1", "#d62728",
                  abs(F13), Fx13, Fy13, th13, r"F_{13}")
with colB:
    results_block("Força na partícula 3 devido à partícula 2", "#1f77b4",
                  abs(F23), Fx23, Fy23, th23, r"F_{23}")
with colC:
    results_block("Força resultante na partícula 3", "#2ca02c",
                  abs(Fr),  Fxr,  Fyr,  thr,  r"F_{r}")
