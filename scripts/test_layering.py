"""对比不同分层策略对最终画面的影响（与原始描摹结果逐像素比对）。"""
import re
import sys

import cairosvg
from PIL import Image, ImageChops

TRACED = r"f:\schoolCompWorks\clone\gtihubMainPagePro\build\footer_traced_e3.svg"
TMP = r"f:\schoolCompWorks\clone\gtihubMainPagePro\build"

inner = re.search(r"<svg[^>]*>(.*)</svg>", open(TRACED, encoding="utf-8").read(), re.S).group(1).strip()
raw = re.findall(r"<path[^>]*/>", inner)


def parse(p):
    mf = re.search(r'fill="(#[0-9a-fA-F]{6})"', p)
    md = re.search(r'd="([^"]+)"', p)
    nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", md.group(1))]
    xs, ys = nums[0::2], nums[1::2]
    r, g, b = int(mf.group(1)[1:3], 16), int(mf.group(1)[3:5], 16), int(mf.group(1)[5:7], 16)
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return dict(svg=p, r=r, g=g, b=b, lum=lum, w=max(xs) - min(xs), h=max(ys) - min(ys))


items = [parse(p) for p in raw]


def build(k: int, mode: str) -> str:
    """mode=prefix: 前 k 条为底色，其后按颜色分层；mode=color: 全量按颜色分层后再取底色"""
    skin_rule = lambda x: x["r"] > x["g"] >= x["b"] and 18 <= x["r"] - x["b"] <= 95 and x["lum"] >= 0.5
    eye_rule = lambda x: x["b"] > x["r"] and x["b"] > x["g"] and (x["b"] - x["r"]) >= 8 and x["lum"] >= 0.28
    if mode == "prefix":
        base, rest = items[:k], items[k:]
        skin = [x for x in rest if skin_rule(x)]
        sid = {id(x) for x in skin}
        eyes = [x for x in rest if eye_rule(x) and id(x) not in sid]
        eid = {id(x) for x in eyes}
        detail = [x for x in rest if id(x) not in sid and id(x) not in eid]
    else:
        skin = [x for x in items if skin_rule(x)]
        sid = {id(x) for x in skin}
        eyes = [x for x in items if eye_rule(x) and id(x) not in sid]
        eid = {id(x) for x in eyes}
        others = [x for x in items if id(x) not in sid and id(x) not in eid]
        base, detail = others[:k], others[k:]
    layers = base + skin + eyes + detail
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1420 946" width="1420" height="946">{"".join(x["svg"] for x in layers)}</svg>'


# 参照：原始顺序
ref_svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1420 946" width="1420" height="946">{"".join(raw)}</svg>'
open(f"{TMP}/ref.svg", "w", encoding="utf-8").write(ref_svg)
cairosvg.svg2png(url=f"{TMP}/ref.svg", write_to=f"{TMP}/ref.png", output_width=900)
ref = Image.open(f"{TMP}/ref.png").convert("RGB")

for mode, k in (("prefix", 20), ("prefix", 30), ("prefix", 40), ("prefix", 60), ("prefix", 100)):
    svg = build(k, mode)
    f = f"{TMP}/lay_{mode}_{k}.svg"
    open(f, "w", encoding="utf-8").write(svg)
    cairosvg.svg2png(url=f, write_to=f"{TMP}/lay_{mode}_{k}.png", output_width=900)
    im = Image.open(f"{TMP}/lay_{mode}_{k}.png").convert("RGB")
    diff = ImageChops.difference(ref, im).convert("L")
    h = diff.histogram()
    total = sum(h)
    bad = sum(h[20:])
    print(f"{mode:7s} k={k:3d}: 差异像素(>20) {bad / total * 100:.2f}%")
