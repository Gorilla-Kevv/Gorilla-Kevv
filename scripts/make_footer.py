import math
import os
import re

import cairosvg

ROOT = r"f:\schoolCompWorks\clone\gtihubMainPagePro"
TRACED = os.path.join(ROOT, "build", "footer_traced_final.svg")
OUT = os.path.join(ROOT, "assets", "footer-v4.svg")
PREVIEW = os.path.join(ROOT, "build", "footer_final.png")

W, H = 1200, 800
SRC_W, SRC_H = 1420, 946                # 2 倍分辨率描摹源（裁切区 710x473）
ART_W, ART_H = W, H                     # 全幅铺满，比例已对齐
ART_X, ART_Y = 0, 0
SCALE = ART_W / SRC_W

# ---------- 1) 描摹图形：每条路径包进 <g>，按散列分配到 16 个动画组 ----------
traced = open(TRACED, encoding="utf-8").read()
inner = re.search(r"<svg[^>]*>(.*)</svg>", traced, re.S).group(1).strip()

GROUPS = 16
parts = inner.split("<path")
grouped = [[] for _ in range(GROUPS)]
for i, chunk in enumerate(parts[1:]):
    path = "<path" + chunk.rstrip()
    if not path.endswith("</path>"):
        path = path.rstrip()          # 自闭合
    gi = (i * 7) % GROUPS             # 散列，避免相邻色块同组
    grouped[gi].append(path)

art_groups = []
for gi, paths in enumerate(grouped):
    art_groups.append(f'          <g class="p{gi}">' + "".join(paths) + "</g>")
art_body = "\n".join(art_groups)

# ---------- 2) 聚散动画：每组的散开向量沿径向分布 ----------
cycle = 10.0
keyframes = []
group_css = []
for gi in range(GROUPS):
    ang = gi * (2 * math.pi / GROUPS) + 0.35
    radius = 34 + (gi % 5) * 12              # 34~82px
    dx = math.cos(ang) * radius
    dy = math.sin(ang) * radius * 0.72
    delay = -0.12 * (gi % 6)
    group_css.append(
        f".p{gi}{{animation:sc{gi} {cycle}s cubic-bezier(.45,0,.55,1) infinite;animation-delay:{delay:.2f}s}}"
    )
    keyframes.append(
        f"@keyframes sc{gi}{{"
        f"0%,40%{{transform:translate(0,0)}}"
        f"62%{{transform:translate({dx:.1f}px,{dy:.1f}px)}}"
        f"82%,100%{{transform:translate(0,0)}}}}"
    )

# ---------- 3) 装饰粒子（配色跟随插画：蓝紫 + 粉） ----------
particles = []
for i, (x, y, r, dur, begin) in enumerate([
    (140, 120, 3.0, 12, 0), (260, 470, 2.2, 15, 3), (1060, 140, 3.4, 13, 5),
    (980, 430, 2.6, 16, 1), (180, 600, 2.4, 14, 7), (1120, 70, 2.8, 11, 9),
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
    (1110, 560, 2.6, 4.4, 0.4), (250, 560, 2.2, 3.9, 2.2), (1010, 100, 2.8, 3.4, 1.3),
]):
    sparkles.append(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFFFFF">'
        f'<animate attributeName="opacity" values="0.15;1;0.15" dur="{dur}s" begin="-{begin}s" repeatCount="indefinite"/>'
        f"</circle>"
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="footer illustration">
  <style>
    {"".join(group_css)}
    {"".join(keyframes)}
  </style>
  <defs>
    <clipPath id="frame"><rect x="0" y="0" width="{W}" height="{H}" rx="22"/></clipPath>
    <pattern id="gridp" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="#BFD0FF" stroke-width="1" stroke-opacity="0.75"/>
    </pattern>
    <linearGradient id="ringGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#9FB6FF"/>
      <stop offset="50%" stop-color="#B9A7FF"/>
      <stop offset="100%" stop-color="#FFC9D8"/>
    </linearGradient>
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

    <!-- 全宽插画：376 条矢量路径，分 16 组做聚散动画 -->
    <g transform="translate({ART_X},{ART_Y}) scale({SCALE:.4f})">
{art_body}
    </g>

    <!-- 矢量网格：散开时浮现，重组时淡出 -->
    <g opacity="0">
      <animate attributeName="opacity" values="0;0;0.5;0.5;0;0" keyTimes="0;0.40;0.60;0.78;0.90;1" dur="{cycle}s" repeatCount="indefinite"/>
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

    <!-- 底部波浪：取自插画的蓝紫配色 -->
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
print(f"written: {OUT}  size: {os.path.getsize(OUT)} bytes  groups={GROUPS}")

cairosvg.svg2png(url=OUT, write_to=PREVIEW, output_width=1000)
print("preview:", PREVIEW)

readme_path = os.path.join(ROOT, "README.md")
m = re.search(r"assets/(footer[^\"')\s]*\.svg)", open(readme_path, encoding="utf-8").read())
ref = m.group(1) if m else None
want = os.path.basename(OUT)
print(f"[{'OK' if ref == want else 'WARN'}] README 引用: {ref} / 输出: {want}")
