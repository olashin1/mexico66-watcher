from playwright.sync_api import sync_playwright

from main import PRODUCT_URL, accept_cookies


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(
        PRODUCT_URL,
        wait_until="domcontentloaded",
        timeout=60_000,
    )

    accept_cookies(page)

    sizes = page.locator(
        'input[name="swatch-size-text"]'
    )

    try:
        sizes.first.wait_for(
            state="attached",
            timeout=10_000,
        )
    except Exception:
        print("No size inputs appeared.")
        browser.close()
        raise SystemExit

    print(f"Found {sizes.count()} size options.\n")

    for i in range(sizes.count()):
        size = sizes.nth(i)

        try:
            label = size.get_attribute(
                "data-option-label"
            )

            print(
                f"Size: {label} | "
                f"disabled={size.is_disabled()} | "
                f"aria-disabled={size.get_attribute('aria-disabled')} | "
                f"class={size.get_attribute('class')}"
            )

        except Exception as error:
            print(
                f"Error reading size {i}: {error}"
            )

    browser.close()