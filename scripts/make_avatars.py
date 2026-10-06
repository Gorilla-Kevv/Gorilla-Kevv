import base64
import io

from PIL import Image

# 移除 Pillow 内置的 AVIF 注册（本机无解码器），让 pillow-avif-plugin 接管
Image.OPEN.pop("AVIF", None)
Image.SAVE.pop("AVIF", None)

import pillow_avif  # noqa: E402,F401

S = 200

SOURCES = [
    # (源文件, 输出, 主色, 辅色)
    (r"C:\Users\kevin\Downloads\哔哩哔哩.avif",
     r"f:\schoolCompWorks\clone\gtihubMainPagePro\assets\avatar-bilibili.svg",
     "#7FD8FF", "#00A1D6"),
    (r"C:\Users\kevin\Downloads\wyy.jpg",
     r"f:\schoolCompWorks\clone\gtihubMainPagePro\assets\avatar-netease.svg",
     "#FFB3C7", "#C20C0C"),
]


def to_square_jpeg(path: str) -> str:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    side = min(w, h)
    left, top = (w - side) // 2, (h - side) // 2
    img = img.crop((left, top, left + side, top + side)).resize((S, S), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=88, optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


for src, out, c1, c2 in SOURCES:
    b64 = to_square_jpeg(src)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {S} {S}" width="{S}" height="{S}" role="img" aria-label="avatar">
  <defs>
    <clipPath id="av"><circle cx="{S // 2}" cy="{S // 2}" r="86"/></clipPath>
    <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
    <radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">
      <stop offset="55%" stop-color="{c1}" stop-opacity="0"/>
      <stop offset="82%" stop-color="{c1}" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="{c2}" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <circle cx="{S // 2}" cy="{S // 2}" r="98" fill="url(#halo)">
    <animate attributeName="opacity" values="0.5;1;0.5" dur="4s" repeatCount="indefinite"/>
  </circle>

  <g transform="translate({S // 2},{S // 2})">
    <g>
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="9s" repeatCount="indefinite"/>
      <circle r="92" fill="none" stroke="url(#ring)" stroke-width="4"
              stroke-dasharray="120 60 30 60" stroke-linecap="round" opacity="0.95"/>
    </g>
    <g>
      <animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="14s" repeatCount="indefinite"/>
      <circle r="92" fill="none" stroke="{c2}" stroke-width="2"
              stroke-dasharray="10 46" stroke-linecap="round" opacity="0.7"/>
    </g>
  </g>

  <g clip-path="url(#av)">
    <image href="data:image/jpeg;base64,{b64}" x="{S // 2 - 86}" y="{S // 2 - 86}" width="172" height="172" preserveAspectRatio="xMidYMid slice"/>
  </g>
</svg>
'''
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"written: {out}  size: {len(svg)} bytes")
