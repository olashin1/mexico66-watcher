from playwright.sync_api import sync_playwright

from main import PRODUCT_URL, accept_cookies


TEST_SIZES = [
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
            el.dispatchEvent(new Event("input", { bubbles: true }));
            el.dispatchEvent(new Event("change", { bubbles: true }));
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

    result = page.wait_for_function(
        """
        () => {
            const body = document.body.innerText.toLowerCase();

            if (body.includes("requested qty is not available")) {
                return "out_of_stock";
            }

            const counter = document.querySelector(
                ".showcart .counter-number"
            );

            if (
                counter &&
                counter.textContent.trim() &&
                counter.textContent.trim() !== "0"
            ) {
                return "in_stock";
            }

            return false;
        }
        """,
        timeout=20_000,
    )

    status = result.json_value()

    if status == "out_of_stock":
        print("RESULT: OUT OF STOCK")
        return False

    if status == "in_stock":
        print("RESULT: IN STOCK")
        return True

    print("RESULT: UNKNOWN")
    return None


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    for size_label in TEST_SIZES:
        try:
            test_size(page, size_label)
        except Exception:
            print("RESULT: UNKNOWN / TIMED OUT")

    browser.close()