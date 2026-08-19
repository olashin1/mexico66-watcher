from playwright.sync_api import sync_playwright

from main import check_stock


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    result = check_stock(page)

    print("\nFinal result:", result)

    browser.close()