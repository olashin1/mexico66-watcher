from playwright.sync_api import sync_playwright

from main import PRODUCT_URL, TARGET_SIZE, accept_cookies


IGNORE_DOMAINS = [
    "google-analytics.com",
    "googlesyndication.com",
    "nr-data.net",
    "onetrust.com",
    "adobedc.net",
    "global-e.com",
]


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

    requests = []

    def capture_request(request):
        if request.resource_type not in ("xhr", "fetch"):
            return

        if any(domain in request.url for domain in IGNORE_DOMAINS):
            return

        requests.append(request)

    page.on("request", capture_request)

    add_to_bag = page.get_by_role(
        "button",
        name="ADD TO BAG",
    )

    print("Add to Bag visible:", add_to_bag.is_visible())
    print("Add to Bag disabled:", add_to_bag.is_disabled())

    print("\nClicking Add to Bag...")

    add_to_bag.click()

    page.wait_for_timeout(5000)

    print("\nRequests:")

    if not requests:
        print("No relevant requests detected.")

    for request in requests:
        print("\n------------------------------")
        print("Method:", request.method)
        print("URL:", request.url)

        if request.post_data:
            print("Body:", request.post_data)

    print("\nPossible stock messages:")

    body_text = page.locator("body").inner_text().lower()

    for keyword in [
        "out of stock",
        "sold out",
        "unavailable",
        "added to your shopping cart",
        "added to bag",
    ]:
        if keyword in body_text:
            print("FOUND:", keyword)

    input("\nPress Enter to close...")

    browser.close()