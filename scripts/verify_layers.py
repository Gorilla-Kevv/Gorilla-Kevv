from playwright.sync_api import sync_playwright

URL = "file:///f:/schoolCompWorks/clone/gtihubMainPagePro/build/anim_v11.html"
OUT = "f:/schoolCompWorks/clone/gtihubMainPagePro/build/"

# 12s 一轮：起稿 0.4-1.8s / 底色 2.0-2.5s / 皮肤 2.5-3.0s / 眼睛 3.1-3.5s
#            细节 3.6-4.2s / 成图 4.2-6.2s / 马赛克 6.0-7.0s / 飞出 7.7-9.7s / 清场 9.7-12s
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    # 每次都新开页面只等一次，避免截图耗时累积
    for t in (1200, 2300, 2900, 3400, 4100, 5200, 7000, 9000, 10800):
        pg = b.new_page(viewport={"width": 1060, "height": 780})
        pg.goto(URL)
        pg.wait_for_timeout(t)
        pg.locator("#hero").screenshot(path=f"{OUT}v7_t{t}.png")
        pg.close()
        print(f"captured t={t / 1000:.1f}s")
    b.close()
