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
        return "⟷"
    return "→" if val > 0 else "←"

def arrow_y(val, tol=0.0):
    if abs(val) <= tol:
        return "↕"
    return "↑" if val > 0 else "↓"

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

# exibição com 2 AS
Fx13_d, Fy13_d, F13_d = sig(Fx13, 2), sig(Fy13, 2), sig(F13, 2)
Fx23_d, Fy23_d, F23_d = sig(Fx23, 2), sig(Fy23, 2), sig(F23, 2)
Fxr_d,  Fyr_d,  Fr_d  = sig(Fxr,  2), sig(Fyr,  2), sig(Fr,  2)

# ===================== Figura (Canvas) =====================
st.header("Figura – Sistema Bidimensional")

# faixa fixa do gráfico: -15 a 15
xMin, xMax = -15, 15
yMin, yMax = -15, 15
ticks = list(range(-14, 15, 2))  # ticks de 2 em 2 (evita poluição com -15)

col_p1 = color_charge(q1)
col_p2 = color_charge(q2)
col_p3 = color_charge(q3)

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

// fundo branco
ctx.fillStyle = "white";
ctx.fillRect(0,0,W,H);

const xMin = {xMin}, xMax = {xMax}, yMin = {yMin}, yMax = {yMax};
const padL = 60, padR = 30, padT = 25, padB = 55;

function X(x) {{
  return padL + (x - xMin) * ((W - padL - padR) / (xMax - xMin));
}}
function Y(y) {{
  return padT + (yMax - y) * ((H - padT - padB) / (yMax - yMin));
}}

// ---------------- Grade cinza claro (pedido) ----------------
function drawGrid() {{
  const ticks = {ticks};
  ctx.save();
  ctx.strokeStyle = "#eeeeee";
  ctx.lineWidth = 1;

  // verticais
  ticks.forEach(t => {{
    ctx.beginPath();
    ctx.moveTo(X(t), Y(yMin));
    ctx.lineTo(X(t), Y(yMax));
    ctx.stroke();
  }});
  // horizontais
  ticks.forEach(t => {{
    ctx.beginPath();
    ctx.moveTo(X(xMin), Y(t));
    ctx.lineTo(X(xMax), Y(t));
    ctx.stroke();
  }});

  ctx.restore();
}}

// ---------------- Eixos e ticks ----------------
function drawAxes() {{
  drawGrid();

  // eixos principais
  ctx.strokeStyle = "#111";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(X(xMin), Y(0));
  ctx.lineTo(X(xMax), Y(0));
  ctx.moveTo(X(0), Y(yMin));
  ctx.lineTo(X(0), Y(yMax));
  ctx.stroke();

  // ticks e labels
  const ticks = {ticks};
  ctx.fillStyle = "#111";
  ctx.font = "12px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "top";

  ticks.forEach(t => {{
    // ticks em x
    ctx.beginPath();
    ctx.moveTo(X(t), Y(0)-6);
    ctx.lineTo(X(t), Y(0)+6);
    ctx.stroke();
    ctx.fillText(String(t), X(t), Y(0)+10);
  }});

  ctx.textAlign = "right";
  ctx.textBaseline = "middle";
  ticks.forEach(t => {{
    // ticks em y
    ctx.beginPath();
    ctx.moveTo(X(0)-6, Y(t));
    ctx.lineTo(X(0)+6, Y(t));
    ctx.stroke();
    if (t !== 0) ctx.fillText(String(t), X(0)-10, Y(t));
  }});

  // nomes dos eixos
  ctx.textAlign = "right";
  ctx.textBaseline = "bottom";
  ctx.fillText("x (m)", X(xMax), Y(0)-10);
  ctx.textAlign = "left";
  ctx.textBaseline = "top";
  ctx.fillText("y (m)", X(0)+10, Y(yMax));
}}

function drawParticle(x,y,n,colorBorder) {{
  const px = X(x), py = Y(y);
  ctx.fillStyle = "#fafafa";
  ctx.strokeStyle = colorBorder;
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(px, py, 16, 0, 2*Math.PI);
  ctx.fill();
  ctx.stroke();

  ctx.fillStyle = "#111";
  ctx.font = "bold 16px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(String(n), px, py);
  return {{px, py}};
}}

function drawVectorOverLabel(text, xAnchor, yBaseline, align, color) {{
  // setinha sobre o rótulo para indicar vetor
  ctx.save();
  ctx.font = "14px Arial";
  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.lineWidth = 2;

  const w = ctx.measureText(text).width;
  let xLeft = xAnchor;
  if (align === "right") xLeft = xAnchor - w;

  const yArrow = yBaseline - 16;
  ctx.beginPath();
  ctx.moveTo(xLeft, yArrow);
  ctx.lineTo(xLeft + w, yArrow);
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(xLeft + w, yArrow);
  ctx.lineTo(xLeft + w - 6, yArrow - 4);
  ctx.lineTo(xLeft + w - 6, yArrow + 4);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}}

function drawArrowPix(x0, y0, dx, dy, color, label) {{
  ctx.save();
  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.lineWidth = 3;

  const x1 = x0 + dx;
  const y1 = y0 + dy;

  // linha
  ctx.beginPath();
  ctx.moveTo(x0, y0);
  ctx.lineTo(x1, y1);
  ctx.stroke();

  // cabeça
  const ang = Math.atan2(dy, dx);
  const head = 10;
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x1 - head*Math.cos(ang - Math.PI/6), y1 - head*Math.sin(ang - Math.PI/6));
  ctx.lineTo(x1 - head*Math.cos(ang + Math.PI/6), y1 - head*Math.sin(ang + Math.PI/6));
  ctx.closePath();
  ctx.fill();

  // rótulo
  ctx.font = "14px Arial";
  const align = (dx >= 0) ? "left" : "right";
  ctx.textAlign = align;
  ctx.textBaseline = "bottom";
  const xText = x1 + (dx >= 0 ? 8 : -8);
  const yText = y1 - 6;
  ctx.fillText(label, xText, yText);

  // seta em cima do rótulo (vetor)
  drawVectorOverLabel(label, xText, yText, align, color);

  ctx.restore();
}}

function drawDashedComponents(x0, y0, dx, dy, color) {{
  // tracejado das componentes sem rótulos
  ctx.save();
  ctx.setLineDash([6, 5]);
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;

  // componente x
  ctx.beginPath();
  ctx.moveTo(x0, y0);
  ctx.lineTo(x0 + dx, y0);
  ctx.stroke();

  // componente y
  ctx.beginPath();
  ctx.moveTo(x0 + dx, y0);
  ctx.lineTo(x0 + dx, y0 + dy);
  ctx.stroke();

  ctx.setLineDash([]);
  ctx.restore();
}}

// ============================
// Limitar vetor para caber no retângulo útil (pedido 7)
// Sem alterar escala dos eixos: "corta" o comprimento se necessário.
// ============================
function maxLenToFit(x0, y0, ux, uy) {{
  // retângulo útil
  const xmin = padL, xmax = W - padR;
  const ymin = padT, ymax = H - padB;

  // evita divisão por zero
  const eps = 1e-9;

  let tMax = Infinity;

  // interseção com x = xmin / xmax
  if (Math.abs(ux) > eps) {{
    const tx1 = (xmin - x0) / ux;
    const tx2 = (xmax - x0) / ux;
    const tx = Math.max(Math.min(tx1, tx2), 0); // primeiro t >= 0 que pega borda mais próxima no sentido
    // mas precisamos do menor t positivo que atinge qualquer borda, então:
    const candidates = [tx1, tx2].filter(t => t > 0);
    if (candidates.length) tMax = Math.min(tMax, Math.min(...candidates));
  }}

  // interseção com y = ymin / ymax
  if (Math.abs(uy) > eps) {{
    const ty1 = (ymin - y0) / uy;
    const ty2 = (ymax - y0) / uy;
    const candidates = [ty1, ty2].filter(t => t > 0);
    if (candidates.length) tMax = Math.min(tMax, Math.min(...candidates));
  }}

  // tMax é a distância paramétrica até sair; aplicamos folga
  if (!isFinite(tMax)) return 0;
  return 0.92 * tMax; // folga para não colar na borda
}}

drawAxes();

const P1 = drawParticle({x1}, {y1}, 1, "{col_p1}");
const P2 = drawParticle({x2}, {y2}, 2, "{col_p2}");
const P3 = drawParticle({x3}, {y3}, 3, "{col_p3}");

// escala base por módulo relativo
const maxF = {maxF};
function vecPixFit(Fx, Fy, maxLen=150) {{
  const mag = Math.hypot(Fx, Fy);
  if (mag === 0) return {{dx:0, dy:0}};

  const Lwanted = maxLen * (mag / maxF);

  // unitário no canvas (y invertido)
  const ux = (Fx / mag);
  const uy = (-Fy / mag);

  const Lfit = maxLenToFit(P3.px, P3.py, ux, uy);
  const L = Math.min(Lwanted, Lfit);

  return {{dx: ux*L, dy: uy*L}};
}}

const v13 = vecPixFit({Fx13}, {Fy13}, 160);
const v23 = vecPixFit({Fx23}, {Fy23}, 160);
const vr  = vecPixFit({Fxr},  {Fyr},  180);

drawArrowPix(P3.px, P3.py, v13.dx, v13.dy, "#d62728", "F₁₃");
drawDashedComponents(P3.px, P3.py, v13.dx, v13.dy, "#d62728");

drawArrowPix(P3.px, P3.py, v23.dx, v23.dy, "#1f77b4", "F₂₃");
drawDashedComponents(P3.px, P3.py, v23.dx, v23.dy, "#1f77b4");

drawArrowPix(P3.px, P3.py, vr.dx,  vr.dy,  "#2ca02c", "Fᵣ");
drawDashedComponents(P3.px, P3.py, vr.dx,  vr.dy,  "#2ca02c");
</script>
"""
components.html(html, height=650)

# ===================== Distâncias (sem fórmulas) =====================
st.header("Distâncias")

d1, d2 = st.columns(2)
with d1:
    st.latex(rf"r_{{13}} = {latex_sci(r13, 2, r'\mathrm{{m}}')}")
with d2:
    st.latex(rf"r_{{23}} = {latex_sci(r23, 2, r'\mathrm{{m}}')}")

# ===================== Forças Eletrostáticas (2D) =====================
st.header("Forças Eletrostáticas (2D)")

st.latex(r"F_{13}=K\frac{|q_1q_3|}{r_{13}^2}")
st.latex(r"F_{23}=K\frac{|q_2q_3|}{r_{23}^2}")

# K corrigido (não aparece como texto cru)
st.latex(r"K = 9{,}0\times10^9\ \mathrm{N\cdot m^2/C^2}")

st.markdown(
    "onde **q** são as cargas das partículas, **r** são as distâncias entre elas e **K** é a constante de Coulomb."
)

# Substituição numérica
st.subheader("Substituição numérica")

# valores das cargas (em C) a partir dos sliders (µC)
q1_ltx = latex_charge_C_from_uC(q1_uC)
q2_ltx = latex_charge_C_from_uC(q2_uC)
q3_ltx = latex_charge_C_from_uC(q3_uC)

r13_ltx = latex_sci_no_unit(r13, 2)
r23_ltx = latex_sci_no_unit(r23, 2)

st.latex(
    rf"F_{{13}} = (9{{,}}0\times10^9)\cdot\frac{{\left|({q1_ltx})({q3_ltx})\right|}}{{({r13_ltx})^2}}"
)
st.latex(rf"F_{{13}} = {latex_sci(abs(F13_d), 2, r'\mathrm{{N}}')}")

st.latex(
    rf"F_{{23}} = (9{{,}}0\times10^9)\cdot\frac{{\left|({q2_ltx})({q3_ltx})\right|}}{{({r23_ltx})^2}}"
)
st.latex(rf"F_{{23}} = {latex_sci(abs(F23_d), 2, r'\mathrm{{N}}')}")

# ===================== Resultados =====================
st.header("Resultados (módulo, componentes e direção)")

def results_block(title, color, Fmag, Fx, Fy, theta, label_main):
    # strings latex
    mag_s = latex_sci(sig(Fmag, 2), 2, r"\mathrm{N}")
    fx_s  = latex_sci(sig(Fx,   2), 2, r"\mathrm{N}")
    fy_s  = latex_sci(sig(Fy,   2), 2, r"\mathrm{N}")
    th_s  = f"{theta:.1f}".replace(".", "{,}")

    st.markdown(
        f"""
        <div style="background:#ffffff;border:1px solid #eee;border-radius:14px;
                    padding:14px 16px; box-shadow:0 1px 8px rgba(0,0,0,0.06);">
          <div style="font-size:14px;color:#333;margin-bottom:10px;">
            <b style="color:{color};">●</b> <b>{title}</b>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # módulo
    st.latex(rf"{label_main} = {mag_s}")

    # componentes com setas ao lado (pedido 1)
    # (usa math inline + unicode setas)
    st.markdown(
        rf"$ {label_main}x = {fx_s}\ $ **{arrow_x(sig(Fx,2))}**"
        rf"&nbsp;&nbsp;&nbsp;&nbsp;"
        rf"$ {label_main}y = {fy_s}\ $ **{arrow_y(sig(Fy,2))}**",
        unsafe_allow_html=True
    )

    st.latex(rf"\theta = {th_s}^\circ")

colA, colB, colC = st.columns(3)
with colA:
    results_block("Força na partícula 3 devido à partícula 1", "#d62728",
                  abs(F13), Fx13, Fy13, th13, r"F_{13}")
with colB:
    results_block("Força na partícula 3 devido à partícula 2", "#1f77b4",
                  abs(F23), Fx23, Fy23, th23, r"F_{23
