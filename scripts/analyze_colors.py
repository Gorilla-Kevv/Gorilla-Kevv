"""分析色块构成，确定「底色 / 皮肤 / 眼睛 / 细节」四层的分类阈值。"""
import re

TRACED = r"f:\schoolCompWorks\clone\gtihubMainPagePro\build\footer_traced_e3.svg"
inner = re.search(r"<svg[^>]*>(.*)</svg>", open(TRACED, encoding="utf-8").read(), re.S).group(1).strip()
raw = re.findall(r"<path[^>]*/>", inner)


def info(p):
    mf = re.search(r'fill="(#[0-9a-fA-F]{6})"', p)
    md = re.search(r'd="([^"]+)"', p)
    nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", md.group(1))]
    xs, ys = nums[0::2], nums[1::2]
    if len(xs) < 2 or len(ys) < 2:
        return None
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    r, g, b = int(mf.group(1)[1:3], 16), int(mf.group(1)[3:5], 16), int(mf.group(1)[5:7], 16)
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return dict(r=r, g=g, b=b, lum=lum, area=max(w * h, 1), ink=(lum < 0.42 and min(w, h) < 34))


items = [x for x in (info(p) for p in raw) if x]
total_area = sum(i["area"] for i in items)
print(f"路径 {len(items)}  总面积 {total_area:.0f}")

# 前 15% 路径的面积占比（底色候选）
for frac in (0.08, 0.10, 0.15, 0.20):
    k = int(len(items) * frac)
    print(f"  前 {frac:.0%} 路径（{k} 条）覆盖面积 {sum(i['area'] for i in items[:k]) / total_area:.1%}")

BASE_K = 100
base = items[:BASE_K]
rest = items[BASE_K:]

skin = [i for i in rest if i["r"] > i["g"] > i["b"] and 18 <= i["r"] - i["b"] <= 95 and i["lum"] >= 0.5]
eye = [i for i in rest if i["b"] >= i["r"] and i["b"] > i["g"] and not (i["r"] > i["g"] > i["b"])]
base_ids = {id(i) for i in base}
skin_ids = {id(i) for i in skin}
eye_ids = {id(i) for i in eye}
detail = [i for i in rest if id(i) not in skin_ids and id(i) not in eye_ids]

print(f"\n分层（基于前 {BASE_K} 条）：")
print(f"  底色  {len(base):3d} 条  面积占比 {sum(i['area'] for i in base) / total_area:.1%}")
print(f"  皮肤  {len(skin):3d} 条  面积占比 {sum(i['area'] for i in skin) / total_area:.1%}")
print(f"  眼睛  {len(eye):3d} 条  面积占比 {sum(i['area'] for i in eye) / total_area:.1%}")
print(f"  细节  {len(detail):3d} 条  面积占比 {sum(i['area'] for i in detail) / total_area:.1%}")
print(f"  其中线稿路径在各层分布: 底色 {sum(1 for i in base if i['ink'])} / 皮肤 {sum(1 for i in skin if i['ink'])}"
      f" / 眼睛 {sum(1 for i in eye if i['ink'])} / 细节 {sum(1 for i in detail if i['ink'])}")

# 抽样看皮肤与眼睛的色值
print("\n皮肤层样例色:", [f"#{i['r']:02x}{i['g']:02x}{i['b']:02x}" for i in skin[:6]])
print("眼睛层样例色:", [f"#{i['r']:02x}{i['g']:02x}{i['b']:02x}" for i in eye[:6]])
