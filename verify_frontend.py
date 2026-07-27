from playwright.sync_api import sync_playwright
import os

def run_cuj(page):
    page.route("**/api/v1/**", lambda route: route.fulfill(json={}))

    html_path = f"file://{os.path.abspath('src/presentation/templates/index.html')}"
    page.goto(html_path)
    page.wait_for_timeout(1000)

    with open('src/presentation/static/css/style.css', 'r') as f:
        page.add_style_tag(content=f.read())
    page.wait_for_timeout(1000)

    # Tab to focus on the pre containers to verify tabindex="0" and visual focus
    page.keyboard.press("Tab")
    page.wait_for_timeout(500)
    page.keyboard.press("Tab")
    page.wait_for_timeout(500)

    page.screenshot(path="/app/verification/screenshots/verification.png")
    page.wait_for_timeout(1000)

if __name__ == "__main__":
    os.makedirs("/app/verification/videos", exist_ok=True)
    os.makedirs("/app/verification/screenshots", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(record_video_dir="/app/verification/videos")
        page = context.new_page()
        try:
            run_cuj(page)
        finally:
            context.close()
            browser.close()