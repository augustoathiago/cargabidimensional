import streamlit as st
import streamlit.components.v1 as components
import math

# =========================================================
# Config
# =========================================================
st.set_page_config(page_title="Simulador Força Eletrostática 2D", layout="wide")
K = 9.0e9

# =========================================================
# Helpers
# =========================================================
_sup_map = str.maketrans("0123456789-+", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺")

def sig(x, n=2):
    """n algarismos significativos (float)"""
    if x == 0 or math.isclose(x, 0.0, abs_tol=0.0):
        return 0.0
    return float(f"{x:.{n}g}")

def br_decimal(s: str) -> str:
    return s.replace(".", ",")

def sci_parts(x, n=2):
    if x == 0:
        return 0.0, 0
    exp = int(math.floor(math.log10(abs(x))))
    mant = x / (10 ** exp)
    mant = float(f"{mant:.{n}g}")
    if abs(mant) >= 10:
        mant /= 10
        exp += 1
    return mant, exp

def br_sci(x, n=2, unit=""):
    if x == 0:
        out = "0"
    else:
        mant, exp = sci_parts(x, n=n)
        mant_s = br_decimal(f"{mant:.{n}g}")
        out = f"{mant_s}×10{str(exp).translate(_sup_map)}"
    return f"{out} {unit}".strip()

def fmt_uC_br(q_uC: float) -> str:
    return f"{round(q_uC, 2):.2f}".replace(".", ",")

def fmt_pos_br(x: float) -> str:
    return f"{round(x, 1):.1f}".replace(".", ",")

def latex_charge_C_from_uC(q_uC: float) -> str:
    """Exibe exatamente o valor do slider (2 casas) como mantissa × 10^{-6}"""
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
    theta = math.degrees(math.atan2(Fy, Fx))
    return Fx, Fy, F, theta, r

def triangle_svg(Fx, Fy, label="F", color="#d62728"):
    """
    Desenha triângulo retângulo (SVG) com vetor inclinado, componentes e ângulo.
    Escala automática só para visual (não é escala física).
    """
    # evita zero
    mag = math.hypot(Fx, Fy)
    if mag == 0:
        Fx_n, Fy_n = 60, 0
        ang = 0.0
    else:
        # normaliza para caber
        scale = 80.0 / max(abs(Fx), abs(Fy), 1e-30)
        Fx_n = Fx * scale
        Fy_n = Fy * scale
        ang = math.degrees(math.atan2(Fy, Fx))

    # sistema SVG: y cresce para baixo, então invertendo Fy
    x0, y0 = 20, 110
    x1 = x0 + Fx_n
    y1 = y0 - Fy_n  # inverte

    # projeções
    xp, yp = x1, y0

    # ângulo (pequeno arco)
    arc_r = 18
    # desenhar arco próximo da origem
    # simples: arco fixo (visual), e texto do ângulo
    ang_txt = f"{ang:.1f}".replace(".", ",") + "°"

    # valores
    Fx_txt = br_sci(Fx, 2, "N")
    Fy_txt = br_sci(Fy, 2, "N")
    F_txt  = br_sci(mag, 2, "N")

    # labels com subscritos via <tspan baseline-shift>
    # para simplificar: usar texto normal "F13x" etc no SVG e subscrito no Streamlit com LaTeX
    svg = f"""
    <div style="background:#fff;border:1px solid #eee;border-radius:12px;padding:10px;">
      <div style="font-size:13px;color:#333;margin-bottom:6px;"><b>Triângulo das componentes</b></div>
      <svg width="260" height="140" viewBox="0 0 260 140">
        <rect x="0" y="0" width="260" height="140" fill="white"/>
        <!-- eixos locais -->
        <line x1="{x0}" y1="{y0}" x2="{x0+190}" y2="{y0}" stroke="#888" stroke-width="1"/>
        <line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0-90}" stroke="#888" stroke-width="1"/>

        <!-- componente x -->
        <line x1="{x0}" y1="{y0}" x2="{xp}" y2="{yp}" stroke="#555" stroke-width="2" stroke-dasharray="6 5"/>
        <!-- seta x -->
        <polygon points="{xp},{yp} {xp-8},{yp-4} {xp-8},{yp+4}" fill="#555"/>

        <!-- componente y -->
        <line x1="{xp}" y1="{yp}" x2="{x1}" y2="{y1}" stroke="#555" stroke-width="2" stroke-dasharray="6 5"/>
        <!-- seta y -->
        <polygon points="{x1},{y1} {x1-4},{y1+8} {x1+4},{y1+8}" fill="#555"/>

        <!-- vetor resultante -->
        <line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{color}" stroke-width="3"/>
        <polygon points="{x1},{y1} {x1-10},{y1+4} {x1-6},{y1+10}" fill="{color}"/>

        <!-- ângulo (texto) -->
        <text x="{x0+26}" y="{y0-10}" font-size="12" fill="#111">θ = {ang_txt}</text>

        <!-- rótulos -->
        <text x="{(x0+xp)/2}" y="{y0+18}" font-size="12" fill="#111">{label}x</text>
        <text x="{xp+10}" y="{(yp+y1)/2}" font-size="12" fill="#111">{label}y</text>
        <text x="{x1+8}" y="{y1-6}" font-size="12" fill="{color}">{label}</text>
      </svg>

      <div style="font-size:13px;color:#111;margin-top:6px;line-height:1.35">
        <div><b>{label}</b> = {F_txt}</div>
        <div><b>{label}x</b> = {Fx_txt} &nbsp;&nbsp; {arrow_x(Fx)}</div>
        <div><b>{label}y</b> = {Fy_txt} &nbsp;&nbsp; {arrow_y(Fy)}</div>
      </div>
    </div>
    """
    return svg

# =========================================================
# Cabeçalho
# =========================================================
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
        "próxima a outras duas partículas carregadas **1** e **2**."
    )
    st.markdown("**Desafio:** tente encontrar uma situação onde a partícula 3 está em equilíbrio (\\(\\vec F_r \\approx 0\\)).")

# =========================================================
# Controles
# =========================================================
st.header("Definições das Partículas (x, y e carga)")

qmin_uC, qmax_uC, qstep_uC = -5.0, 5.0, 0.05
xmin_slider, xmax_slider = -10.0, 10.0
ymin_slider, ymax_slider = -10.0, 10.0

c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("Partícula 1")
    x1 = st.slider("x₁ (m)", xmin_slider, xmax_slider, -4.0, 0.1, format="%.1f")
    y1 = st.slider("y₁ (m)", ymin_slider, ymax_slider, 0.0, 0.1, format="%.1f")
    q1_uC = st.slider("q₁ (µC)", qmin_uC, qmax_uC, 2.0, qstep_uC, format="%.2f")
    q1 = q1_uC * 1e-6

with c2:
    st.subheader("Partícula 2")
    x2 = st.slider("x₂ (m)", xmin_slider, xmax_slider, 4.0, 0.1, format="%.1f")
    y2 = st.slider("y₂ (m)", ymin_slider, ymax_slider, 0.0, 0.1, format="%.1f")
    q2_uC = st.slider("q₂ (µC)", qmin_uC, qmax_uC, -2.0, qstep_uC, format="%.2f")
    q2 = q2_uC * 1e-6

with c3:
    st.subheader("Partícula 3")
    x3 = st.slider("x₃ (m)", xmin_slider, xmax_slider, 0.0, 0.1, format="%.1f")
    y3 = st.slider("y₃ (m)", ymin_slider, ymax_slider, 2.0, 0.1, format="%.1f")
    q3_uC = st.slider("q₃ (µC)", qmin_uC, qmax_uC, 1.0, qstep_uC, format="%.2f")
    q3 = q3_uC * 1e-6

# =========================================================
# Restrições: posições iguais (2D)
# =========================================================
p1 = (round(x1, 1), round(y1, 1))
p2 = (round(x2, 1), round(y2, 1))
p3 = (round(x3, 1), round(y3, 1))

if len({p1, p2, p3}) < 3:
    st.error("❌ As partículas **não podem** estar na mesma posição (x, y). Ajuste os sliders.")
    st.stop()

# =========================================================
# Física
# =========================================================
Fx13, Fy13, F13, th13, r13 = coulomb_force_2d(q3, q1, x3, y3, x1, y1, K=K)
Fx23, Fy23, F23, th23, r23 = coulomb_force_2d(q3, q2, x3, y3, x2, y2, K=K)

Fxr = Fx13 + Fx23
Fyr = Fy13 + Fy23
Fr  = math.hypot(Fxr, Fyr)
thr = math.degrees(math.atan2(Fyr, Fxr)) if Fr != 0 else 0.0

# versões "didáticas" (2 AS) para exibição principal
Fx13_d, Fy13_d, F13_d = sig(Fx13, 2), sig(Fy13, 2), sig(F13, 2)
Fx23_d, Fy23_d, F23_d = sig(Fx23, 2), sig(Fy23, 2), sig(F23, 2)
Fxr_d,  Fyr_d,  Fr_d  = sig(Fxr,  2), sig(Fyr,  2), sig(Fr,  2)

equilibrio = (Fr_d == 0.0)

# =========================================================
# Figura (Canvas)
# =========================================================
st.header("Figura – Sistema Bidimensional (fundo branco)")

# escala de setas (pixel) com base no maior módulo
maxF = max(abs(F13), abs(F23), abs(Fr), 1e-30)

# cor borda partícula 3 pela carga
def color_charge(q):
    eps = 1e-15
    if q > eps:  return "#d62728"  # vermelho
    if q < -eps: return "#1f77b4"  # azul
    return "#111"

col_p1 = color_charge(q1)
col_p2 = color_charge(q2)
col_p3 = color_charge(q3)  # requisito 7

# plano exibido
xMin, xMax = -10, 10
yMin, yMax = -10, 10
ticks = list(range(-10, 11, 2))

html = f"""
<div style="background:white;padding:6px;border-radius:14px;border:1px solid #eee;">
  <canvas id="canvas2d" width="920" height="620"
    style="background: white; border: 1px solid #e9e9e9; display:block; border-radius:12px;"></canvas>
</div>

<script>
const canvas = document.getElementById("canvas2d");
const ctx = canvas.getContext("2d");
const W = canvas.width, H = canvas.height;

// fundo branco (garantido)
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

// =====================================================
// Eixos e ticks
// =====================================================
function drawAxes() {{
  // grade leve
  ctx.strokeStyle = "#f0f0f0";
  ctx.lineWidth = 1;
  for (let t of {ticks}) {{
    // verticais
    ctx.beginPath();
    ctx.moveTo(X(t), Y(yMin));
    ctx.lineTo(X(t), Y(yMax));
    ctx.stroke();
    // horizontais
    ctx.beginPath();
    ctx.moveTo(X(xMin), Y(t));
    ctx.lineTo(X(xMax), Y(t));
    ctx.stroke();
  }}

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
  ctx.fillStyle = "#111";
  ctx.font = "13px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "top";

  for (let t of {ticks}) {{
    // x ticks
    ctx.beginPath();
    ctx.moveTo(X(t), Y(0)-6);
    ctx.lineTo(X(t), Y(0)+6);
    ctx.stroke();
    ctx.fillText(String(t).replace(".", ","), X(t), Y(0)+10);
  }}

  ctx.textAlign = "right";
  ctx.textBaseline = "middle";
  for (let t of {ticks}) {{
    // y ticks
    ctx.beginPath();
    ctx.moveTo(X(0)-6, Y(t));
    ctx.lineTo(X(0)+6, Y(t));
    ctx.stroke();
    if (t !== 0) ctx.fillText(String(t).replace(".", ","), X(0)-10, Y(t));
  }}

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
  ctx.textAlign = "left";
  ctx.textBaseline = "bottom";
  ctx.fillText(label, x1 + 6, y1 - 6);

  ctx.restore();
  return {{x1, y1}};
}}

function drawDashedComponents(x0, y0, dx, dy, color, labx, laby) {{
  ctx.save();
  ctx.setLineDash([6, 5]);
  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.lineWidth = 2;

  // componente x (horizontal)
  ctx.beginPath();
  ctx.moveTo(x0, y0);
  ctx.lineTo(x0 + dx, y0);
  ctx.stroke();
  // cabeça x
  const sx = dx >= 0 ? 1 : -1;
  ctx.beginPath();
  ctx.moveTo(x0 + dx, y0);
  ctx.lineTo(x0 + dx - sx*8, y0 - 4);
  ctx.lineTo(x0 + dx - sx*8, y0 + 4);
  ctx.closePath();
  ctx.fill();

  // componente y (vertical a partir do fim de x)
  ctx.beginPath();
  ctx.moveTo(x0 + dx, y0);
  ctx.lineTo(x0 + dx, y0 + dy);
  ctx.stroke();
  // cabeça y
  const sy = dy <= 0 ? 1 : -1; // canvas y cresce p/ baixo
  ctx.beginPath();
  ctx.moveTo(x0 + dx, y0 + dy);
  ctx.lineTo(x0 + dx - 4, y0 + dy + sy*8);
  ctx.lineTo(x0 + dx + 4, y0 + dy + sy*8);
  ctx.closePath();
  ctx.fill();

  // labels
  ctx.setLineDash([]);
  ctx.font = "12px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  ctx.fillText(labx, x0 + dx/2, y0 + 6);
  ctx.textAlign = "left";
  ctx.textBaseline = "middle";
  ctx.fillText(laby, x0 + dx + 6, y0 + dy/2);

  ctx.restore();
}}

drawAxes();

// partículas
const P1 = drawParticle({x1}, {y1}, 1, "{col_p1}");
const P2 = drawParticle({x2}, {y2}, 2, "{col_p2}");
const P3 = drawParticle({x3}, {y3}, 3, "{col_p3}"); // requisito 7

// =====================================================
// Vetores de força (desenhados em pixels com escala)
// =====================================================
const maxF = {maxF};
function vecPix(Fx, Fy, maxLen=120) {{
  const mag = Math.hypot(Fx, Fy);
  if (mag === 0) return {{dx:0, dy:0}};
  const L = maxLen * (mag / maxF);
  const ux = Fx / mag;
  const uy = Fy / mag;
  // canvas: y invertido -> dy = -uy*L
  return {{dx: ux*L, dy: -uy*L}};
}}

const v13 = vecPix({Fx13}, {Fy13}, 130);
const v23 = vecPix({Fx23}, {Fy23}, 130);
const vr  = vecPix({Fxr},  {Fyr},  150);

// F13
drawArrowPix(P3.px, P3.py, v13.dx, v13.dy, "#d62728", "F\u2081\u2083");
drawDashedComponents(P3.px, P3.py, v13.dx, v13.dy, "#d62728", "F\u2081\u2083x", "F\u2081\u2083y");

// F23
drawArrowPix(P3.px, P3.py, v23.dx, v23.dy, "#1f77b4", "F\u2082\u2083");
drawDashedComponents(P3.px, P3.py, v23.dx, v23.dy, "#1f77b4", "F\u2082\u2083x", "F\u2082\u2083y");

// Fr
drawArrowPix(P3.px, P3.py, vr.dx, vr.dy, "#2ca02c", "F\u1D63"); // Fᵣ
drawDashedComponents(P3.px, P3.py, vr.dx, vr.dy, "#2ca02c", "F\u1D63x", "F\u1D63y");
</script>
"""
components.html(html, height=650)

# =========================================================
# Seção Teoria / Equações
# =========================================================
st.header("Forças Eletrostáticas (2D)")

st.latex(r"\vec{F}_{ij} = K\,q_i q_j\,\frac{\vec{r}_i-\vec{r}_j}{\left|\vec{r}_i-\vec{r}_j\right|^3}")
st.latex(r"r_{ij}=\sqrt{(x_i-x_j)^2+(y_i-y_j)^2}")
st.latex(r"F_{ijx}=K\,q_i q_j\frac{(x_i-x_j)}{r_{ij}^3}\quad;\quad F_{ijy}=K\,q_i q_j\frac{(y_i-y_j)}{r_{ij}^3}")
st.latex(r"\theta_{ij}=\arctan\!\left(\frac{F_{ijy}}{F_{ijx}}\right)\quad(\text{usando }\mathrm{atan2})")

st.subheader("Equações de \u2192  \(\\vec{F}_{13}\) e \(\\vec{F}_{23}\) (substituição)")
st.latex(
    rf"\vec{{F}}_{{13}}=K\,(q_3)(q_1)\,\frac{{(x_3-x_1)\hat{{i}}+(y_3-y_1)\hat{{j}}}}{{r_{{13}}^3}}"
)
st.latex(
    rf"r_{{13}}=\sqrt{{({fmt_pos_br(x3)}-{fmt_pos_br(x1)})^2+({fmt_pos_br(y3)}-{fmt_pos_br(y1)})^2}}"
)

st.latex(
    rf"\vec{{F}}_{{23}}=K\,(q_3)(q_2)\,\frac{{(x_3-x_2)\hat{{i}}+(y_3-y_2)\hat{{j}}}}{{r_{{23}}^3}}"
)
st.latex(
    rf"r_{{23}}=\sqrt{{({fmt_pos_br(x3)}-{fmt_pos_br(x2)})^2+({fmt_pos_br(y3)}-{fmt_pos_br(y2)})^2}}"
)

# =========================================================
# Cards de resultados (com setas para componentes)
# =========================================================
st.header("Resultados (módulo, componentes e direção)")

def card_force(title, color, Fx, Fy, F, theta, label_main="F_{13}"):
    Fx_d, Fy_d, F_d = sig(Fx, 2), sig(Fy, 2), sig(F, 2)
    theta_s = f"{theta:.1f}".replace(".", ",")
    st.markdown(
        f"""
        <div style="
            border-left: 8px solid {color};
            background: #ffffff;
            padding: 14px 16px;
            border-radius: 14px;
            box-shadow: 0 1px 8px rgba(0,0,0,0.06);
            margin-bottom: 10px;">
          <div style="font-size: 14px; color: #333; margin-bottom: 10px;"><b>{title}</b></div>

          <div style="font-size: 18px; color:#111; line-height:1.45;">
            <div><b>|F|</b> = {br_sci(F_d,2,"N")}</div>
            <div><b>Fx</b> = {br_sci(Fx_d,2,"N")} <span style="font-size:18px;">{arrow_x(Fx_d)}</span></div>
            <div><b>Fy</b> = {br_sci(Fy_d,2,"N")} <span style="font-size:18px;">{arrow_y(Fy_d)}</span></div>
            <div><b>θ</b> = {theta_s}°</div>
          </div>

          <div style="font-size: 12px; color: #555; margin-top: 10px;">
            Resultados exibidos com <b>2 algarismos significativos</b>.
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    # LaTeX bonito (evita /text /theta etc)
    st.latex(rf"{label_main} = {br_sci(F_d,2,'N')}")
    st.latex(rf"{label_main}x = {br_sci(Fx_d,2,'N')}\quad,\quad {label_main}y = {br_sci(Fy_d,2,'N')}")
    st.latex(rf"\theta = {theta:.1f}^\circ")

colA, colB, colC = st.columns(3)
with colA:
    card_force("Força na partícula 3 devido à partícula 1", "#d62728", Fx13, Fy13, F13, th13, label_main=r"F_{13}")
    components.html(triangle_svg(Fx13, Fy13, label="F13", color="#d62728"), height=210)

with colB:
    card_force("Força na partícula 3 devido à partícula 2", "#1f77b4", Fx23, Fy23, F23, th23, label_main=r"F_{23}")
    components.html(triangle_svg(Fx23, Fy23, label="F23", color="#1f77b4"), height=210)

with colC:
    card_force("Força Resultante na partícula 3", "#2ca02c", Fxr, Fyr, Fr, thr, label_main=r"F_{r}")
    components.html(triangle_svg(Fxr, Fyr, label="Fr", color="#2ca02c"), height=210)

# =========================================================
# Resultante e Equilíbrio
# =========================================================
st.subheader("Soma vetorial")
st.latex(r"\vec{F}_r = \vec{F}_{13} + \vec{F}_{23}")
st.latex(rf"F_{{rx}}=F_{{13x}}+F_{{23x}}\quad;\quad F_{{ry}}=F_{{13y}}+F_{{23y}}")

if equilibrio:
    st.success("✅ A partícula 3 está em **equilíbrio** (com 2 algarismos significativos, \\(\\vec F_r \\approx 0\\)).")
else:
    st.info("ℹ️ Ajuste posições e cargas para buscar \\(\\vec F_r \\approx 0\\).")
