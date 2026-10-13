"""页脚：舞台照片（缩小高度、人物居中裁切）+ 灯光特效 + 「来找我玩」联系面板

联系面板内容与 README 原「📬 来找我玩」章节一致：标题、四枚链接徽章、
下方句子；徽章图形用矢量重绘（含极简品牌图标），链接以 SVG <a> 保留。
"""
import base64
import io
import json
import random
import subprocess

from PIL import Image, ImageFont

SRC = r"C:\Users\kevin\Pictures\Screenshots\屏幕截图 2026-10-07 025751.png"
OUT = r"f:\schoolCompWorks\clone\gtihubMainPagePro\assets\footer-stage-v3.svg"

W, H = 1200, 520                     # 高度由 800 缩到 520，占用更小

# ---------- 1) 底图（宽度铺满、高度居中裁切，人物主体保持中央） ----------
img = Image.open(SRC).convert("RGB")
img = img.resize((W, round(W * img.size[1] / img.size[0])), Image.LANCZOS)
buf = io.BytesIO()
img.save(buf, "JPEG", quality=82, optimize=True, progressive=True)
b64 = base64.b64encode(buf.getvalue()).decode("ascii")
print(f"jpeg bytes: {len(buf.getvalue())}  source: {img.size} -> canvas {W}x{H}")

# ---------- 2) 文本度量 ----------
FONT_PATHS = {
    "latin": [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"],
    "cjk": [r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\msyh.ttc"],
    "emoji": [r"C:\Windows\Fonts\seguiemj.ttf"],
}
_cache = {}


def _font(kind: str, size: int):
    key = (kind, size)
    if key not in _cache:
        f = None
        for p in FONT_PATHS[kind]:
            try:
                f = ImageFont.truetype(p, size)
                break
            except OSError:
                continue
        _cache[key] = f
    return _cache[key]


def text_w(s: str, size: int) -> float:
    total = 0.0
    for ch in s:
        code = ord(ch)
        if code >= 0x1F000 or (0x2600 <= code <= 0x27BF):
            f = _font("emoji", size)
            total += (f.getlength(ch) if f else 0) or size * 1.2
        elif code > 0x2E7F:
            f = _font("cjk", size)
            total += (f.getlength(ch) if f else 0) or size
        else:
            f = _font("latin", size)
            total += (f.getlength(ch) if f else 0) or size * 0.58
    return total


# ---------- 3) 粒子 / 光效 ----------
random.seed(20261007)

PARTICLE_COLORS = [("#8FFFE4", 0.85), ("#B9A7FF", 0.8), ("#FFFFFF", 0.75), ("#5FE8C8", 0.7)]


def particle(i: int) -> str:
    x = random.uniform(0, W)
    y = random.uniform(0, H)
    r = random.uniform(1.6, 4.6)
    color, op = random.choice(PARTICLE_COLORS)
    drift = random.uniform(40, 120)
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


particles = "\n".join(particle(i) for i in range(24))

bokeh = "\n".join(
    f'    <circle cx="{random.uniform(60, W - 60):.0f}" cy="{random.uniform(50, H - 140):.0f}" '
    f'r="{random.uniform(12, 26):.0f}" fill="{"#B9A7FF" if i % 2 else "#8FFFE4"}" opacity="0.16" filter="url(#bblur)">'
    f'<animate attributeName="opacity" values="0.05;0.26;0.05" dur="{random.uniform(5, 9):.1f}s" '
    f'begin="-{random.uniform(0, 6):.1f}s" repeatCount="indefinite"/></circle>'
    for i in range(6)
)

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

spots = []
for i in range(3):
    c = ["#8FFFE4", "#B9A7FF", "#FFD9A0"][i]
    y = [140, 240, 340][i]
    dur = [19, 24, 27][i]
    r = [240, 210, 280][i]
    begin = [0, 7, 13][i]
    direction = 1 if i % 2 == 0 else -1
    x0 = -320 if direction == 1 else W + 320
    x1 = W + 320 if direction == 1 else -320
    spots.append(
        f'      <g><animateTransform attributeName="transform" type="translate" '
        f'values="{x0} 0; {x1} 0" dur="{dur}s" begin="-{begin}s" repeatCount="indefinite"/>'
        f'<ellipse cx="0" cy="{y}" rx="{r}" ry="{r * 0.6:.0f}" fill="{c}" opacity="0.2" filter="url(#sblur)">'
        f'<animate attributeName="opacity" values="0.06;0.26;0.06" dur="{dur / 3:.1f}s" begin="-{begin}s" repeatCount="indefinite"/>'
        f'</ellipse></g>'
    )
spots = "\n".join(spots)

streaks = []
for i in range(3):
    dur = [8, 11, 14][i]
    begin = [0, 3.5, 7][i]
    h = [9, 14, 7][i]
    c = ["#FFFFFF", "#B9A7FF", "#8FFFE4"][i]
    streaks.append(
        f'      <g><animateTransform attributeName="transform" type="translate" '
        f'values="0 -60; 0 {H + 60}" dur="{dur}s" begin="-{begin}s" repeatCount="indefinite"/>'
        f'<rect x="0" y="{i * 80}" width="{W}" height="{h}" fill="{c}" opacity="0.13" filter="url(#pblur)"/></g>'
    )
streaks = "\n".join(streaks)

# ---------- 3.5) 年度活动曲线（复刻自参考截图：深底面板 + 品红尖峰折线） ----------
CAL_QUERY = ("query($login:String!){user(login:$login){contributionsCollection{"
             "contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}")

# gh 不可用时的内置快照（生成于 2026-10-13，367 天）
FALLBACK_COUNTS = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 3, 0, 2, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
    0, 0, 0, 0, 5, 14, 3, 61, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 22, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 9, 0, 0, 0, 5, 9, 21,
    13, 5, 1, 21, 10, 25, 0, 5, 13, 20, 58, 29, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 3, 8, 0, 1, 4,
    0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 1, 10, 6, 3, 0, 20, 18, 18, 4, 0, 3, 3, 3, 0, 4,
    22, 79, 4, 1, 11, 1, 8, 8,
]


def fetch_counts() -> list:
    """优先实时拉取逐日贡献，失败则回退内置快照"""
    try:
        r = subprocess.run(
            ["gh", "api", "graphql", "-F", "login=Gorilla-Kevv", "-f", f"query={CAL_QUERY}"],
            capture_output=True, text=True, encoding="utf-8", timeout=45,
        )
        cal = json.loads(r.stdout)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        days = [d["contributionCount"] for w in cal["weeks"] for d in w["contributionDays"]]
        if len(days) < 300:
            raise ValueError(f"calendar too short: {len(days)}")
        print(f"curve data: LIVE gh api  ({len(days)} days, {sum(days)} contributions)")
        return days
    except Exception as e:                                    # noqa: BLE001
        print(f"[WARN] gh 实时拉取失败，使用内置快照: {e}")
        return FALLBACK_COUNTS


counts = fetch_counts()
CUR_TOTAL = sum(counts)
CUR_MAX = max(counts) or 1

# 几何：面板横贯顶部无文字区
CP_X, CP_Y, CP_W, CP_H = 24, 14, W - 48, 132
C_X0, C_X1 = CP_X + 20, CP_X + CP_W - 20
C_BASE, C_MAXH = CP_Y + 122, 74
step = (C_X1 - C_X0) / max(len(counts) - 1, 1)


def cy(c: int) -> float:
    """幂缩放：小数值也能看出起伏（0.55 次方），峰值顶满"""
    return C_BASE - (c / CUR_MAX) ** 0.55 * C_MAXH


pts = [(C_X0 + i * step, cy(c)) for i, c in enumerate(counts)]
d_line = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
d_fill = d_line + f" L{C_X1:.1f},{C_BASE} L{C_X0:.1f},{C_BASE} Z"
peak_i = counts.index(CUR_MAX)
pk_x, pk_y = pts[peak_i]

DRAW_DUR = 3.2
curve_parts = [
    # 面板底
    f'    <rect x="{CP_X}" y="{CP_Y}" width="{CP_W}" height="{CP_H}" rx="16" fill="#070B14" opacity="0.68" stroke="#FFFFFF" stroke-opacity="0.09"/>',
    # 标题行 + 总数 + 细分隔线（对应截图的「年度活动曲线：」与横线）
    f'    <text x="{CP_X + 20}" y="{CP_Y + 30}" fill="#F4F7FB" font-size="21" font-weight="bold" '
    f'font-family="\'Microsoft YaHei\',\'PingFang SC\',sans-serif" filter="url(#tshadow)">年度活动曲线'
    f'<tspan fill="#FF7FBC" font-size="15" font-weight="normal" dx="10">近一年 {CUR_TOTAL} 次 · 峰值 {CUR_MAX}/天</tspan></text>',
    f'    <line x1="{CP_X + 20}" y1="{CP_Y + 40}" x2="{CP_X + CP_W - 20}" y2="{CP_Y + 40}" stroke="#FFFFFF" stroke-opacity="0.10"/>',
    # 曲线下方渐隐填充（画完后淡入）
    f'    <path d="{d_fill}" fill="url(#curveFill)" opacity="0">'
    f'<animate attributeName="opacity" values="0;0;0.2" keyTimes="0;{0.4 + DRAW_DUR / 10:.2f};{0.4 + DRAW_DUR / 10 + 0.1:.2f}" '
    f'dur="10s" repeatCount="indefinite"/></path>',
    # 发光底层
    f'    <path d="{d_line}" fill="none" stroke="#FF5CA8" stroke-width="7" stroke-linejoin="round" '
    f'stroke-opacity="0.35" filter="url(#glow)" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">'
    f'<animate attributeName="stroke-dashoffset" values="1;0" begin="0.4s" dur="{DRAW_DUR}s" fill="freeze" '
    f'calcMode="spline" keySplines="0.3 0 0.2 1"/></path>',
    # 主线（自左向右描画，画完定格）
    f'    <path id="actCurve" d="{d_line}" fill="none" stroke="#FF5CA8" stroke-width="2.4" stroke-linejoin="round" '
    f'pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">'
    f'<animate attributeName="stroke-dashoffset" values="1;0" begin="0.4s" dur="{DRAW_DUR}s" fill="freeze" '
    f'calcMode="spline" keySplines="0.3 0 0.2 1"/></path>',
    # 峰值呼吸点
    f'    <circle cx="{pk_x:.1f}" cy="{pk_y:.1f}" r="3" fill="#FFD7EC" opacity="0">'
    f'<animate attributeName="opacity" values="0;0;0.95;0.45;0.95" '
    f'keyTimes="0;{0.4 + DRAW_DUR / 10:.2f};{0.4 + DRAW_DUR / 10 + 0.05:.2f};0.97;1" dur="10s" repeatCount="indefinite"/></circle>',
    # 巡游光点：沿曲线循环滑行
    f'    <circle cx="{C_X0:.1f}" cy="{C_BASE}" r="3.6" fill="#FFE3F1" filter="url(#glow)" opacity="0">'
    f'<animateMotion dur="9s" begin="3.6s" repeatCount="indefinite"><mpath xlink:href="#actCurve"/></animateMotion>'
    f'<animate attributeName="opacity" values="0;0.95;0.95;0" keyTimes="0;0.05;0.92;1" dur="9s" begin="3.6s" repeatCount="indefinite"/></circle>',
]
curve_layer = "\n".join(curve_parts)

# ---------- 4) 联系面板 ----------
HEAD = "来找我玩"
HEAD_FS = 38
SENT = "如果逛到这里，顺手给我个 ⭐ 吧，我会开心一整天 🥰"
SENT_FS = 23

head_w = text_w(HEAD, HEAD_FS)
head_icon_w = 30
head_total = head_icon_w + 14 + head_w
head_x = (W - head_total) / 2
head_y = 322

PILL_H = 42
PILL_R = PILL_H / 2
PILL_FS = 20
ICON = 22
PAD = 15
GAP = 10

BADGES = [
    # label, value, 主色, 标签色, 图标, 链接
    ("GitHub", "Gorilla-Kevv", "#24292f", "#181818", "github", "https://github.com/Gorilla-Kevv"),
    ("Bilibili", "Gorilla_Kev", "#00A1D6", "#0086b3", "bilibili", "https://space.bilibili.com/182698016"),
    ("网易云音乐人", "歌瑞沫拉菌", "#C20C0C", "#9c0a0a", "netease", "https://music.163.com/#/artist?id=49513294"),
    ("Email", "写在这儿", "#FF6B6B", "#e05555", "mail", "https://github.com/Gorilla-Kevv"),
]


def icon(name: str, x: float, y: float, size: float) -> str:
    """极简矢量品牌图标，size 为边长，x/y 为左上角"""
    s = size
    cx, cy = x + s / 2, y + s / 2
    if name == "github":                       # 猫头剪影
        return (
            f'<g fill="#FFFFFF"><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{s * 0.46:.1f}"/>'
            f'<path d="M{cx - s * 0.36:.1f},{cy - s * 0.30:.1f} L{cx - s * 0.20:.1f},{cy - s * 0.52:.1f} '
            f'L{cx - s * 0.04:.1f},{cy - s * 0.34:.1f} Z"/>'
            f'<path d="M{cx + s * 0.36:.1f},{cy - s * 0.30:.1f} L{cx + s * 0.20:.1f},{cy - s * 0.52:.1f} '
            f'L{cx + s * 0.04:.1f},{cy - s * 0.34:.1f} Z"/>'
            f'<circle cx="{cx:.1f}" cy="{cy + s * 0.10:.1f}" r="{s * 0.46:.1f}" fill="#181818"/></g>'
        )
    if name == "bilibili":                     # 电视机 + 天线
        return (
            f'<g stroke="#FFFFFF" stroke-width="{s * 0.11:.1f}" fill="none" stroke-linecap="round">'
            f'<path d="M{cx - s * 0.30:.1f},{cy - s * 0.34:.1f} L{cx - s * 0.12:.1f},{cy - s * 0.12:.1f}"/>'
            f'<path d="M{cx + s * 0.30:.1f},{cy - s * 0.34:.1f} L{cx + s * 0.12:.1f},{cy - s * 0.12:.1f}"/>'
            f'<rect x="{cx - s * 0.44:.1f}" y="{cy - s * 0.16:.1f}" width="{s * 0.88:.1f}" height="{s * 0.56:.1f}" rx="{s * 0.12:.1f}" fill="#FFFFFF" stroke="none"/>'
            f'<line x1="{cx - s * 0.16:.1f}" y1="{cy + s * 0.02:.1f}" x2="{cx - s * 0.16:.1f}" y2="{cy + s * 0.22:.1f}" stroke="#00A1D6" stroke-width="{s * 0.12:.1f}"/>'
            f'<line x1="{cx + s * 0.16:.1f}" y1="{cy + s * 0.02:.1f}" x2="{cx + s * 0.16:.1f}" y2="{cy + s * 0.22:.1f}" stroke="#00A1D6" stroke-width="{s * 0.12:.1f}"/>'
            f'</g>'
        )
    if name == "netease":                      # 音符
        return (
            f'<g fill="#FFFFFF">'
            f'<rect x="{cx - s * 0.06:.1f}" y="{cy - s * 0.46:.1f}" width="{s * 0.10:.1f}" height="{s * 0.62:.1f}" rx="{s * 0.05:.1f}"/>'
            f'<path d="M{cx - s * 0.04:.1f},{cy - s * 0.46:.1f} L{cx + s * 0.40:.1f},{cy - s * 0.34:.1f} '
            f'L{cx + s * 0.40:.1f},{cy - s * 0.16:.1f} L{cx - s * 0.04:.1f},{cy - s * 0.28:.1f} Z"/>'
            f'<ellipse cx="{cx - s * 0.24:.1f}" cy="{cy + s * 0.20:.1f}" rx="{s * 0.20:.1f}" ry="{s * 0.15:.1f}"/>'
            f'<ellipse cx="{cx + s * 0.20:.1f}" cy="{cy + s * 0.32:.1f}" rx="{s * 0.20:.1f}" ry="{s * 0.15:.1f}"/></g>'
        )
    # mail：信封
    return (
        f'<g fill="none" stroke="#FFFFFF" stroke-width="{s * 0.10:.1f}" stroke-linejoin="round">'
        f'<rect x="{cx - s * 0.44:.1f}" y="{cy - s * 0.30:.1f}" width="{s * 0.88:.1f}" height="{s * 0.60:.1f}" rx="{s * 0.10:.1f}"/>'
        f'<path d="M{cx - s * 0.40:.1f},{cy - s * 0.24:.1f} L{cx:.1f},{cy + s * 0.10:.1f} L{cx + s * 0.40:.1f},{cy - s * 0.24:.1f}"/></g>'
    )


pill_w = []
for label, value, _, _, _, _ in BADGES:
    pw = PAD + ICON + 8 + text_w(label, PILL_FS) + GAP + text_w(value, PILL_FS) + PAD
    pill_w.append(pw)

GAP_PILL = 18
total_w = sum(pill_w) + GAP_PILL * (len(BADGES) - 1)
px_cursor = (W - total_w) / 2
pill_y = 372

pills = []
for (label, value, main, dark, ico, href), pw in zip(BADGES, pill_w):
    x = px_cursor
    label_w = PAD + ICON + 8 + text_w(label, PILL_FS) + GAP / 2
    parts = [
        f'    <a xlink:href="{href}" href="{href}" target="_blank">',
        # 整块底色（右侧圆角）+ 左侧标签底色
        f'      <rect x="{x:.1f}" y="{pill_y}" width="{pw:.1f}" height="{PILL_H}" rx="{PILL_R}" fill="{main}" stroke="#FFFFFF" stroke-opacity="0.22" stroke-width="1"/>',
        f'      <rect x="{x:.1f}" y="{pill_y}" width="{label_w:.1f}" height="{PILL_H}" rx="{PILL_R}" fill="{dark}"/>',
        f'      <rect x="{x + label_w - PILL_R:.1f}" y="{pill_y}" width="{PILL_R}" height="{PILL_H}" fill="{dark}"/>',
        icon(ico, x + PAD, pill_y + (PILL_H - ICON) / 2, ICON),
        f'      <text x="{x + PAD + ICON + 8:.1f}" y="{pill_y + PILL_H / 2 + 7:.1f}" fill="#FFFFFF" font-size="{PILL_FS}" font-family="\'Segoe UI\',\'Microsoft YaHei\',sans-serif" font-weight="bold">{label}</text>',
        f'      <text x="{x + label_w + GAP / 2:.1f}" y="{pill_y + PILL_H / 2 + 7:.1f}" fill="#FFFFFF" font-size="{PILL_FS}" font-family="\'Segoe UI\',\'Microsoft YaHei\',sans-serif" font-weight="bold">{value}</text>',
        "    </a>",
    ]
    pills.append("\n".join(parts))
    px_cursor += pw + GAP_PILL
pill_layer = "\n".join(pills)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="stage footer with contact panel">
  <defs>
    <clipPath id="frame"><rect x="0" y="0" width="{W}" height="{H}" rx="22"/></clipPath>
    <filter id="pblur" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="1.6"/></filter>
    <filter id="bblur" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="9"/></filter>
    <filter id="sblur" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="42"/></filter>
    <filter id="tshadow" x="-40%" y="-40%" width="180%" height="180%">
      <feDropShadow dx="0" dy="2" stdDeviation="3.4" flood-color="#04121C" flood-opacity="0.9"/>
    </filter>
    <filter id="glow" x="-120%" y="-120%" width="340%" height="340%"><feGaussianBlur stdDeviation="3.2"/></filter>
    <linearGradient id="curveFill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FF5CA8" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="#FF5CA8" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="pulseGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#7FFFE0" stop-opacity="0.9"/>
      <stop offset="50%" stop-color="#B9A7FF" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#FFC7F0" stop-opacity="0.9"/>
    </linearGradient>
    <linearGradient id="titleGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#FFE7A3"/>
      <stop offset="45%" stop-color="#FFB3C7"/>
      <stop offset="100%" stop-color="#B9A7FF"/>
    </linearGradient>
    <linearGradient id="scrim" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#04121C" stop-opacity="0"/>
      <stop offset="45%" stop-color="#04121C" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="#04121C" stop-opacity="0.78"/>
    </linearGradient>
{"".join(chr(10) + "    " + f'<linearGradient id="cone{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{c}" stop-opacity="0.45"/><stop offset="45%" stop-color="{c}" stop-opacity="0.16"/><stop offset="100%" stop-color="{c}" stop-opacity="0"/></linearGradient>' for i, c in enumerate(BEAM_COLORS))}
  </defs>

  <g clip-path="url(#frame)">
    <!-- 舞台照片：宽度铺满、垂直居中裁切（人物保持画面中央） -->
    <image href="data:image/jpeg;base64,{b64}" x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"/>

    <g style="mix-blend-mode:screen">
{spots}
    </g>

    <g style="mix-blend-mode:screen">
{cones}
    </g>

    <g style="mix-blend-mode:screen">
{streaks}
    </g>

    <rect x="0" y="0" width="{W}" height="{H}" fill="url(#pulseGrad)" opacity="0" style="mix-blend-mode:screen">
      <animate attributeName="opacity" values="0;0.05;0.14;0.04;0.09;0" dur="4.8s" repeatCount="indefinite"/>
    </rect>

    <!-- 年度活动曲线面板 -->
{curve_layer}

    <!-- 文字区压暗，保证可读性 -->
    <rect x="0" y="150" width="{W}" height="{H - 150}" fill="url(#scrim)"/>

    <!-- 标题：来找我玩 -->
    <g filter="url(#tshadow)">
      <g transform="translate({head_x:.1f},{head_y - 22:.1f})">
        <rect x="0" y="2" width="{head_icon_w}" height="{head_icon_w * 0.72:.0f}" rx="5" fill="none" stroke="url(#titleGrad)" stroke-width="3"/>
        <path d="M2,4 L{head_icon_w / 2:.1f},{head_icon_w * 0.44:.1f} L{head_icon_w - 2:.0f},4" fill="none" stroke="url(#titleGrad)" stroke-width="3" stroke-linejoin="round"/>
      </g>
      <text x="{head_x + head_icon_w + 14:.1f}" y="{head_y}" fill="url(#titleGrad)" font-size="{HEAD_FS}" font-weight="bold"
            font-family="'Microsoft YaHei','PingFang SC','Segoe UI',sans-serif">{HEAD}</text>
    </g>

    <!-- 链接徽章 -->
{pill_layer}

    <!-- 句子 -->
    <text x="{W / 2}" y="466" text-anchor="middle" fill="#EAF6FF" font-size="{SENT_FS}" filter="url(#tshadow)"
          font-family="'Microsoft YaHei','PingFang SC','Segoe UI',sans-serif">{SENT}</text>

{bokeh}

{particles}
  </g>
</svg>
'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"written: {OUT}  size: {len(svg)} bytes  pills_width={total_w:.0f}")

import os
import re

readme = os.path.join(r"f:\schoolCompWorks\clone\gtihubMainPagePro", "README.md")
m = re.search(r"assets/(footer[^\"')\s]*\.svg)", open(readme, encoding="utf-8").read())
ref = m.group(1) if m else None
want = os.path.basename(OUT)
print(f"[{'OK' if ref == want else 'WARN'}] README 页脚引用: {ref} / 输出: {want}")
