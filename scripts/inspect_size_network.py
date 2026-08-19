from playwright.sync_api import sync_playwright

from main import PRODUCT_URL, TARGET_SIZE, accept_cookies


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    def log_response(response):
        resource_type = response.request.resource_type

        if resource_type in ("xhr", "fetch"):
            print("\n--- NETWORK RESPONSE ---")
            print("Type:", resource_type)
            print("Status:", response.status)
            print("URL:", response.url)

            try:
                content_type = response.headers.get("content-type", "")

                if "json" in content_type:
                    print("JSON:")
                    print(response.json())
            except Exception:
                pass

    page.on("response", log_response)

    page.goto(
        PRODUCT_URL,
        wait_until="domcontentloaded",
        timeout=60_000,
    )

    accept_cookies(page)

    size = page.locator(
        f'input[name="swatch-size-text"][data-option-label="{TARGET_SIZE}"]'
    )

    size.wait_for(
        state="attached",
        timeout=10_000,
    )

    print("\nTarget size found.")
    print("Option ID:", size.get_attribute("data-option-id"))

    print("\nTriggering size selection...")

    size.evaluate(
        """
        el => {
            el.checked = true;

            el.dispatchEvent(
                new Event("input", {
                    bubbles: true
                })
            );

            el.dispatchEvent(
                new Event("change", {
                    bubbles: true
                })
            );

            el.click();
        }
        """
    )

    page.wait_for_timeout(5000)

    print("\nChecked:", size.is_checked())

    input("\nPress Enter to close...")

    browser.close()