from playwright.sync_api import sync_playwright

from main import PRODUCT_URL, TARGET_SIZE, accept_cookies


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(
        PRODUCT_URL,
        wait_until="domcontentloaded",
        timeout=60_000,
    )

    accept_cookies(page)

    size_input = page.locator(
        f'input[name="swatch-size-text"][data-option-label="{TARGET_SIZE}"]'
    )

    size_input.wait_for(
        state="attached",
        timeout=10_000,
    )

    print("\nINPUT:")
    print(
        size_input.evaluate(
            "(el) => el.outerHTML"
        )
    )

    print("\nPARENT:")
    print(
        size_input.evaluate(
            "(el) => el.parentElement.outerHTML"
        )
    )

    print("\nGRANDPARENT:")
    print(
        size_input.evaluate(
            "(el) => el.parentElement.parentElement.outerHTML"
        )
    )

    browser.close()