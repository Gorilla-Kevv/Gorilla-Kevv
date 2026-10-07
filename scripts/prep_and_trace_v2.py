import os
import sys

import cairosvg
import vtracer
from PIL import Image, ImageFilter

SRC = r"C:\Users\kevin\AppData\Local\CodeBuddyExtension\Data\cfe805eb-31c9-4acf-9297-05f0a314fab2\CodeBuddyIDE\cfe805eb-31c9-4acf-9297-05f0a314fab2\history\8fc61c06892a948b1cd32b2380757372\4b9399dd7d75466c8f8f68d262119876\assets\屏幕截图 2026-07-30 023530.219fbfd7d0.png"
TMP = r"f:\schoolCompWorks\clone\gtihubMainPagePro\build"

# 画布 1200x800 的比例（1.5）；左右两侧的墙面/台灯/窗框全部裁掉，只保留人物主体
CROP = (230, 135, 940, 608)       # x0,y0,x1,y1 —— 710 x 473 ≈ 1.501
SCALE2X = 2

LAYER_DIFF = int(sys.argv[1]) if len(sys.argv) > 1 else 12
COLOR_PREC = int(sys.argv[2]) if len(sys.argv) > 2 else 6
SPECKLE = int(sys.argv[3]) if len(sys.argv) > 3 else 6
TAG = sys.argv[4] if len(sys.argv) > 4 else "v2"
PATH_PREC = int(sys.argv[5]) if len(sys.argv) > 5 else 2

os.makedirs(TMP, exist_ok=True)

img = Image.open(SRC).convert("RGB").crop(CROP)
W, H = img.size
print("cropped:", img.size)

# 清理右上角残留墙面（浅色中性像素替换为发色），避开下方的白色衣袖
px = img.load()
samples = [px[int(W * 0.05), int(H * 0.5)]] + [px[int(W * 0.08), int(H * f)] for f in (0.3, 0.7, 0.9)]
HAIR = tuple(sum(c[i] for c in samples) // len(samples) for i in range(3))
def is_wall(r, g, b):
    bright = (r + g + b) / 3
    return bright > 148 and (max(r, g, b) - min(r, g, b)) < 40   # 浅色低饱和：墙/灯/框；皮肤饱和度更高不会被误伤


fixed = 0
for y in range(H):
    for x in range(W):
        # 只清理外围边框带（上 8%、左 4%、右 4%），保护人物主体
        in_frame = y < H * 0.08 or x < W * 0.04 or (x > W * 0.96 and y < H * 0.72)
        if in_frame:
            r, g, b = px[x, y]
            if is_wall(r, g, b):
                px[x, y] = HAIR
                fixed += 1
print(f"wall remnants cleaned: {fixed} px -> hair color {HAIR}")

clean = img.filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.GaussianBlur(0.4))
big = clean.resize((W * SCALE2X, H * SCALE2X), Image.LANCZOS)
src_png = os.path.join(TMP, f"footer_src_{TAG}.png")
big.save(src_png, "PNG")

traced = os.path.join(TMP, f"footer_traced_{TAG}.svg")
vtracer.convert_image_to_svg_py(
    src_png, traced,
    colormode="color",
    hierarchical="stacked",
    mode="spline",
    filter_speckle=SPECKLE,
    color_precision=COLOR_PREC,
    layer_difference=LAYER_DIFF,
    corner_threshold=60,
    length_threshold=3.5,
    max_iterations=10,
    splice_threshold=45,
    path_precision=PATH_PREC,
)
size = os.path.getsize(traced)
paths = open(traced, encoding="utf-8").read().count("<path")
print(f"traced: {size} bytes, {paths} paths  (layer_diff={LAYER_DIFF}, color_prec={COLOR_PREC}, speckle={SPECKLE}, path_prec={PATH_PREC})")

cairosvg.svg2png(url=traced, write_to=os.path.join(TMP, f"footer_traced_{TAG}.png"), output_width=1200)
print("rasterized")
