from playwright.sync_api import sync_playwright

from main import PRODUCT_URL, accept_cookies


TARGET_OPTION_ID = "2640"


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(
        PRODUCT_URL,
        wait_until="domcontentloaded",
        timeout=60_000,
    )

    accept_cookies(page)

    scripts = page.locator("script")

    print(f"Found {scripts.count()} script tags.\n")

    matches = 0

    for i in range(scripts.count()):
        script = scripts.nth(i)

        try:
            content = script.text_content() or ""

            if TARGET_OPTION_ID not in content:
                continue

            matches += 1

            index = content.find(TARGET_OPTION_ID)

            start = max(0, index - 1000)
            end = min(len(content), index + 2000)

            print(f"\n--- MATCH {matches} ---")
            print(content[start:end])

        except Exception:
            continue

    print(f"\nTotal matches: {matches}")

    browser.close()