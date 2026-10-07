import os
import re

import cairosvg

ROOT = r"f:\schoolCompWorks\clone\gtihubMainPagePro"
TRACED = os.path.join(ROOT, "build", "footer_traced_mid.svg")
OUT = os.path.join(ROOT, "assets", "footer-v2.svg")
PREVIEW = os.path.join(ROOT, "build", "footer_final.png")

W, H = 1200, 480
ART_W, ART_H = 700, 377          # 900x485 等比缩放
ART_X, ART_Y = (W - ART_W) // 2, 16   # 底部 393，波浪从 405 起，互不遮挡
ART_CX, ART_CY = ART_X + ART_W / 2, ART_Y + ART_H / 2

# 1) 取出描摹结果的内部图形
traced = open(TRACED, encoding="utf-8").read()
inner = re.search(r"<svg[^>]*>(.*)</svg>", traced, re.S).group(1).strip()
vb = re.search(r'viewBox="([^"]+)"', traced)
print("traced viewBox:", vb.group(1) if vb else "none")
src_w, src_h = 900, 485
scale = ART_W / src_w

# 2) 装饰粒子
particles = []
for i, (x, y, r, dur, begin) in enumerate([
    (120, 120, 3.0, 12, 0), (210, 300, 2.2, 15, 3), (1080, 150, 3.4, 13, 5),
    (990, 330, 2.6, 16, 1), (150, 400, 2.4, 14, 7), (1120, 60, 2.8, 11, 9),
    (60, 250, 2.0, 17, 4), (1150, 240, 2.2, 15, 6),
]):
    particles.append(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="{"#B9A7FF" if i % 2 else "#8FFFE4"}" opacity="0.8">'
        f'<animate attributeName="cy" values="{y};{y - 46};{y}" dur="{dur}s" begin="-{begin}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0.1;0.85;0.1" dur="{dur / 3:.1f}s" begin="-{begin}s" repeatCount="indefinite"/>'
        f"</circle>"
    )

sparkles = []
for i, (x, y, r, dur, begin) in enumerate([
    (95, 90, 3.2, 3.2, 0), (320, 60, 2.4, 4.1, 0.9), (880, 70, 3.0, 3.6, 1.7),
    (1120, 380, 2.6, 4.4, 0.4), (250, 380, 2.2, 3.9, 2.2), (1010, 90, 2.8, 3.4, 1.3),
]):
    sparkles.append(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFFFFF">'
        f'<animate attributeName="opacity" values="0.15;1;0.15" dur="{dur}s" begin="-{begin}s" repeatCount="indefinite"/>'
        f"</circle>"
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="footer illustration">
  <defs>
    <clipPath id="frame"><rect x="0" y="0" width="{W}" height="{H}" rx="22"/></clipPath>
    <clipPath id="artclip"><rect x="{ART_X}" y="{ART_Y}" width="{ART_W}" height="{ART_H}" rx="20"/></clipPath>
    <linearGradient id="bg" x1="0" y1="0" x2="0.3" y2="1">
      <stop offset="0%" stop-color="#0B1F2A"/>
      <stop offset="55%" stop-color="#123040"/>
      <stop offset="100%" stop-color="#17394B"/>
    </linearGradient>
    <linearGradient id="ringGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#8FFFE4"/>
      <stop offset="50%" stop-color="#B9A7FF"/>
      <stop offset="100%" stop-color="#FFB3C7"/>
    </linearGradient>
    <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="50%" stop-color="#FFFFFF" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="glowT" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0%" stop-color="#8FFFE4" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="#8FFFE4" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glowP" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0%" stop-color="#B9A7FF" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="#B9A7FF" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="w1" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#FF9AA2"/><stop offset="100%" stop-color="#FFB6C9"/>
    </linearGradient>
    <linearGradient id="w2" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#FF6B6B"/><stop offset="100%" stop-color="#FF9F45"/>
    </linearGradient>
    <linearGradient id="w3" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#9B72FF"/><stop offset="100%" stop-color="#4D96FF"/>
    </linearGradient>
    <filter id="softglow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="16"/>
    </filter>
    <filter id="pblur" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="1.4"/>
    </filter>
  </defs>

  <g clip-path="url(#frame)">
    <rect x="0" y="0" width="{W}" height="{H}" fill="url(#bg)"/>

    <ellipse cx="230" cy="150" rx="330" ry="220" fill="url(#glowT)"/>
    <ellipse cx="980" cy="300" rx="330" ry="220" fill="url(#glowP)"/>

    <!-- 插画卡片 -->
    <g>
      <animateTransform attributeName="transform" type="translate" values="0 0; 0 -7; 0 0" dur="9s" repeatCount="indefinite"/>
      <rect x="{ART_X - 3}" y="{ART_Y - 3}" width="{ART_W + 6}" height="{ART_H + 6}" rx="23"
            fill="none" stroke="url(#ringGrad)" stroke-width="3" opacity="0.9"/>
      <g filter="url(#softglow)" opacity="0.5">
        <rect x="{ART_X}" y="{ART_Y}" width="{ART_W}" height="{ART_H}" rx="20" fill="#8FFFE4" opacity="0.18">
          <animate attributeName="opacity" values="0.08;0.28;0.08" dur="5s" repeatCount="indefinite"/>
        </rect>
      </g>
      <g clip-path="url(#artclip)">
        <g transform="translate({ART_X},{ART_Y}) scale({scale:.4f})">
{inner}
        </g>
        <!-- 掠过卡片的高光 -->
        <g>
          <animateTransform attributeName="transform" type="translate" values="-620 0; 760 0" dur="6.5s" repeatCount="indefinite"/>
          <rect x="{ART_X - 260}" y="{ART_Y - 40}" width="240" height="{ART_H + 80}" fill="url(#sweep)" transform="skewX(-18)" style="mix-blend-mode:screen"/>
        </g>
      </g>
    </g>

    <!-- 底部波浪 -->
    <path d="M0,414 C160,382 300,432 470,414 C640,396 760,438 940,414 C1060,398 1140,418 1200,406 L1200,{H} L0,{H} Z" fill="url(#w1)" opacity="0.85"/>
    <path d="M0,436 C140,412 290,456 460,438 C630,420 750,456 920,436 C1050,421 1140,442 1200,428 L1200,{H} L0,{H} Z" fill="url(#w2)" opacity="0.92"/>
    <path d="M0,458 C170,440 310,472 480,458 C650,444 780,472 950,458 C1080,446 1150,464 1200,452 L1200,{H} L0,{H} Z" fill="url(#w3)"/>

{"".join(sparkles)}
{"".join(particles)}
  </g>
</svg>
'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"written: {OUT}  size: {os.path.getsize(OUT)} bytes")

# 光栅化用于版式检查
cairosvg.svg2png(url=OUT, write_to=PREVIEW, output_width=1000)
print("preview:", PREVIEW)

# README 引用自检
readme_path = os.path.join(ROOT, "README.md")
m = re.search(r"assets/(footer[^\"')\s]*\.svg)", open(readme_path, encoding="utf-8").read())
ref = m.group(1) if m else None
want = os.path.basename(OUT)
print(f"[{'OK' if ref == want else 'WARN'}] README 引用: {ref} / 输出: {want}")
