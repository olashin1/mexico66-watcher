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

    page.wait_for_timeout(2000)

    label = page.locator(
        "label.size-option-label",
        has_text=TARGET_SIZE,
    )

    print("Labels found:", label.count())

    if label.count() == 0:
        browser.close()
        raise SystemExit("Target size label not found")

    input_id = label.first.get_attribute("for")

    print("Target ID:", input_id)

    target = page.locator(f"#{input_id}")

    print("Target elements:", target.count())

    if target.count() > 0:
        element = target.first

        print("\nVisible:", element.is_visible())
        print("Disabled:", element.is_disabled())
        print("Tag:", element.evaluate("(el) => el.tagName"))
        print("Class:", element.get_attribute("class"))
        print("Value:", element.get_attribute("value"))
        print("Aria disabled:", element.get_attribute("aria-disabled"))

        print("\nHTML:")
        print(
            element.evaluate(
                "(el) => el.outerHTML"
            )
        )

    browser.close()