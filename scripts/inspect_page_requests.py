from playwright.sync_api import sync_playwright

from main import PRODUCT_URL


KEYWORDS = [
    "stock",
    "inventory",
    "availability",
    "product",
    "graphql",
    "rest",
    "configurable",
]


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    def inspect_response(response):
        url = response.url.lower()

        if not any(keyword in url for keyword in KEYWORDS):
            return

        print("\n------------------------------")
        print("Status:", response.status)
        print("Type:", response.request.resource_type)
        print("URL:", response.url)

        try:
            content_type = response.headers.get(
                "content-type",
                ""
            )

            if "json" in content_type:
                print("JSON:")
                print(response.json())

        except Exception:
            pass

    page.on("response", inspect_response)

    page.goto(
        PRODUCT_URL,
        wait_until="networkidle",
        timeout=60_000,
    )

    input("\nPress Enter to close...")

    browser.close()