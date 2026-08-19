import time

from playwright.sync_api import sync_playwright

from main import PRODUCT_URL, accept_cookies


TEST_SIZES = [
    "27.5",
    "28.0",
    "28.5",
]


def test_size(page, size_label):
    print(f"\n===== Testing size {size_label} =====")

    page.goto(
        PRODUCT_URL,
        wait_until="domcontentloaded",
        timeout=60_000,
    )

    accept_cookies(page)

    size = page.locator(
        f'input[name="swatch-size-text"]'
        f'[data-option-label="{size_label}"]'
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

    error = page.get_by_text(
        "The requested qty is not available",
        exact=False,
    )

    start = time.perf_counter()

    add_to_bag.click()

    try:
        error.wait_for(
            state="visible",
            timeout=60_000,
        )

        elapsed = time.perf_counter() - start

        print("OUT OF STOCK")
        print(f"Error appeared after {elapsed:.2f} seconds")

    except Exception:
        elapsed = time.perf_counter() - start

        print(
            f"No error detected after {elapsed:.2f} seconds"
        )


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    for size_label in TEST_SIZES:
        test_size(page, size_label)

    browser.close()