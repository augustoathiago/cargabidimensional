import streamlit as st
import streamlit.components.v1 as components
import math
import json
from string import Template

st.set_page_config(page_title="Simulador Força Eletrostática (2D)", layout="wide")

# ===================== Helpers =====================

def sig(x, n=2):
    """Retorna x com n algarismos significativos (float)."""
    if x == 0 or math.isclose(x, 0.0, abs_tol=0.0):
        return 0.0
    return float(f"{x:.{n}g}")

def br_decimal(s: str) -> str:
    """Troca ponto por vírgula em uma string numérica."""
    return s.replace(".", ",")

_sup_map = str.maketrans("0123456789-+", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺")

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

def br_sci_force_text(x, n=2, unit="N"):
    """Valor em notação científica com vírgula e n algarismos significativos."""
    if x == 0:
        out = "0"
    else:
        mant, exp = sci_parts(x, n=n)
        mant_s = br_decimal(f"{mant:.{n}g}")
        out = f"{mant_s}×10{str(exp).translate(_sup_map)}"
    return f"{out} {unit}".strip()

def fmt_uC_br(q_uC: float) -> str:
    """Retorna a carga do slider em µC com 2 casas e vírgula."""
    return f"{round(q_uC, 2):.2f}".replace(".", ",")

def latex_charge_C_from_uC(q_uC: float) -> str:
    """LaTeX da carga (µC -> C como mantissa×10^{-6})."""
    if math.isclose(q_uC, 0.0, abs_tol=0.0):
        return r"0"
    mant = f"{round(q_uC, 2):.2f}".replace(".", "{,}")
    return rf"{mant}\times10^{{-6}}"

def fmt_pos_br(x: float) -> str:
    """Retorna posição do slider com 1 casa e vírgula."""
    return f"{round(x, 1):.1f}".replace(".", ",")

def br_charge_canvas_from_uC(q_uC: float) -> str:
    """Texto para canvas: q em µC exibido como C em 10^-6."""
    if math.isclose(q_uC, 0.0, abs_tol=0.0):
        return "0 C"
    mant_s = fmt_uC_br(q_uC)
    exp = -6
    return f"{mant_s}×10{str(exp).translate(_sup_map)} C"

def safe_hypot(x, y):
    return math.sqrt(x*x + y*y)

def br_angle_deg(theta_deg: float) -> str:
    """Formata ângulo em graus com 1 casa e vírgula."""
    return br_decimal(f"{theta_deg:.1f}")

def latex_r_2d_from_positions(xa, ya, xb, yb):
    """Mostra r com base na resolução do slider (0,1 m)."""
    dx = round(xa, 1) - round(xb, 1)
    dy = round(ya, 1) - round(yb, 1)
    r = math.sqrt(dx*dx + dy*dy)
    dxs = br_decimal(f"{dx:.1f}").replace("-", "{-}")
    dys = br_decimal(f"{dy:.1f}").replace("-", "{-}")
    rs  = br_decimal(f"{r:.2f}")
    return dxs, dys, rs

# ===================== Física 2D =====================

def coulomb_force_2d(qi, qj, xi, yi, xj, yj, K=9e9):
    """
    Força em i (vetor 2D) devido a j:
      F = K*qi*qj * r_vec / |r|^3, onde r_vec=(xi-xj, yi-yj)
    Retorna (Fx, Fy, r)
    """
    rx = xi - xj
    ry = yi - yj
    r = math.sqrt(rx*rx + ry*ry)
    if math.isclose(r, 0.0, abs_tol=0.0):
        return 0.0, 0.0, 0.0
    coef = K * qi * qj / (r**3)
    Fx = coef * rx
    Fy = coef * ry
    return Fx, Fy, r

# ===================== Cabeçalho =====================

col_logo, col_title = st.columns([1, 5], vertical_alignment="center")
with col_logo:
    try:
        st.image("logo_maua.png", use_container_width=True)
    except Exception:
        st.warning("Arquivo 'logo_maua.png' não encontrado na raiz do repositório.")
with col_title:
    st.title("Simulador Força Eletrostática Bidimensional (x,y)")
    st.write(
        "Veja as forças aplicadas na partícula carregada **3** quando posicionada no plano "
        "próxima a outras duas partículas carregadas **1** e **2**."
    )
    st.markdown("**Desafio: encontre uma situação onde a partícula 3 está em equilíbrio ou quase em equilíbrio (Fᵣ ~ 0).**")

# ===================== Controles =====================

st.header("Definições das Partículas (2D)")

col1, col2, col3 = st.columns(3)

qmin_uC, qmax_uC, qstep_uC = -5.0, 5.0, 0.05
xmin_slider, xmax_slider = -10.0, 10.0
ymin_slider, ymax_slider = -10.0, 10.0

with col1:
    st.subheader("Partícula 1")
    x1 = st.slider("Posição x₁ (m)", xmin_slider, xmax_slider, -4.0, 0.1, format="%.1f")
    y1 = st.slider("Posição y₁ (m)", ymin_slider, ymax_slider,  0.0, 0.1, format="%.1f")
    q1_uC = st.slider("Carga q₁ (µC)", qmin_uC, qmax_uC, 2.0, qstep_uC, format="%.2f")
    q1 = q1_uC * 1e-6

with col2:
    st.subheader("Partícula 2")
    x2 = st.slider("Posição x₂ (m)", xmin_slider, xmax_slider,  4.0, 0.1, format="%.1f")
    y2 = st.slider("Posição y₂ (m)", ymin_slider, ymax_slider,  0.0, 0.1, format="%.1f")
    q2_uC = st.slider("Carga q₂ (µC)", qmin_uC, qmax_uC, -2.0, qstep_uC, format="%.2f")
    q2 = q2_uC * 1e-6

with col3:
    st.subheader("Partícula 3")
    x3 = st.slider("Posição x₃ (m)", xmin_slider, xmax_slider,  0.0, 0.1, format="%.1f")
    y3 = st.slider("Posição y₃ (m)", ymin_slider, ymax_slider,  0.0, 0.1, format="%.1f")
    q3_uC = st.slider("Carga q₃ (µC)", qmin_uC, qmax_uC,  1.0, qstep_uC, format="%.2f")
    q3 = q3_uC * 1e-6

# Bloqueio de posições iguais (mesmo ponto no plano)
pts = {(x1, y1), (x2, y2), (x3, y3)}
if len(pts) < 3:
    st.error("❌ As partículas **não podem** estar na mesma posição (mesmo ponto (x,y)). Ajuste as posições.")
    st.stop()

# ===================== Cálculos =====================

K = 9.0e9

F13x_raw, F13y_raw, r13 = coulomb_force_2d(q3, q1, x3, y3, x1, y1, K=K)
F23x_raw, F23y_raw, r23 = coulomb_force_2d(q3, q2, x3, y3, x2, y2, K=K)

# Componentes exibidas com 2 AS
F13x = sig(F13x_raw, 2)
F13y = sig(F13y_raw, 2)
F23x = sig(F23x_raw, 2)
F23y = sig(F23y_raw, 2)

# Resultante DIDÁTICA: soma usando componentes exibidas (2 AS)
Frx = sig(F13x + F23x, 2)
Fry = sig(F13y + F23y, 2)

# Módulos e ângulos a partir do exibido
F13 = sig(safe_hypot(F13x, F13y), 2)
F23 = sig(safe_hypot(F23x, F23y), 2)
Fr  = sig(safe_hypot(Frx,  Fry),  2)

theta13 = math.degrees(math.atan2(F13y, F13x)) if not (F13x == 0 and F13y == 0) else 0.0
theta23 = math.degrees(math.atan2(F23y, F23x)) if not (F23x == 0 and F23y == 0) else 0.0
thetar  = math.degrees(math.atan2(Fry,  Frx))  if not (Frx  == 0 and Fry  == 0) else 0.0

equilibrio = (Frx == 0.0 and Fry == 0.0)

# ===================== Figura 2D (Canvas) =====================

st.header("Figura – Sistema Bidimensional (x,y)")

# limites do plano mostrado
xMin, xMax = -15.0, 15.0
yMin, yMax = -12.0, 12.0
xticks = list(range(-15, 16, 3))
yticks = list(range(-12, 13, 3))

# escala dos vetores (pixels)
maxVec = max(F13, F23, Fr, 1e-30)
Lmax = 150.0

def vec_scale(Fmag):
    return Lmax * (abs(Fmag) / maxVec)

def force_to_pixel_dxdy(Fx, Fy, Fmag):
    if Fmag == 0:
        return 0.0, 0.0
    s = vec_scale(Fmag) / Fmag
    return Fx * s, -Fy * s  # y invertido no canvas

dx13, dy13 = force_to_pixel_dxdy(F13x, F13y, F13)
dx23, dy23 = force_to_pixel_dxdy(F23x, F23y, F23)
dxr,  dyr  = force_to_pixel_dxdy(Frx,  Fry,  Fr)

# Strings para rótulos das cargas
q1_str = br_charge_canvas_from_uC(q1_uC)
q2_str = br_charge_canvas_from_uC(q2_uC)
q3_str = br_charge_canvas_from_uC(q3_uC)

# Dados enviados ao JS via JSON (sem f-string com chaves do JS!)
DATA = {
    "xMin": xMin, "xMax": xMax, "yMin": yMin, "yMax": yMax,
    "xticks": xticks, "yticks": yticks,
    "p1": {"x": x1, "y": y1, "q": q1, "qText": q1_str},
    "p2": {"x": x2, "y": y2, "q": q2, "qText": q2_str},
    "p3": {"x": x3, "y": y3, "q": q3, "qText": q3_str},
    "vec": {
        "F13": {"dx": dx13, "dy": dy13},
        "F23": {"dx": dx23, "dy": dy23},
        "Fr":  {"dx": dxr,  "dy": dyr},
    }
}

canvas_template = Template(r"""
<div id="canvasWrap" style="
    width: 100%;
    overflow: auto;
    -webkit-overflow-scrolling: touch;
    cursor: grab;
    user-select: none;
    touch-action: pan-x pan-y;
">
  <canvas id="canvas" width="1050" height="560"
    style="background: white; border: 1px solid #eee; display: block;">
  </canvas>
</div>

<script>
const DATA = $DATA_JSON;

const wrap = document.getElementById("canvasWrap");
let isDown = false;
let startX = 0, startY = 0;
let startScrollLeft = 0, startScrollTop = 0;
let activePointerId = null;

wrap.addEventListener("pointerdown", (e) => {
  if (e.pointerType === "mouse" && e.button !== 0) return;
  isDown = true;
  activePointerId = e.pointerId;
  wrap.setPointerCapture(activePointerId);
  startX = e.clientX;
  startY = e.clientY;
  startScrollLeft = wrap.scrollLeft;
  startScrollTop = wrap.scrollTop;
  wrap.style.cursor = "grabbing";
});

wrap.addEventListener("pointermove", (e) => {
  if (!isDown) return;
  if (activePointerId !== e.pointerId) return;
  const dx = e.clientX - startX;
  const dy = e.clientY - startY;
  wrap.scrollLeft = startScrollLeft - dx;
  wrap.scrollTop  = startScrollTop  - dy;
});

function endDrag(e) {
  if (activePointerId !== null && e.pointerId !== activePointerId) return;
  isDown = false;
  activePointerId = null;
  wrap.style.cursor = "grab";
}
wrap.addEventListener("pointerup", endDrag);
wrap.addEventListener("pointercancel", endDrag);

// ===================== desenho =====================
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const W = canvas.width;
const H = canvas.height;

ctx.clearRect(0, 0, W, H);
ctx.fillStyle = "white";
ctx.fillRect(0, 0, W, H);

const xMin = DATA.xMin, xMax = DATA.xMax, yMin = DATA.yMin, yMax = DATA.yMax;
const xticks = DATA.xticks, yticks = DATA.yticks;

const padL = 70, padR = 30, padT = 30, padB = 70;

function X(x) {
  return padL + (x - xMin) * ((W - padL - padR) / (xMax - xMin));
}
function Y(y) {
  return padT + (yMax - y) * ((H - padT - padB) / (yMax - yMin));
}

function drawAxes() {
  // grade
  ctx.strokeStyle = "#f0f0f0";
  ctx.lineWidth = 1;

  xticks.forEach(t => {
    const px = X(t);
    ctx.beginPath();
    ctx.moveTo(px, padT);
    ctx.lineTo(px, H - padB);
    ctx.stroke();
  });
  yticks.forEach(t => {
    const py = Y
