from playwright.sync_api import sync_playwright

URL = "file:///f:/schoolCompWorks/clone/gtihubMainPagePro/build/anim_v5.html"
OUT = "f:/schoolCompWorks/clone/gtihubMainPagePro/build/"

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    pg = b.new_page(viewport={"width": 1060, "height": 760})
    pg.goto(URL)

    marks = [2000, 4900, 7200, 11000]
    prev = 0
    for i, t in enumerate(marks):
        pg.wait_for_timeout(t - prev)
        prev = t
        pg.screenshot(path=f"{OUT}v5_t{t}.png")
        print(f"captured t={t / 1000:.1f}s")
    b.close()
