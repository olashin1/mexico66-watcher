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

    input_id = size_input.get_attribute("id")

    size_label = page.locator(
        f'label[for="{input_id}"]'
    )

    print("Before click:")
    print("checked:", size_input.is_checked())
    print("disabled:", size_input.is_disabled())

    print("\nLabel:")
    print("visible:", size_label.is_visible())
    print("html:", size_label.evaluate("(el) => el.outerHTML"))

    size_label.click(force=True)

    page.wait_for_timeout(1000)

    print("\nAfter click:")
    print("checked:", size_input.is_checked())
    print("disabled:", size_input.is_disabled())

    print("\nVisible buttons:")

    buttons = page.locator("button")

    for i in range(buttons.count()):
        button = buttons.nth(i)

        try:
            if not button.is_visible():
                continue

            text = button.inner_text().strip()

            if not text:
                continue

            print(
                repr(text),
                "| disabled=",
                button.is_disabled(),
                "| class=",
                button.get_attribute("class"),
            )

        except Exception:
            continue

    input("\nPress Enter to close...")

    browser.close()