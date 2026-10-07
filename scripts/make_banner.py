import base64
import io
import random
import xml.sax.saxutils as sx

from PIL import Image, ImageFont

SRC = r"C:\Users\kevin\Pictures\Screenshots\屏幕截图 2026-10-07 025751.png"
OUT = r"f:\schoolCompWorks\clone\gtihubMainPagePro\assets\banner-stage-v3.svg"

W, H = 1200, 675

# ---------- 1) 底图压缩 ----------
img = Image.open(SRC).convert("RGB")
img = img.resize((W, H), Image.LANCZOS)
buf = io.BytesIO()
img.save(buf, "JPEG", quality=82, optimize=True, progressive=True)
b64 = base64.b64encode(buf.getvalue()).decode("ascii")
print(f"jpeg bytes: {len(buf.getvalue())}")

# ---------- 2) 文字度量 ----------
TITLE = "🦍 Hi 你好呀，我是 Gorilla Kev 👋"
TITLE_FS = 46
LINES = ["Voice AI & TTS Builder", "Agent Skill Crafter", "Godot Game Jammer", "Turning Coffee into Code"]
LINE_FS = 26

FONT_PATHS = {
    "latin": [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"],
    "cjk": [r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simsun.ttc"],
    "emoji": [r"C:\Windows\Fonts\seguiemj.ttf"],
    "mono": [r"C:\Windows\Fonts\consolab.ttf", r"C:\Windows\Fonts\consola.ttf", r"C:\Windows\Fonts\lucon.ttf"],
}
_cache = {}


def _pick(kind: str, size: int):
    key = (kind, size)
    if key in _cache:
        return _cache[key]
    f = None
    for p in FONT_PATHS[kind]:
        try:
            f = ImageFont.truetype(p, size)
            break
        except OSError:
            continue
    _cache[key] = f
    return f


def char_w(ch: str, fs: int) -> float:
    code = ord(ch)
    if code >= 0x1F000 or (0x2600 <= code <= 0x27BF):
        f = _pick("emoji", fs)
        if f:
            return f.getlength(ch) or fs * 1.2
        return fs * 1.2
    if code > 0x2E7F:
        f = _pick("cjk", fs)
        if f:
            return f.getlength(ch) or fs
        return fs
    f = _pick("latin", fs)
    if f:
        return f.getlength(ch) or fs * 0.58
    return fs * 0.58


def mono_w(text: str, fs: int) -> float:
    f = _pick("mono", fs)
    if f:
        return f.getlength(text)
    return len(text) * fs * 0.55


# 昵称逐字定位（每个字符一个 <text>，text-anchor=middle 防止字体差异累积漂移）
centers = []
cursor_x = 0.0
for ch in TITLE:
    w = char_w(ch, TITLE_FS)
    centers.append((ch, cursor_x + w / 2))
    cursor_x += w
title_w = cursor_x

# 打字行几何
line_ws = [mono_w(t, LINE_FS) for t in LINES]
line_w_max = max(line_ws)
panel_w = max(title_w, line_w_max + 60) + 90
panel_x = (W - panel_w) / 2
panel_y, panel_h = 232, 196
title_y = panel_y + 78
line_left = panel_x + (panel_w - line_w_max) / 2
line_y = panel_y + 136
CYCLE = 9.6          # 四句轮播总时长
SEG = CYCLE / len(LINES)

# ---------- 3) 粒子 / 光斑 ----------
random.seed(20261007)

PARTICLE_COLORS = [("#8FFFE4", 0.85), ("#B9A7FF", 0.8), ("#FFFFFF", 0.75), ("#5FE8C8", 0.7)]


def particle(i: int) -> str:
    x = random.uniform(0, W)
    y = random.uniform(0, H)
    r = random.uniform(1.6, 5.2)
    color, op = random.choice(PARTICLE_COLORS)
    drift = random.uniform(45, 150)
    dur = random.uniform(9, 20)
    begin = random.uniform(0, 12)
    tw = random.uniform(2.2, 5.5)
    blur = " filter=\"url(#pblur)\"" if i % 3 == 0 else ""
    return (
        f'    <g{blur}>'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="0 0; 0 -{drift:.0f}; 0 0" dur="{dur:.1f}s" begin="-{begin:.1f}s" repeatCount="indefinite"/>'
        f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="{color}" opacity="{op}">'
        f'<animate attributeName="opacity" values="0.05;{op};0.05" dur="{tw:.1f}s" begin="-{begin:.1f}s" repeatCount="indefinite"/>'
        f'</circle></g>'
    )


particles = "\n".join(particle(i) for i in range(26))

bokeh = "\n".join(
    f'    <circle cx="{random.uniform(60, W - 60):.0f}" cy="{random.uniform(80, H - 120):.0f}" '
    f'r="{random.uniform(14, 30):.0f}" fill="{"#B9A7FF" if i % 2 else "#8FFFE4"}" opacity="0.18" filter="url(#bblur)">'
    f'<animate attributeName="opacity" values="0.06;0.3;0.06" dur="{random.uniform(5, 9):.1f}s" '
    f'begin="-{random.uniform(0, 6):.1f}s" repeatCount="indefinite"/></circle>'
    for i in range(7)
)

BEAM_COLORS = ["#B9A7FF", "#7FFFE0", "#FFC7F0", "#9AD9FF", "#C8FFB0"]
CONE_PIVOTS = [(170, -30), (430, -60), (620, -80), (840, -50), (1060, -30)]

cones = []
for i, (px, py) in enumerate(CONE_PIVOTS):
    c = BEAM_COLORS[i % len(BEAM_COLORS)]
    amp = random.uniform(9, 16)
    dur = random.uniform(10, 17)
    half_w = random.uniform(70, 130)
    begin = random.uniform(0, 9)
    cones.append(
        f'      <g transform="translate({px},{py})"><g>'
        f'<animateTransform attributeName="transform" type="rotate" '
        f'values="{-amp:.1f};{amp:.1f};{-amp:.1f}" dur="{dur:.1f}s" begin="-{begin:.1f}s" repeatCount="indefinite"/>'
        f'<path d="M0,0 L{-half_w * 0.35:.0f},40 L{-half_w:.0f},{H} L{half_w:.0f},{H} L{half_w * 0.35:.0f},40 Z" '
        f'fill="url(#cone{i % len(BEAM_COLORS)})"/>'
        f'</g></g>'
    )
cones = "\n".join(cones)

spots = []
for i in range(3):
    c = ["#8FFFE4", "#B9A7FF", "#FFD9A0"][i]
    y = [180, 300, 420][i]
    dur = [19, 24, 27][i]
    r = [260, 220, 300][i]
    begin = [0, 7, 13][i]
    direction = 1 if i % 2 == 0 else -1
    x0 = -320 if direction == 1 else W + 320
    x1 = W + 320 if direction == 1 else -320
    spots.append(
        f'      <g><animateTransform attributeName="transform" type="translate" '
        f'values="{x0} 0; {x1} 0" dur="{dur}s" begin="-{begin}s" repeatCount="indefinite"/>'
        f'<ellipse cx="0" cy="{y}" rx="{r}" ry="{r * 0.62:.0f}" fill="{c}" opacity="0.2" filter="url(#sblur)">'
        f'<animate attributeName="opacity" values="0.06;0.26;0.06" dur="{dur / 3:.1f}s" begin="-{begin}s" repeatCount="indefinite"/>'
        f'</ellipse></g>'
    )
spots = "\n".join(spots)

streaks = []
for i in range(3):
    dur = [8, 11, 14][i]
    begin = [0, 3.5, 7][i]
    h = [10, 16, 7][i]
    c = ["#FFFFFF", "#B9A7FF", "#8FFFE4"][i]
    streaks.append(
        f'      <g><animateTransform attributeName="transform" type="translate" '
        f'values="0 -60; 0 {H + 60}" dur="{dur}s" begin="-{begin}s" repeatCount="indefinite"/>'
        f'<rect x="0" y="{i * 90}" width="{W}" height="{h}" fill="{c}" opacity="0.16" filter="url(#pblur)"/></g>'
    )
streaks = "\n".join(streaks)

# ---------- 4) 昵称逐字动画 ----------
title_chars = []
for i, (ch, cx) in enumerate(centers):
    esc = sx.escape(ch)
    title_chars.append(
        f'      <text x="{cx:.1f}" y="{title_y}" text-anchor="middle" opacity="0" filter="url(#tshadow)">{esc}'
        f'<animate attributeName="opacity" values="0;1" dur="0.5s" begin="{i * 0.05:.2f}s" fill="freeze"/>'
        f'<animate attributeName="y" values="{title_y};{title_y - 5};{title_y}" dur="2.8s" begin="-{i * 0.13:.2f}s" repeatCount="indefinite"/>'
        f'</text>'
    )
title_layer = "\n".join(title_chars)

# ---------- 5) 打字机四句轮播（剪裁显字） ----------
line_groups = []
cursor_groups = []
for i, (text, lw) in enumerate(zip(LINES, line_ws)):
    s = i * SEG / CYCLE
    kt = [f"{s + 0.0005:.4f}", f"{s + 0.09:.4f}", f"{s + 0.235:.4f}", f"{s + 0.2499:.4f}"]
    if i == 0:
        kt[0] = "0.0005"
    esc = sx.escape(text)
    line_groups.append(
        f'      <g clip-path="url(#tl{i})" opacity="0">'
        f'<animate attributeName="opacity" values="0;1;1;1;0;0" '
        f'keyTimes="0;{kt[0]};{kt[1]};{kt[2]};{kt[3]};1" dur="{CYCLE}s" repeatCount="indefinite"/>'
        f'<text x="{line_left:.1f}" y="{line_y}" filter="url(#tshadow)">{esc}</text>'
        f'</g>'
    )
    cursor_groups.append(
        f'      <rect x="{line_left:.1f}" y="{line_y - 20}" width="3" height="26" fill="#8FFFE4" opacity="0">'
        f'<animate attributeName="opacity" values="0;0.9;0.9;0.9;0;0" '
        f'keyTimes="0;{kt[0]};{kt[1]};{kt[2]};{kt[3]};1" dur="{CYCLE}s" repeatCount="indefinite"/>'
        f'<animate attributeName="x" values="{line_left:.1f};{line_left:.1f};{line_left + lw:.1f};{line_left + lw:.1f};{line_left:.1f};{line_left:.1f}" '
        f'keyTimes="0;{kt[0]};{kt[1]};{kt[2]};{kt[3]};1" dur="{CYCLE}s" repeatCount="indefinite"/>'
        f'</rect>'
    )
line_layer = "\n".join(line_groups)
cursor_layer = "\n".join(cursor_groups)

clip_defs = "\n".join(
    f'    <clipPath id="tl{i}"><rect x="{line_left - 4:.1f}" y="{panel_y}" width="0" height="{panel_h}">'
    f'<animate attributeName="width" values="0;0;{lw + 8:.0f};{lw + 8:.0f};0;0" '
    f'keyTimes="0;{s + 0.0005:.4f};{s + 0.09:.4f};{s + 0.235:.4f};{s + 0.2499:.4f};1" dur="{CYCLE}s" repeatCount="indefinite"/>'
    f'</rect></clipPath>'
    for i, (s, lw) in enumerate(zip([i2 * SEG / CYCLE for i2 in range(len(LINES))], line_ws))
)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="stage banner">
  <defs>
    <clipPath id="frame"><rect x="0" y="0" width="{W}" height="{H}" rx="22"/></clipPath>
    <filter id="pblur" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="1.6"/></filter>
    <filter id="bblur" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="10"/></filter>
    <filter id="sblur" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="46"/></filter>
    <filter id="panelblur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="7"/></filter>
    <filter id="tshadow" x="-40%" y="-40%" width="180%" height="180%">
      <feDropShadow dx="0" dy="2" stdDeviation="3.2" flood-color="#04121C" flood-opacity="0.85"/>
    </filter>
    <linearGradient id="bottomFade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0B1F2A" stop-opacity="0"/>
      <stop offset="100%" stop-color="#0B1F2A" stop-opacity="0.35"/>
    </linearGradient>
    <linearGradient id="pulseGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#7FFFE0" stop-opacity="0.9"/>
      <stop offset="50%" stop-color="#B9A7FF" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#FFC7F0" stop-opacity="0.9"/>
    </linearGradient>
    <linearGradient id="titleGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#FFE7A3"/>
      <stop offset="45%" stop-color="#FFB3C7"/>
      <stop offset="100%" stop-color="#B9A7FF"/>
    </linearGradient>
{clip_defs}
{"".join(chr(10) + "    " + f'<linearGradient id="cone{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{c}" stop-opacity="0.45"/><stop offset="45%" stop-color="{c}" stop-opacity="0.16"/><stop offset="100%" stop-color="{c}" stop-opacity="0"/></linearGradient>' for i, c in enumerate(BEAM_COLORS))}
  </defs>

  <g clip-path="url(#frame)">
    <image href="data:image/jpeg;base64,{b64}" x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"/>

    <g style="mix-blend-mode:screen">
{spots}
    </g>

    <g style="mix-blend-mode:screen">
{cones}
    </g>

    <g style="mix-blend-mode:screen">
{streaks}
    </g>

    <rect x="0" y="0" width="{W}" height="{H}" fill="url(#pulseGrad)" opacity="0" style="mix-blend-mode:screen">
      <animate attributeName="opacity" values="0;0.05;0.14;0.04;0.09;0" dur="4.8s" repeatCount="indefinite"/>
    </rect>

    <!-- 文字底板 -->
    <g filter="url(#panelblur)">
      <rect x="{panel_x}" y="{panel_y}" width="{panel_w:.0f}" height="{panel_h}" rx="26" fill="#06202C" fill-opacity="0.52" stroke="#FFFFFF" stroke-opacity="0.14" stroke-width="1.5"/>
    </g>

    <!-- 昵称：逐字入场 + 浮动 -->
    <g font-family="'Segoe UI','Microsoft YaHei','PingFang SC','Noto Sans SC',sans-serif" font-size="{TITLE_FS}" font-weight="bold" fill="url(#titleGrad)">
{title_layer}
    </g>

    <!-- 打字机轮播 -->
    <g font-family="Consolas,'JetBrains Mono','Courier New',monospace" font-size="{LINE_FS}" fill="#EAF9FF">
{line_layer}
    </g>
{cursor_layer}

{bokeh}

{particles}

    <rect x="0" y="{H - 150}" width="{W}" height="150" fill="url(#bottomFade)"/>
  </g>
</svg>
'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"written: {OUT}  size: {len(svg)} bytes")
print(f"title_w={title_w:.0f}  line_w_max={line_w_max:.0f}  panel={panel_w:.0f}x{panel_h}")
