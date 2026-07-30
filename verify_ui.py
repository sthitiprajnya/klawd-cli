from playwright.sync_api import sync_playwright

def mock_api(route):
    if '/api/v1/jobs' in route.request.url:
        route.fulfill(json={"jobs": [{"job_id": "job123", "task": "Test task", "status": "completed"}]})
    elif '/api/v1/skills/provenance' in route.request.url:
        route.fulfill(json={"records": [{"id": 1, "source": "github"}]})
    elif '/api/v1/skills' in route.request.url:
        route.fulfill(json={"skills": [{"name": "test_skill", "version": "1.0.0"}]})
    else:
        route.continue_()

def serve_css(route):
    css_path = "/app/src/presentation/static/css/style.css"
    with open(css_path, "rb") as f:
        route.fulfill(body=f.read(), headers={'Content-Type': 'text/css'})

def serve_js(route):
    js_path = "/app/src/presentation/static/js/app.js"
    with open(js_path, "rb") as f:
        route.fulfill(body=f.read(), headers={'Content-Type': 'application/javascript'})

def run_cuj(page):
    page.route('**/api/v1/**', mock_api)
    page.route('**/static/css/style.css', serve_css)
    page.route('**/static/js/app.js', serve_js)

    html_path = "file:///app/src/presentation/templates/index.html"
    page.goto(html_path)
    page.wait_for_timeout(1000)

    # Focus the skills container to demonstrate keyboard accessibility
    page.locator("#skills-container").focus()
    page.wait_for_timeout(500)

    page.screenshot(path="./screenshot.png")
    page.wait_for_timeout(1000)

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(record_video_dir="./videos")
        page = context.new_page()
        try:
            run_cuj(page)
        finally:
            context.close()
            browser.close()