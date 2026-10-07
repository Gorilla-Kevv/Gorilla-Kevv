"""首图：矢量插画 + 马赛克色块聚散动画 + 标题/打字机文字层（文字内容与位置保持不变）"""
import math
import os
import random
import re
import xml.sax.saxutils as sx

import cairosvg
from PIL import Image, ImageFont

ROOT = r"f:\schoolCompWorks\clone\gtihubMainPagePro"
TRACED = os.path.join(ROOT, "build", "footer_traced_e3.svg")
SRC_PNG = os.path.join(ROOT, "build", "footer_src_final.png")
OUT = os.path.join(ROOT, "assets", "hero-illus-v4.svg")
PREVIEW = os.path.join(ROOT, "build", "hero_final.png")

W, H = 1200, 675
SRC_W, SRC_H = 1420, 946
SCALE = W / SRC_W                      # 插画铺满宽度
ART_H = SRC_H * SCALE                  # 799.4
ART_DY = (ART_H - H) / 2               # 垂直居中裁切量 62.2
CYCLE = 14.0                            # 一个完整循环（秒）

TILE = 80
COLS, ROWS = W // TILE, 10             # 15 x 10（插画空间）
MORPH_SHIFT = -ART_DY                  # 色块层与插画层同步位移

# ---------- 贝塞尔缓动曲线（SMIL calcMode="spline" 的 keySplines 控制点） ----------
HOLD = "0 0 1 1"                       # 静止区间（线性，无位移）
EASE_OUT = "0.34 0.02 0.18 1"          # 飞出：起手有冲劲，末段平滑收住
EASE_IN = "0.26 0.86 0.28 1"           # 飞回：缓起，落位时柔和减速
FADE = "0.42 0 0.58 1"                 # 淡入淡出：两端对称的标准缓动
MOVE_SPLINES = ";".join([HOLD, EASE_OUT, HOLD, EASE_IN, HOLD])
FADE_SPLINES = ";".join([HOLD, FADE, HOLD, FADE, HOLD])

random.seed(7)

# ---------- 1) 插画 ----------
traced = open(TRACED, encoding="utf-8").read()
art = re.search(r"<svg[^>]*>(.*)</svg>", traced, re.S).group(1).strip()

# ---------- 2) 马赛克色块 ----------
mosaic_img = Image.open(SRC_PNG).convert("RGB").resize((COLS, ROWS), Image.BOX)
mpx = mosaic_img.load()

tiles = []
for row in range(ROWS):
    for col in range(COLS):
        r, g, b = mpx[col, row]
        colour = f"#{r:02x}{g:02x}{b:02x}"
        x, y = col * TILE, row * TILE

        # 对角扫描错峰
        s = (col + row) / (COLS + ROWS - 2)
        t_in = 0.26 + s * 0.10
        t_out = 0.92 + s * 0.05

        # 飞出画布的位移：沿"由画面中心向外"的方向，走到边界外再留 120px 余量
        ccx, ccy = x + TILE / 2, y + TILE / 2
        vx, vy = ccx - W / 2, ccy - ART_H / 2
        d = math.hypot(vx, vy)
        if d < 1:
            ux, uy = 0.0, -1.0
        else:
            ux, uy = vx / d, vy / d
        tx = (W / 2 + TILE) / abs(ux) if abs(ux) > 1e-3 else 1e9
        ty = (ART_H / 2 + TILE) / abs(uy) if abs(uy) > 1e-3 else 1e9
        travel = min(tx, ty) + 120
        dx, dy = ux * travel, uy * travel

        # 飞出/飞回的错峰很小，保证"成形停留"是全体一致的
        launch = 0.44 + s * 0.02
        away = 0.545 + s * 0.02
        back = 0.73 + s * 0.02
        home = 0.835 + s * 0.02

        tiles.append(
            f'    <rect x="{x}" y="{y}" width="{TILE}" height="{TILE}" rx="0" fill="{colour}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
            f'keyTimes="0;{t_in:.3f};{t_in + 0.04:.3f};{t_out:.3f};{t_out + 0.04:.3f};1" '
            f'calcMode="spline" keySplines="{FADE_SPLINES}" dur="{CYCLE}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;0 0;{dx:.0f} {dy:.0f};{dx:.0f} {dy:.0f};0 0;0 0" '
            f'keyTimes="0;{launch:.3f};{away:.3f};{back:.3f};{home:.3f};1" '
            f'calcMode="spline" keySplines="{MOVE_SPLINES}" dur="{CYCLE}s" repeatCount="indefinite"/>'
            f'<animate attributeName="rx" values="0;0;22;22;0;0" '
            f'keyTimes="0;{launch:.3f};{away:.3f};{back:.3f};{home:.3f};1" '
            f'calcMode="spline" keySplines="{MOVE_SPLINES}" dur="{CYCLE}s" repeatCount="indefinite"/>'
            f"</rect>"
        )
tile_layer = "\n".join(tiles)

# ---------- 3) 文字度量（与原首图完全一致） ----------
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
        return (f.getlength(ch) if f else 0) or fs * 1.2
    if code > 0x2E7F:
        f = _pick("cjk", fs)
        return (f.getlength(ch) if f else 0) or fs
    f = _pick("latin", fs)
    return (f.getlength(ch) if f else 0) or fs * 0.58


def mono_w(text: str, fs: int) -> float:
    f = _pick("mono", fs)
    return f.getlength(text) if f else len(text) * fs * 0.55


centers = []
cursor_x = 0.0
for ch in TITLE:
    w = char_w(ch, TITLE_FS)
    centers.append((ch, cursor_x + w / 2))
    cursor_x += w
title_w = cursor_x
title_left = (W - title_w) / 2

line_ws = [mono_w(t, LINE_FS) for t in LINES]
line_w_max = max(line_ws)
panel_w = max(title_w, line_w_max + 60) + 90
panel_x = (W - panel_w) / 2
panel_y, panel_h = 232, 196
title_y = panel_y + 78
line_left = panel_x + (panel_w - line_w_max) / 2
line_y = panel_y + 136
CYCLE_TXT = 9.6
SEG = CYCLE_TXT / len(LINES)

title_chars = []
for i, (ch, cx) in enumerate(centers):
    esc = sx.escape(ch)
    title_chars.append(
        f'      <text x="{title_left + cx:.1f}" y="{title_y}" text-anchor="middle" opacity="0" filter="url(#tshadow)">{esc}'
        f'<animate attributeName="opacity" values="0;1" dur="0.5s" begin="{i * 0.05:.2f}s" fill="freeze"/>'
        f'<animate attributeName="y" values="{title_y};{title_y - 5};{title_y}" dur="2.8s" begin="-{i * 0.13:.2f}s" repeatCount="indefinite"/>'
        f'</text>'
    )
title_layer = "\n".join(title_chars)

MATRIX_CHARS = "01<>/#$%&@!?;:=+~^*ABCDEFGHIJKLMNOPQRSTUVWXYZ"
TICKS = 4


def mtx_text(x: float, y: float, glyph: str, fill: str, t0: float, t1: float) -> str:
    return (
        f'      <text x="{x:.1f}" y="{y}" text-anchor="middle" fill="{fill}" opacity="0">{sx.escape(glyph)}'
        f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
        f'keyTimes="0;{t0:.4f};{t0 + 0.002:.4f};{t1:.4f};{t1 + 0.002:.4f};1" dur="{CYCLE_TXT}s" repeatCount="indefinite"/></text>'
    )


matrix_parts = []
for i, (text, lw) in enumerate(zip(LINES, line_ws)):
    n = len(text)
    chw = lw / n
    s = i * SEG / CYCLE_TXT          # 本句窗口起点（占整轮比例）
    wend = s + 0.235                 # 正确字符显示到此处（此后整句隐藏，进入下一句）
    scr_start = s + 0.004            # 乱码翻滚起点
    scr_end = s + 0.052              # 乱码翻滚结束 → 锁定
    for j, ch in enumerate(text):
        if ch == " ":
            continue
        x = line_left + j * chw + chw / 2
        d = j * 0.0025               # 轻微左→右波浪错峰
        a0, a1 = scr_start + d, scr_end + d
        # 单轮：乱码翻滚 → 原地锁定为正确字符（每句文本只出现一次）
        step = (a1 - a0) / TICKS
        for k in range(TICKS):
            g = MATRIX_CHARS[random.randrange(len(MATRIX_CHARS))]
            matrix_parts.append(mtx_text(x, line_y, g, "#5FD8A8", a0 + k * step, a0 + (k + 1) * step))
        matrix_parts.append(mtx_text(x, line_y, ch, "#FFFFFF", a1, wend))
line_layer = "\n".join(matrix_parts)

# ---------- 4) 粒子 / 星点 ----------
particles = []
for i, (x, y, r, dur, begin) in enumerate([
    (140, 120, 3.0, 12, 0), (260, 420, 2.2, 15, 3), (1060, 140, 3.4, 13, 5),
    (980, 400, 2.6, 16, 1), (180, 560, 2.4, 14, 7), (1120, 70, 2.8, 11, 9),
    (70, 300, 2.0, 17, 4), (1140, 300, 2.2, 15, 6), (620, 90, 2.4, 13, 8),
]):
    particles.append(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="{"#B9A7FF" if i % 2 else "#9FB6FF"}" opacity="0.7">'
        f'<animate attributeName="cy" values="{y};{y - 44};{y}" dur="{dur}s" begin="-{begin}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0.08;0.7;0.08" dur="{dur / 3:.1f}s" begin="-{begin}s" repeatCount="indefinite"/>'
        f"</circle>"
    )

sparkles = []
for i, (x, y, r, dur, begin) in enumerate([
    (110, 90, 3.2, 3.2, 0), (330, 60, 2.4, 4.1, 0.9), (880, 80, 3.0, 3.6, 1.7),
    (1110, 520, 2.6, 4.4, 0.4), (250, 520, 2.2, 3.9, 2.2), (1010, 100, 2.8, 3.4, 1.3),
]):
    sparkles.append(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFFFFF">'
        f'<animate attributeName="opacity" values="0.15;1;0.15" dur="{dur}s" begin="-{begin}s" repeatCount="indefinite"/>'
        f"</circle>"
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="hero illustration">
  <defs>
    <clipPath id="frame"><rect x="0" y="0" width="{W}" height="{H}" rx="22"/></clipPath>
    <pattern id="gridp" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="#BFD0FF" stroke-width="1" stroke-opacity="0.75"/>
    </pattern>
    <filter id="panelblur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="7"/></filter>
    <filter id="tshadow" x="-40%" y="-40%" width="180%" height="180%">
      <feDropShadow dx="0" dy="2" stdDeviation="3.2" flood-color="#04121C" flood-opacity="0.85"/>
    </filter>
    <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="50%" stop-color="#FFFFFF" stop-opacity="0.16"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="glowB" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0%" stop-color="#5B6FD8" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#5B6FD8" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glowV" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0%" stop-color="#8A6FD8" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#8A6FD8" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="titleGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#FFE7A3"/>
      <stop offset="45%" stop-color="#FFB3C7"/>
      <stop offset="100%" stop-color="#B9A7FF"/>
    </linearGradient>
    <linearGradient id="w1" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#8FA6FF"/><stop offset="100%" stop-color="#A98BF0"/>
    </linearGradient>
    <linearGradient id="w2" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#5B6FD8"/><stop offset="100%" stop-color="#7C6BD8"/>
    </linearGradient>
    <linearGradient id="w3" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#2C3A5E"/><stop offset="100%" stop-color="#3E4A78"/>
    </linearGradient>
  </defs>

  <g clip-path="url(#frame)">
    <rect x="0" y="0" width="{W}" height="{H}" fill="#1A2340"/>

    <!-- 插画层（垂直居中裁切适配画布） -->
    <g transform="translate(0,{MORPH_SHIFT:.1f}) scale({SCALE:.4f})" opacity="1">
      <animate attributeName="opacity" values="1;1;0;0;1;1"
               keyTimes="0;0.28;0.38;0.93;0.98;1"
               calcMode="spline" keySplines="{FADE_SPLINES}" dur="{CYCLE}s" repeatCount="indefinite"/>
{art}
    </g>

    <!-- 马赛克色块层 -->
    <g transform="translate(0,{MORPH_SHIFT:.1f})">
{tile_layer}
    </g>

    <!-- 矢量网格 -->
    <g opacity="0">
      <animate attributeName="opacity" values="0;0;0.55;0.55;0;0"
               keyTimes="0;0.34;0.44;0.76;0.90;1"
               calcMode="spline" keySplines="{FADE_SPLINES}" dur="{CYCLE}s" repeatCount="indefinite"/>
      <rect x="0" y="0" width="{W}" height="{H}" fill="url(#gridp)"/>
      <rect x="0" y="0" width="{W}" height="{H}" fill="none" stroke="#BFD0FF" stroke-width="2" opacity="0.5"/>
    </g>

    <!-- 掠过的高光 -->
    <g style="mix-blend-mode:screen">
      <g>
        <animateTransform attributeName="transform" type="translate" values="-520 0; 1320 0" dur="7.5s" repeatCount="indefinite"/>
        <rect x="-160" y="-40" width="230" height="{H + 80}" fill="url(#sweep)" transform="skewX(-18)"/>
      </g>
    </g>

    <!-- 底部波浪 -->
    <path d="M0,{H - 88} C160,{H - 116} 300,{H - 70} 470,{H - 88} C640,{H - 104} 760,{H - 66} 940,{H - 88} C1060,{H - 100} 1140,{H - 84} 1200,{H - 96} L1200,{H} L0,{H} Z" fill="url(#w1)" opacity="0.72"/>
    <path d="M0,{H - 68} C140,{H - 88} 290,{H - 48} 460,{H - 66} C630,{H - 82} 750,{H - 50} 920,{H - 68} C1050,{H - 80} 1140,{H - 62} 1200,{H - 74} L1200,{H} L0,{H} Z" fill="url(#w2)" opacity="0.9"/>
    <path d="M0,{H - 44} C170,{H - 62} 310,{H - 30} 480,{H - 42} C650,{H - 54} 780,{H - 30} 950,{H - 44} C1080,{H - 54} 1150,{H - 36} 1200,{H - 48} L1200,{H} L0,{H} Z" fill="url(#w3)"/>

    <!-- 底部光晕 -->
    <g style="mix-blend-mode:screen">
      <ellipse cx="260" cy="{H - 60}" rx="360" ry="150" fill="url(#glowB)">
        <animate attributeName="opacity" values="0.5;0.9;0.5" dur="6s" repeatCount="indefinite"/>
      </ellipse>
      <ellipse cx="950" cy="{H - 40}" rx="360" ry="150" fill="url(#glowV)">
        <animate attributeName="opacity" values="0.9;0.5;0.9" dur="7s" repeatCount="indefinite"/>
      </ellipse>
    </g>

    <!-- 文字底板（在人物插画上适当降低浓度，保持文字可读的同时不遮挡面部） -->
    <g filter="url(#panelblur)">
      <rect x="{panel_x}" y="{panel_y}" width="{panel_w:.0f}" height="{panel_h}" rx="26" fill="#06202C" fill-opacity="0.34" stroke="#FFFFFF" stroke-opacity="0.12" stroke-width="1.5"/>
    </g>
    <rect x="{panel_x}" y="{panel_y + panel_h * 0.18:.0f}" width="{panel_w:.0f}" height="{panel_h * 0.64:.0f}" rx="20" fill="#04121C" opacity="0.22"/>

    <!-- 昵称：逐字入场 + 浮动 -->
    <g font-family="'Segoe UI','Microsoft YaHei','PingFang SC','Noto Sans SC',sans-serif" font-size="{TITLE_FS}" font-weight="bold" fill="url(#titleGrad)">
{title_layer}
    </g>

    <!-- 黑客帝国式乱码解码轮播 -->
    <g font-family="Consolas,'JetBrains Mono','Courier New',monospace" font-size="{LINE_FS}">
{line_layer}
    </g>

    <g style="mix-blend-mode:screen">
{"".join(sparkles)}
{"".join(particles)}
    </g>
  </g>
</svg>
'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"written: {OUT}  size: {os.path.getsize(OUT)} bytes  tiles={COLS * ROWS}  art_dy={MORPH_SHIFT:.1f}")

cairosvg.svg2png(url=OUT, write_to=PREVIEW, output_width=1000)
print("preview:", PREVIEW)

readme_path = os.path.join(ROOT, "README.md")
m = re.search(r"assets/(hero[^\"')\s]*\.svg)", open(readme_path, encoding="utf-8").read())
ref = m.group(1) if m else None
want = os.path.basename(OUT)
print(f"[{'OK' if ref == want else 'WARN'}] README 首图引用: {ref} / 输出: {want}")
