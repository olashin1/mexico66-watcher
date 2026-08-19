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

    size = page.locator(
        f'input[name="swatch-size-text"][data-option-label="{TARGET_SIZE}"]'
    )

    size.wait_for(
        state="attached",
        timeout=10_000,
    )

    size.evaluate(
        """
        el => {
            el.checked = true;
            el.dispatchEvent(new Event("input", { bubbles: true }));
            el.dispatchEvent(new Event("change", { bubbles: true }));
            el.click();
        }
        """
    )

    print("Selected:", size.is_checked())

    def inspect_response(response):
        if "/checkout/cart/add/" not in response.url:
            return

        print("\n--- CART RESPONSE ---")
        print("Status:", response.status)
        print("URL:", response.url)

        try:
            print("Content-Type:", response.headers.get("content-type"))

            body = response.text()

            print("\nResponse body:")
            print(body[:5000])

        except Exception as error:
            print("Could not read response:", error)

    page.on("response", inspect_response)

    add_to_bag = page.get_by_role(
        "button",
        name="ADD TO BAG",
    )

    print("\nClicking Add to Bag...")

    add_to_bag.click()

    page.wait_for_timeout(5000)

    print("\nPage messages:")

    messages = page.locator(
        ".message, "
        ".messages, "
        "[role='alert']"
    )

    for i in range(messages.count()):
        message = messages.nth(i)

        try:
            text = message.inner_text().strip()

            if text:
                print(repr(text))

        except Exception:
            pass

    input("\nPress Enter to close...")

    browser.close()