"""首图动画：起稿 → 逐层上色（底色/皮肤/眼睛/细节）→ 成图 → 马赛克 → 色块飞出清场 → 循环

要点：
* 上色按图层顺序推进，每层是一组同色系路径（保持组内原始叠放顺序）
* 底色层 = 原始叠放顺序中最靠前的 100 条（覆盖 93% 面积的大色块），
  因此整体叠放顺序与原图接近，最终画面与原插画基本一致
* 清场：色块飞出画面后不再飞回，画面清空即进入下一轮循环
"""
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
OUT = os.path.join(ROOT, "assets", "hero-illus-v8.svg")
PREVIEW = os.path.join(ROOT, "build", "hero_final.png")

W, H = 1200, 675
SRC_W, SRC_H = 1420, 946
SCALE = W / SRC_W
ART_H = SRC_H * SCALE
ART_DY = (ART_H - H) / 2
MORPH_SHIFT = -ART_DY
CYCLE = 12.0                            # 一个完整循环（秒）

TILE = 80
COLS, ROWS = W // TILE, 10

# ---------- 贝塞尔缓动 ----------
HOLD = "0 0 1 1"
EASE_OUT = "0.34 0.02 0.18 1"           # 飞出：起手有冲劲，末段平滑收住
FADE = "0.42 0 0.58 1"
MOVE_SPLINES = ";".join([HOLD, EASE_OUT, HOLD, HOLD, HOLD])
FADE_SPLINES = ";".join([HOLD, FADE, HOLD, FADE, HOLD])

random.seed(7)

# ---------- 1) 路径解析与分层 ----------
traced = open(TRACED, encoding="utf-8").read()
inner = re.search(r"<svg[^>]*>(.*)</svg>", traced, re.S).group(1).strip()
raw_paths = re.findall(r"<path[^>]*/>", inner)


def parse_path(p: str):
    mf = re.search(r'fill="(#[0-9a-fA-F]{6})"', p)
    md = re.search(r'd="([^"]+)"', p)
    if not (mf and md):
        return None
    nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", md.group(1))]
    xs, ys = nums[0::2], nums[1::2]
    if len(xs) < 2 or len(ys) < 2:
        return None
    r, g, b = int(mf.group(1)[1:3], 16), int(mf.group(1)[3:5], 16), int(mf.group(1)[5:7], 16)
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return dict(svg=p, r=r, g=g, b=b, lum=lum, w=max(xs) - min(xs), h=max(ys) - min(ys))


items = [x for x in (parse_path(p) for p in raw_paths) if x]

# 线稿（起稿阶段单独一层）
ink = [x for x in items if x["lum"] < 0.42 and min(x["w"], x["h"]) < 34]

# 上色四层：底色取原始叠放顺序最靠前的若干条（保证大块底子与叠放关系不变，
# 实测最终画面与原始描摹差异 < 0.35%），其后按颜色族分出 皮肤 / 眼睛 / 细节
BASE_K = 30
base = items[:BASE_K]
rest = items[BASE_K:]

skin = [x for x in rest
        if x["r"] > x["g"] >= x["b"] and 18 <= x["r"] - x["b"] <= 95 and x["lum"] >= 0.5]
skin_ids = {id(x) for x in skin}
eyes = [x for x in rest
        if x["b"] > x["r"] and x["b"] > x["g"] and (x["b"] - x["r"]) >= 8 and x["lum"] >= 0.28
        and id(x) not in skin_ids]
eye_ids = {id(x) for x in eyes}
detail = [x for x in rest if id(x) not in skin_ids and id(x) not in eye_ids]
print(f"分层：底色 {len(base)} / 皮肤 {len(skin)} / 眼睛 {len(eyes)} / 细节 {len(detail)} / 线稿 {len(ink)}")

LAYER_ORDER = [("base", base), ("skin", skin), ("eyes", eyes), ("detail", detail)]

# ---------- 2) 各层动画时间 ----------
LAYER_TIME = {"base": (0.165, 0.205), "skin": (0.210, 0.250),
              "eyes": (0.260, 0.292), "detail": (0.300, 0.352)}
WRAP_OUT, WRAP_IN = 0.520, 0.580        # 交给马赛克：整幅淡出

layers = []
for name, plist in LAYER_ORDER:
    t0, t1 = LAYER_TIME[name]
    body = "".join(x["svg"] for x in plist)
    if not body:
        continue
    layers.append(
        f'      <g opacity="0" data-layer="{name}">'
        f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{t0:.3f};{t1:.3f};1" '
        f'calcMode="spline" keySplines="{";".join([HOLD, FADE, HOLD])}" '
        f'dur="{CYCLE}s" repeatCount="indefinite"/>' + body + "</g>"
    )
layer_body = "\n".join(layers)

defs_ink = '    <g id="ink">' + "".join(x["svg"] for x in ink) + "</g>"

# ---------- 3) 马赛克色块 ----------
mosaic_img = Image.open(SRC_PNG).convert("RGB").resize((COLS, ROWS), Image.BOX)
mpx = mosaic_img.load()

tiles = []
for row in range(ROWS):
    for col in range(COLS):
        r, g, b = mpx[col, row]
        colour = f"#{r:02x}{g:02x}{b:02x}"
        x, y = col * TILE, row * TILE

        s = (col + row) / (COLS + ROWS - 2)
        t_in = 0.50 + s * 0.05
        t_out = 0.94 + s * 0.02

        ccx, ccy = x + TILE / 2, y + TILE / 2
        vx, vy = ccx - W / 2, ccy - ART_H / 2
        d = math.hypot(vx, vy)
        ux, uy = (0.0, -1.0) if d < 1 else (vx / d, vy / d)
        tx = (W / 2 + TILE) / abs(ux) if abs(ux) > 1e-3 else 1e9
        ty = (ART_H / 2 + TILE) / abs(uy) if abs(uy) > 1e-3 else 1e9
        travel = min(tx, ty) + 120
        dx, dy = ux * travel, uy * travel

        launch = 0.64 + s * 0.03        # 飞出起点
        away = 0.78 + s * 0.03          # 全部离场（此后不再飞回）

        # 位置复位必须排在所有色块完全淡出之后（最晚 t_out+0.03 = 0.99），
        # 否则会在还看得见的时候被拉回原位，形成"收回"的瞬跳
        RESET_A, RESET_B = 0.992, 0.999
        tiles.append(
            f'    <rect x="{x}" y="{y}" width="{TILE}" height="{TILE}" rx="0" fill="{colour}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
            f'keyTimes="0;{t_in:.3f};{t_in + 0.03:.3f};{t_out:.3f};{t_out + 0.03:.3f};1" '
            f'calcMode="spline" keySplines="{FADE_SPLINES}" dur="{CYCLE}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;0 0;{dx:.0f} {dy:.0f};{dx:.0f} {dy:.0f};0 0;0 0" '
            f'keyTimes="0;{launch:.3f};{away:.3f};{RESET_A};{RESET_B};1" '
            f'calcMode="spline" keySplines="{MOVE_SPLINES}" dur="{CYCLE}s" repeatCount="indefinite"/>'
            f'<animate attributeName="rx" values="0;0;22;22;0;0" '
            f'keyTimes="0;{launch:.3f};{away:.3f};{RESET_A};{RESET_B};1" '
            f'calcMode="spline" keySplines="{MOVE_SPLINES}" dur="{CYCLE}s" repeatCount="indefinite"/>'
            f"</rect>"
        )
tile_layer = "\n".join(tiles)

# ---------- 4) 文字度量 ----------
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
    if key not in _cache:
        f = None
        for p in FONT_PATHS[kind]:
            try:
                f = ImageFont.truetype(p, size)
                break
            except OSError:
                continue
        _cache[key] = f
    return _cache[key]


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
    s = i * SEG / CYCLE_TXT
    wend = s + 0.235
    scr_start = s + 0.004
    scr_end = s + 0.052
    for j, ch in enumerate(text):
        if ch == " ":
            continue
        x = line_left + j * chw + chw / 2
        d = j * 0.0025
        a0, a1 = scr_start + d, scr_end + d
        step = (a1 - a0) / TICKS
        for k in range(TICKS):
            g = MATRIX_CHARS[random.randrange(len(MATRIX_CHARS))]
            matrix_parts.append(mtx_text(x, line_y, g, "#5FD8A8", a0 + k * step, a0 + (k + 1) * step))
        matrix_parts.append(mtx_text(x, line_y, ch, "#FFFFFF", a1, wend))
line_layer = "\n".join(matrix_parts)

# ---------- 5) 粒子 / 星点 ----------
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

    <!-- 起稿遮罩：白色方块自上而下扫过 -->
    <mask id="m_line" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">
      <rect x="-40" y="-820" width="{W + 80}" height="830" fill="#FFFFFF">
        <animate attributeName="y" values="-820;-820;0;0;-820;-820"
                 keyTimes="0;0.030;0.150;0.340;0.380;1" dur="{CYCLE}s" repeatCount="indefinite"/>
      </rect>
    </mask>

{defs_ink}
  </defs>

  <g clip-path="url(#frame)">
    <rect x="0" y="0" width="{W}" height="{H}" fill="#1A2340"/>

    <!-- 起稿：线稿自上而下勾出 -->
    <g mask="url(#m_line)">
      <g transform="translate(0,{MORPH_SHIFT:.1f}) scale({SCALE:.4f})" opacity="1">
        <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.200;0.320;1"
                 dur="{CYCLE}s" repeatCount="indefinite"/>
        <use xlink:href="#ink" href="#ink"/>
      </g>
    </g>

    <!-- 逐层上色：底色 → 皮肤 → 眼睛 → 细节；整体在交给马赛克时淡出 -->
    <g transform="translate(0,{MORPH_SHIFT:.1f}) scale({SCALE:.4f})" opacity="0">
      <animate attributeName="opacity" values="0;0;1;1;0;0"
               keyTimes="0;0.030;0.050;{WRAP_OUT};{WRAP_IN};1" dur="{CYCLE}s" repeatCount="indefinite"/>
{layer_body}
    </g>

    <!-- 马赛克色块：拼合 → 飞出画面（清场） -->
    <g transform="translate(0,{MORPH_SHIFT:.1f})">
{tile_layer}
    </g>

    <!-- 矢量网格 -->
    <g opacity="0">
      <animate attributeName="opacity" values="0;0;0.55;0.55;0;0"
               keyTimes="0;0.50;0.56;0.92;0.98;1"
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

    <!-- 文字底板 -->
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
print(f"written: {OUT}  size: {os.path.getsize(OUT)} bytes  tiles={COLS * ROWS}  cycle={CYCLE}s")

readme_path = os.path.join(ROOT, "README.md")
m = re.search(r"assets/(hero[^\"')\s]*\.svg)", open(readme_path, encoding="utf-8").read())
ref = m.group(1) if m else None
want = os.path.basename(OUT)
print(f"[{'OK' if ref == want else 'WARN'}] README 首图引用: {ref} / 输出: {want}")
