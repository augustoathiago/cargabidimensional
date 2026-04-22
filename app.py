import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Simulador Força Eletrostática 2D", layout="wide")

# ===================== CSS (melhor uso no mobile) =====================
st.markdown(
    """
    <style>
      /* Ajusta margens/padding em telas menores */
      @media (max-width: 768px){
        .block-container { padding-left: 0.8rem; padding-right: 0.8rem; }
      }
    </style>
    """,
    unsafe_allow_html=True
)

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

# ===================== Figura (Canvas) =====================
st.header("Figura – Sistema Bidimensional")
st.caption("📱 No celular: deslize para o lado (horizontal) para ver toda a figura.")

xMin, xMax = -15, 15
yMin, yMax = -15, 15
ticks = list(range(-14, 15, 2))

col_p1 = color_charge(q1)
col_p2 = color_charge(q2)
col_p3 = color_charge(q3)

# Tamanho lógico do canvas (em CSS px). Mantemos grande para leitura e habilitamos scroll.
CANVAS_CSS_W = 920
CANVAS_CSS_H = 620

html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<style>
  html, body {{
    margin: 0; padding: 0;
    background: transparent;
    font-family: Arial, sans-serif;
  }}

  /* Contêiner com rolagem horizontal (swipe no mobile) */
  .frame {{
    background: white;
    padding: 6px;
    border-radius: 14px;
    border: 1px solid #eee;
  }}

  .scroll-x {{
    width: 100%;
    overflow-x: auto;
    overflow-y: hidden;
    -webkit-overflow-scrolling: touch;
    touch-action: pan-x;
    border-radius: 12px;
  }}

  /* Dica visual sutil de que existe scroll lateral */
  .hint {{
    position: relative;
  }}
  .hint:after {{
    content: "";
    pointer-events: none;
    position: absolute;
    top: 0; right: 0;
    width: 26px; height: 100%;
    background: linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,0.95));
  }}

  canvas {{
    background: white;
    border: 1px solid #e9e9e9;
    display: block;
    border-radius: 12px;

    /* Importante: não deixar o canvas "encolher" */
    max-width: none;
  }}
</style>
</head>

<body>
  <div class="frame">
    <div class="scroll-x hint">
      <canvas id="canvas2d"></canvas>
    </div>
  </div>

<script>
  const canvas = document.getElementById("canvas2d");
  const ctx = canvas.getContext("2d");

  // =====================================================
  // ✅ NITIDEZ EM TELAS RETINA (celulares)
  // - define tamanho "CSS" e multiplica pelo devicePixelRatio
  // - mantém coordenadas e cálculos em pixels "CSS"
  // =====================================================
  const cssW = {CANVAS_CSS_W};
  const cssH = {CANVAS_CSS_H};
  const dpr = window.devicePixelRatio || 1;

  canvas.style.width = cssW + "px";
  canvas.style.height = cssH + "px";
  canvas.width = Math.floor(cssW * dpr);
  canvas.height = Math.floor(cssH * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0); // escala o desenho para ficar nítido

  const W = cssW, H = cssH;

  ctx.fillStyle = "white";
  ctx.fillRect(0,0,W,H);

  const xMin = {xMin}, xMax = {xMax}, yMin = {yMin}, yMax = {yMax};
  const padL = 60, padR = 30, padT = 25, padB = 55;

  // =====================================================
  // ✅ ESCALA ISOMÉTRICA (ticks iguais em X e Y)
  // =====================================================
  const plotW = (W - padL - padR);
  const plotH = (H - padT - padB);
  const rangeX = (xMax - xMin);
  const rangeY = (yMax - yMin);

  const scaleX = plotW / rangeX;
  const scaleY = plotH / rangeY;
  const scale  = Math.min(scaleX, scaleY);

  const extraX = plotW - scale * rangeX;
  const extraY = plotH - scale * rangeY;

  function X(x) {{
    return padL + extraX/2 + (x - xMin) * scale;
  }}
  function Y(y) {{
    return padT + extraY/2 + (yMax - y) * scale;
  }}

  // ---------------- Grade cinza claro ----------------
  function drawGrid() {{
    const ticks = {ticks};
    ctx.save();
    ctx.strokeStyle = "#eeeeee";
    ctx.lineWidth = 1;

    ticks.forEach(t => {{
      ctx.beginPath();
      ctx.moveTo(X(t), Y(yMin));
      ctx.lineTo(X(t), Y(yMax));
      ctx.stroke();

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

    ctx.strokeStyle = "#111";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(X(xMin), Y(0)); ctx.lineTo(X(xMax), Y(0));
    ctx.moveTo(X(0), Y(yMin)); ctx.lineTo(X(0), Y(yMax));
    ctx.stroke();

    const ticks = {ticks};
    ctx.fillStyle = "#111";
    ctx.font = "12px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "top";

    ticks.forEach(t => {{
      ctx.beginPath(); ctx.moveTo(X(t), Y(0)-6); ctx.lineTo(X(t), Y(0)+6); ctx.stroke();
      ctx.fillText(String(t), X(t), Y(0)+10);
    }});

    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    ticks.forEach(t => {{
      ctx.beginPath(); ctx.moveTo(X(0)-6, Y(t)); ctx.lineTo(X(0)+6, Y(t)); ctx.stroke();
      if (t !== 0) ctx.fillText(String(t), X(0)-10, Y(t));
    }});

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
    ctx.beginPath(); ctx.arc(px, py, 16, 0, 2*Math.PI); ctx.fill(); ctx.stroke();
    ctx.fillStyle = "#111";
    ctx.font = "bold 16px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(String(n), px, py);
    return {{px, py}};
  }}

  function drawVectorOverLabel(text, xAnchor, yBaseline, align, color) {{
    ctx.save();
    ctx.font = "14px Arial";
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = 2;
    const w = ctx.measureText(text).width;
    let xLeft = xAnchor;
    if (align === "right") xLeft = xAnchor - w;
    const yArrow = yBaseline - 16;

    ctx.beginPath(); ctx.moveTo(xLeft, yArrow); ctx.lineTo(xLeft + w, yArrow); ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(xLeft + w, yArrow);
    ctx.lineTo(xLeft + w - 6, yArrow - 4);
    ctx.lineTo(xLeft + w - 6, yArrow + 4);
    ctx.closePath(); ctx.fill();
    ctx.restore();
  }}

  function drawArrowPix(x0, y0, dx, dy, color, label) {{
    ctx.save();
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = 3;

    const x1 = x0 + dx, y1 = y0 + dy;
    ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();

    const ang = Math.atan2(dy, dx);
    const head = 10;
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x1 - head*Math.cos(ang - Math.PI/6), y1 - head*Math.sin(ang - Math.PI/6));
    ctx.lineTo(x1 - head*Math.cos(ang + Math.PI/6), y1 - head*Math.sin(ang + Math.PI/6));
    ctx.closePath(); ctx.fill();

    ctx.font = "14px Arial";
    const align = (dx >= 0) ? "left" : "right";
    ctx.textAlign = align;
    ctx.textBaseline = "bottom";
    const xText = x1 + (dx >= 0 ? 8 : -8);
    const yText = y1 - 6;
    ctx.fillText(label, xText, yText);
    drawVectorOverLabel(label, xText, yText, align, color);

    ctx.restore();
  }}

  function drawDashedComponents(x0, y0, dx, dy, color) {{
    ctx.save();
    ctx.setLineDash([6, 5]);
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;

    ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x0 + dx, y0); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x0 + dx, y0); ctx.lineTo(x0 + dx, y0 + dy); ctx.stroke();

    ctx.setLineDash([]);
    ctx.restore();
  }}

  // --------- limitador geométrico: garante que o vetor cabe ----------
  function maxLenToFit(x0, y0, ux, uy) {{
    const xmin = padL, xmax = W - padR;
    const ymin = padT, ymax = H - padB;
    const eps = 1e-9;
    let tMax = Infinity;

    if (Math.abs(ux) > eps) {{
      const tx1 = (xmin - x0) / ux;
      const tx2 = (xmax - x0) / ux;
      const candidates = [tx1, tx2].filter(t => t > 0);
      if (candidates.length) tMax = Math.min(tMax, Math.min(...candidates));
    }}
    if (Math.abs(uy) > eps) {{
      const ty1 = (ymin - y0) / uy;
      const ty2 = (ymax - y0) / uy;
      const candidates = [ty1, ty2].filter(t => t > 0);
      if (candidates.length) tMax = Math.min(tMax, Math.min(...candidates));
    }}
    if (!isFinite(tMax)) return 0;
    return 0.92 * tMax;
  }}

  drawAxes();
  const P1 = drawParticle({x1}, {y1}, 1, "{col_p1}");
  const P2 = drawParticle({x2}, {y2}, 2, "{col_p2}");
  const P3 = drawParticle({x3}, {y3}, 3, "{col_p3}");

  // =====================================================
  // ✅ ESCALA DOS VETORES (CORRETA): mesma escala linear para Fx/Fy
  // =====================================================
  const Fx13 = {Fx13}, Fy13 = {Fy13};
  const Fx23 = {Fx23}, Fy23 = {Fy23};
  const Fxr  = {Fxr},  Fyr  = {Fyr};

  const Fref = Math.max(
    Math.abs(Fx13), Math.abs(Fy13),
    Math.abs(Fx23), Math.abs(Fy23),
    Math.abs(Fxr),  Math.abs(Fyr),
    1e-30
  );

  const Lworld_max = 4.0;            // m
  const LmaxPx = scale * Lworld_max; // px
  const S = LmaxPx / Fref;           // N -> px

  function vecFromForce(Fx, Fy) {{
    let dx = S * Fx;
    let dy = -S * Fy; // y invertido no canvas

    const mag = Math.hypot(dx, dy);
    if (mag === 0) return {{dx:0, dy:0}};

    const ux = dx / mag;
    const uy = dy / mag;

    const Lfit = maxLenToFit(P3.px, P3.py, ux, uy);
    if (mag > Lfit && Lfit > 0) {{
      const k = Lfit / mag;
      dx *= k;
      dy *= k;
    }}
    return {{dx, dy}};
  }}

  const v13 = vecFromForce(Fx13, Fy13);
  const v23 = vecFromForce(Fx23, Fy23);
  const vr  = vecFromForce(Fxr,  Fyr);

  drawArrowPix(P3.px, P3.py, v13.dx, v13.dy, "#d62728", "F₁₃");
  drawDashedComponents(P3.px, P3.py, v13.dx, v13.dy, "#d62728");

  drawArrowPix(P3.px, P3.py, v23.dx, v23.dy, "#1f77b4", "F₂₃");
  drawDashedComponents(P3.px, P3.py, v23.dx, v23.dy, "#1f77b4");

  drawArrowPix(P3.px, P3.py, vr.dx,  vr.dy,  "#2ca02c", "Fᵣ");
  drawDashedComponents(P3.px, P3.py, vr.dx,  vr.dy,  "#2ca02c");
</script>
</body>
</html>
"""

# height do iframe: um pouco maior que o canvas + bordas
components.html(html, height=700)

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
