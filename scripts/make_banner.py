import base64
import io
import random

from PIL import Image

SRC = r"C:\Users\kevin\Pictures\Screenshots\屏幕截图 2026-10-07 025751.png"
OUT = r"f:\schoolCompWorks\clone\gtihubMainPagePro\assets\banner.svg"

W, H = 1200, 675

# 1) 压缩原图为 JPEG，控制在合适体积
img = Image.open(SRC).convert("RGB")
img = img.resize((W, H), Image.LANCZOS)
buf = io.BytesIO()
img.save(buf, "JPEG", quality=82, optimize=True, progressive=True)
data = buf.getvalue()
print(f"jpeg bytes: {len(data)}  base64 bytes: {len(data) * 4 // 3}")

b64 = base64.b64encode(data).decode("ascii")

random.seed(20261007)

PARTICLE_COLORS = [
    ("#8FFFE4", 0.85),   # 青绿荧光
    ("#B9A7FF", 0.8),    # 淡紫
    ("#FFFFFF", 0.75),   # 白
    ("#5FE8C8", 0.7),    # 深青
]


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

# 大颗虚化光斑
bokeh = "\n".join(
    f'    <circle cx="{random.uniform(60, W - 60):.0f}" cy="{random.uniform(80, H - 120):.0f}" '
    f'r="{random.uniform(14, 30):.0f}" fill="{"#B9A7FF" if i % 2 else "#8FFFE4"}" opacity="0.18" filter="url(#bblur)">'
    f'<animate attributeName="opacity" values="0.06;0.3;0.06" dur="{random.uniform(5, 9):.1f}s" '
    f'begin="-{random.uniform(0, 6):.1f}s" repeatCount="indefinite"/></circle>'
    for i in range(7)
)

# 旋转灯柱：从顶部 pivot 向下张开的光锥，左右摆动
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

# 移动追光：横向扫过的大范围光斑
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

# 光带：上下扫过的细亮条
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

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="stage banner">
  <defs>
    <clipPath id="frame"><rect x="0" y="0" width="{W}" height="{H}" rx="22"/></clipPath>
    <filter id="pblur" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="1.6"/></filter>
    <filter id="bblur" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="10"/></filter>
    <filter id="sblur" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="46"/></filter>
    <linearGradient id="bottomFade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0B1F2A" stop-opacity="0"/>
      <stop offset="100%" stop-color="#0B1F2A" stop-opacity="0.35"/>
    </linearGradient>
    <linearGradient id="pulseGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#7FFFE0" stop-opacity="0.9"/>
      <stop offset="50%" stop-color="#B9A7FF" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#FFC7F0" stop-opacity="0.9"/>
    </linearGradient>
{"".join(chr(10) + "    " + f'<linearGradient id="cone{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{c}" stop-opacity="0.45"/><stop offset="45%" stop-color="{c}" stop-opacity="0.16"/><stop offset="100%" stop-color="{c}" stop-opacity="0"/></linearGradient>' for i, c in enumerate(BEAM_COLORS))}
  </defs>

  <g clip-path="url(#frame)">
    <image href="data:image/jpeg;base64,{b64}" x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"/>

    <!-- 移动追光 -->
    <g style="mix-blend-mode:screen">
{spots}
    </g>

    <!-- 旋转灯柱 -->
    <g style="mix-blend-mode:screen">
{cones}
    </g>

    <!-- 扫过的光带 -->
    <g style="mix-blend-mode:screen">
{streaks}
    </g>

    <!-- 呼吸式明暗脉冲 -->
    <rect x="0" y="0" width="{W}" height="{H}" fill="url(#pulseGrad)" opacity="0" style="mix-blend-mode:screen">
      <animate attributeName="opacity" values="0;0.05;0.14;0.04;0.09;0" dur="4.8s" repeatCount="indefinite"/>
    </rect>

{bokeh}

{particles}

    <rect x="0" y="{H - 150}" width="{W}" height="150" fill="url(#bottomFade)"/>
  </g>
</svg>
'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"written: {OUT}  size: {len(svg)} bytes")
