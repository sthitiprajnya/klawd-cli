import os
from playwright.sync_api import sync_playwright

def run_cuj(page):
    def handle_css(route):
        with open('src/presentation/static/css/style.css', 'r') as f:
            route.fulfill(body=f.read(), headers={'Content-Type': 'text/css'})
    def handle_js(route):
        with open('src/presentation/static/js/app.js', 'r') as f:
            route.fulfill(body=f.read(), headers={'Content-Type': 'application/javascript'})

    page.route('**/static/css/style.css', handle_css)
    page.route('**/static/js/app.js', handle_js)
    page.route('**/api/v1/**', lambda route: route.fulfill(json={}))

    html_content = open('src/presentation/templates/index.html', 'r').read()
    page.set_content(html_content)
    page.wait_for_timeout(500)

    # tab navigate to the first scrollable pre block
    page.keyboard.press("Tab")
    page.wait_for_timeout(500)

    # tab navigate to the second scrollable pre block
    page.keyboard.press("Tab")
    page.wait_for_timeout(500)

    page.screenshot(path="/app/verification/screenshots/verification.png")
    page.wait_for_timeout(1000)

if __name__ == "__main__":
    os.makedirs("/app/verification/screenshots", exist_ok=True)
    os.makedirs("/app/verification/videos", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="/app/verification/videos"
        )
        page = context.new_page()
        try:
            run_cuj(page)
        finally:
            context.close()
            browser.close()