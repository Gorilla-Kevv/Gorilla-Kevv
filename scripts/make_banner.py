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

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="stage banner">
  <defs>
    <clipPath id="frame"><rect x="0" y="0" width="{W}" height="{H}" rx="22"/></clipPath>
    <filter id="pblur" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="1.6"/></filter>
    <filter id="bblur" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="10"/></filter>
    <linearGradient id="beam" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#B9A7FF" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="#B9A7FF" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="bottomFade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0B1F2A" stop-opacity="0"/>
      <stop offset="100%" stop-color="#0B1F2A" stop-opacity="0.35"/>
    </linearGradient>
  </defs>

  <g clip-path="url(#frame)">
    <image href="data:image/jpeg;base64,{b64}" x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"/>

    <!-- 扫动光束 -->
    <g opacity="0.35">
      <g transform="translate(300,0) rotate(18)">
        <g>
          <animateTransform attributeName="transform" type="rotate" values="-6;7;-6" dur="13s" repeatCount="indefinite"/>
          <path d="M-26,0 L26,0 L150,{H} L-150,{H} Z" fill="url(#beam)"/>
        </g>
      </g>
      <g transform="translate(880,0) rotate(-20)">
        <g>
          <animateTransform attributeName="transform" type="rotate" values="6;-7;6" dur="16s" repeatCount="indefinite"/>
          <path d="M-22,0 L22,0 L130,{H} L-130,{H} Z" fill="url(#beam)"/>
        </g>
      </g>
    </g>

{bokeh}

{particles}

    <rect x="0" y="{H - 150}" width="{W}" height="150" fill="url(#bottomFade)"/>
  </g>
</svg>
'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"written: {OUT}  size: {len(svg)} bytes")
