import math
import os
import random
import re

import cairosvg
from PIL import Image

ROOT = r"f:\schoolCompWorks\clone\gtihubMainPagePro"
TRACED = os.path.join(ROOT, "build", "footer_traced_e3.svg")
SRC_PNG = os.path.join(ROOT, "build", "footer_src_final.png")
OUT = os.path.join(ROOT, "assets", "footer-v5.svg")
PREVIEW = os.path.join(ROOT, "build", "footer_final.png")

W, H = 1200, 800
SRC_W, SRC_H = 1420, 946
SCALE = W / SRC_W
CYCLE = 12.0                     # 一个完整循环（秒）

TILE = 80                        # 正方形色块边长
COLS, ROWS = W // TILE, H // TILE   # 15 x 10 = 150 块
TILE_W = TILE_H = TILE

# ---------- 1) 描摹插画（单层，不再拆散各条路径） ----------
traced = open(TRACED, encoding="utf-8").read()
art = re.search(r"<svg[^>]*>(.*)</svg>", traced, re.S).group(1).strip()

# ---------- 2) 马赛克色块：取每格平均色，按相同色系合并 ----------
mosaic_img = Image.open(SRC_PNG).convert("RGB").resize((COLS, ROWS), Image.BOX)
mpx = mosaic_img.load()
print("tile colors sampled:", COLS, "x", ROWS)

random.seed(7)
tiles = []
for row in range(ROWS):
    for col in range(COLS):
        r, g, b = mpx[col, row]
        colour = f"#{r:02x}{g:02x}{b:02x}"
        x, y = col * TILE, row * TILE

        # 对角扫描错峰
        s = (col + row) / (COLS + ROWS - 2)
        t_in = 0.26 + s * 0.14
        t_out = 0.80 + s * 0.10
        # 分离向量：以画面中心为原点向外，幅度克制（保持画面可读）
        cx, cy = x + TILE / 2, y + TILE / 2
        ang = math.atan2(cy - H / 2, cx - W / 2) + random.uniform(-0.3, 0.3)
        dist = random.uniform(24, 62)
        dx, dy = math.cos(ang) * dist, math.sin(ang) * dist * 0.8

        tiles.append(
            # 无缝铺满整格：对齐时即为一幅马赛克画；分离时圆角渐显、缝隙自然出现
            f'    <rect x="{x}" y="{y}" width="{TILE}" height="{TILE}" rx="0" fill="{colour}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
            f'keyTimes="0;{t_in:.3f};{t_in + 0.05:.3f};{t_out:.3f};{t_out + 0.05:.3f};1" dur="{CYCLE}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;0 0;{dx:.0f} {dy:.0f};0 0;0 0" keyTimes="0;0.44;0.62;0.78;1" dur="{CYCLE}s" repeatCount="indefinite"/>'
            f'<animate attributeName="rx" values="0;0;22;0;0" keyTimes="0;0.44;0.62;0.78;1" dur="{CYCLE}s" repeatCount="indefinite"/>'
            f"</rect>"
        )
tile_layer = "\n".join(tiles)

# ---------- 3) 装饰粒子 ----------
particles = []
for i, (x, y, r, dur, begin) in enumerate([
    (140, 120, 3.0, 12, 0), (260, 470, 2.2, 15, 3), (1060, 140, 3.4, 13, 5),
    (980, 430, 2.6, 16, 1), (180, 620, 2.4, 14, 7), (1120, 70, 2.8, 11, 9),
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
    (1110, 640, 2.6, 4.4, 0.4), (250, 640, 2.2, 3.9, 2.2), (1010, 100, 2.8, 3.4, 1.3),
]):
    sparkles.append(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFFFFF">'
        f'<animate attributeName="opacity" values="0.15;1;0.15" dur="{dur}s" begin="-{begin}s" repeatCount="indefinite"/>'
        f"</circle>"
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="footer illustration">
  <defs>
    <clipPath id="frame"><rect x="0" y="0" width="{W}" height="{H}" rx="22"/></clipPath>
    <pattern id="gridp" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="#BFD0FF" stroke-width="1" stroke-opacity="0.75"/>
    </pattern>
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

    <!-- 插画层：色块重组完成后淡入 -->
    <g transform="translate(0,0) scale({SCALE:.4f})" opacity="1">
      <animate attributeName="opacity" values="1;1;0;0;1;1"
               keyTimes="0;0.34;0.44;0.86;0.94;1" dur="{CYCLE}s" repeatCount="indefinite"/>
{art}
    </g>

    <!-- 马赛克色块层：色彩按格平均，聚拢成方块后向外分离再归位 -->
{tile_layer}

    <!-- 矢量网格：色块阶段浮现 -->
    <g opacity="0">
      <animate attributeName="opacity" values="0;0;0.4;0.4;0;0"
               keyTimes="0;0.30;0.44;0.80;0.90;1" dur="{CYCLE}s" repeatCount="indefinite"/>
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

    <g style="mix-blend-mode:screen">
{"".join(sparkles)}
{"".join(particles)}
    </g>
  </g>
</svg>
'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"written: {OUT}  size: {os.path.getsize(OUT)} bytes  tiles={COLS * ROWS}")

cairosvg.svg2png(url=OUT, write_to=PREVIEW, output_width=1000)
print("preview:", PREVIEW)

readme_path = os.path.join(ROOT, "README.md")
m = re.search(r"assets/(footer[^\"')\s]*\.svg)", open(readme_path, encoding="utf-8").read())
ref = m.group(1) if m else None
want = os.path.basename(OUT)
print(f"[{'OK' if ref == want else 'WARN'}] README 引用: {ref} / 输出: {want}")
