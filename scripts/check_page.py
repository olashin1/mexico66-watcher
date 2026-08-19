from playwright.sync_api import sync_playwright
from main import PRODUCT_URL

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(
        PRODUCT_URL,
        wait_until="domcontentloaded",
        timeout=60_000,
    )

    print("Title:", page.title())
    print("URL:", page.url)

    browser.close()