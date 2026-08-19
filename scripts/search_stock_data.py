from playwright.sync_api import sync_playwright

from main import PRODUCT_URL, accept_cookies


SEARCH_TERMS = [
    "2640",
    "salable",
    "is_salable",
    "stock_status",
    "stockstatus",
    "inventory",
    "availability",
    "available",
]


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(
        PRODUCT_URL,
        wait_until="domcontentloaded",
        timeout=60_000,
    )

    accept_cookies(page)

    page.wait_for_timeout(3000)

    html = page.content()

    for term in SEARCH_TERMS:
        index = html.lower().find(term.lower())

        print(f"\n{term}: {index}")

        if index != -1:
            print(
                html[
                    max(0, index - 500):
                    index + 1500
                ]
            )

    browser.close()