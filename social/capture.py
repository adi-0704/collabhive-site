import pathlib
from playwright.sync_api import sync_playwright

here = pathlib.Path(__file__).parent.resolve()
html_path = here / "ig-50-creators.html"
out_path = here / "ig-50-creators.png"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
    page.goto(html_path.as_uri())
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(800)
    page.screenshot(path=str(out_path))
    browser.close()

print(f"saved -> {out_path}")
