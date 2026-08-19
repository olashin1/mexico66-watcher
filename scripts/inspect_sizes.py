from playwright.sync_api import sync_playwright
from main import PRODUCT_URL, TARGET_SIZE

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(
        PRODUCT_URL,
        wait_until="domcontentloaded",
        timeout=60_000,
    )

    page.wait_for_timeout(3000)

    elements = page.locator(
        "button, label, [role='button'], option, input"
    )

    print("Elements found:", elements.count())

    for i in range(elements.count()):
        element = elements.nth(i)

        try:
            if not element.is_visible():
                continue

            text = element.inner_text().strip()
            value = element.get_attribute("value") or ""
            aria = element.get_attribute("aria-label") or ""

            combined = f"{text} {value} {aria}"

            if TARGET_SIZE in combined:
                print("\nTARGET SIZE FOUND")
                print("Text:", text)
                print("Value:", value)
                print("Aria:", aria)
                print("Class:", element.get_attribute("class"))
                print("Disabled:", element.is_disabled())

        except Exception:
            continue

    browser.close()