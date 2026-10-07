import os

import cairosvg
import vtracer
from PIL import Image

SRC = r"C:\Users\kevin\AppData\Local\CodeBuddyExtension\Data\cfe805eb-31c9-4acf-9297-05f0a314fab2\CodeBuddyIDE\cfe805eb-31c9-4acf-9297-05f0a314fab2\history\8fc61c06892a948b1cd32b2380757372\4b9399dd7d75466c8f8f68d262119876\assets\屏幕截图 2026-07-30 023530.219fbfd7d0.png"
TMP = r"f:\schoolCompWorks\clone\gtihubMainPagePro\build"

os.makedirs(TMP, exist_ok=True)

img = Image.open(SRC).convert("RGB")
print("original:", img.size)

# 裁掉左上 "SEIS... bilibili" 水印与右下角小 logo
crop_top, crop_right = 46, 38
img = img.crop((0, crop_top, img.size[0] - crop_right, img.size[1]))
print("cropped:", img.size)

# 缩放到 900 宽再描摹，控制矢量规模
target_w = 900
img = img.resize((target_w, round(img.size[1] * target_w / img.size[0])), Image.LANCZOS)
src_png = os.path.join(TMP, "footer_src.png")
img.save(src_png, "PNG")
print("trace source:", img.size, os.path.getsize(src_png), "bytes")

traced = os.path.join(TMP, "footer_traced.svg")
vtracer.convert_image_to_svg_py(
    src_png, traced,
    colormode="color",
    hierarchical="stacked",
    mode="spline",
    filter_speckle=6,
    color_precision=6,
    layer_difference=18,
    corner_threshold=60,
    length_threshold=4.0,
    max_iterations=10,
    splice_threshold=45,
    path_precision=2,
)
print("traced svg:", os.path.getsize(traced), "bytes")

# 光栅化回 PNG 以便肉眼比对
cairosvg.svg2png(url=traced, write_to=os.path.join(TMP, "footer_traced.png"),
                 output_width=target_w)
print("rasterized for comparison")
