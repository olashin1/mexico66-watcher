import sys

from playwright.sync_api import sync_playwright

from main import accept_cookies


if len(sys.argv) != 3:
    print(
        "Usage: python -m scripts.test_in_stock "
        '"<product_url>" "<size>"'
    )
    raise SystemExit(1)


product_url = sys.argv[1]
target_size = sys.argv[2]


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    print(f"\nTesting size {target_size}")

    page.goto(
        product_url,
        wait_until="domcontentloaded",
        timeout=60_000,
    )

    accept_cookies(page)

    size = page.locator(
        f'input[name="swatch-size-text"]'
        f'[data-option-label="{target_size}"]'
    )

    size.wait_for(
        state="attached",
        timeout=10_000,
    )

    size.evaluate(
        """
        el => {
            el.checked = true;

            el.dispatchEvent(
                new Event("input", { bubbles: true })
            );

            el.dispatchEvent(
                new Event("change", { bubbles: true })
            );

            el.click();
        }
        """
    )

    print("Selected:", size.is_checked())

    add_to_bag = page.get_by_role(
        "button",
        name="ADD TO BAG",
    )

    print("Clicking Add to Bag...")

    add_to_bag.click()

    print("\nWatching page for 60 seconds...\n")

    try:
        result = page.wait_for_function(
            """
            () => {
                const body =
                    document.body.innerText.toLowerCase();

                if (
                    body.includes(
                        "requested qty is not available"
                    )
                ) {
                    return "out_of_stock";
                }

                const cartCount =
                    document.querySelector(
                        ".showcart .counter-number"
                    );

                if (
                    cartCount &&
                    cartCount.textContent.trim() &&
                    cartCount.textContent.trim() !== "0"
                ) {
                    return "cart_updated";
                }

                return false;
            }
            """,
            timeout=60_000,
        )

        status = result.json_value()

        if status == "out_of_stock":
            print("RESULT: OUT OF STOCK")

        elif status == "cart_updated":
            print("RESULT: CART UPDATED")
            print("This looks like our IN STOCK signal.")

    except Exception:
        print("RESULT: UNKNOWN")

    print("\nVisible Magento messages:")

    messages = page.locator(
        ".message, .messages, [role='alert']"
    )

    for i in range(messages.count()):
        try:
            text = messages.nth(i).inner_text().strip()

            if text:
                print(repr(text))

        except Exception:
            pass

    print("\nCart HTML:")

    try:
        cart = page.get_by_role(
            "button",
            name="My Cart",
        )

        print(
            cart.evaluate(
                "(el) => el.outerHTML"
            )
        )

    except Exception:
        print("Could not inspect cart.")

    input("\nPress Enter to close...")

    browser.close()