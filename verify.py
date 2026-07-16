from playwright.sync_api import sync_playwright

def verify_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Intercept static assets and APIs
        def route_handler(route):
            url = route.request.url
            if url.endswith("/static/css/style.css"):
                with open("src/presentation/static/css/style.css", "rb") as f:
                    route.fulfill(body=f.read(), headers={"Content-Type": "text/css"})
            elif url.endswith("/static/js/app.js"):
                with open("src/presentation/static/js/app.js", "rb") as f:
                    route.fulfill(body=f.read(), headers={"Content-Type": "application/javascript"})
            elif "/api/v1/jobs" in url:
                route.fulfill(json={"jobs": []})
            elif "/api/v1/skills/provenance" in url:
                route.fulfill(json={"records": []})
            elif "/api/v1/skills" in url:
                route.fulfill(json={"skills": {}})
            else:
                route.continue_()

        page.route("**/*", route_handler)

        with open("src/presentation/templates/index.html", "r") as f:
            html = f.read()

        page.set_content(html)
        page.wait_for_load_state("networkidle")

        page.locator("#skills-container").focus()

        page.screenshot(path="verification.png")
        browser.close()

if __name__ == "__main__":
    verify_frontend()
