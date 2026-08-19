from playwright.sync_api import sync_playwright

from main import PRODUCT_URL, TARGET_SIZE, accept_cookies


IGNORE_DOMAINS = [
    "google-analytics.com",
    "googlesyndication.com",
    "nr-data.net",
    "onetrust.com",
    "adobedc.net",
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

    print("Target size:", TARGET_SIZE)
    print("Option ID:", size.get_attribute("data-option-id"))

    requests = []

    def capture_request(request):
        if request.resource_type not in ("xhr", "fetch"):
            return

        if any(domain in request.url for domain in IGNORE_DOMAINS):
            return

        requests.append(request)

    page.on("request", capture_request)

    print("\nSelecting size...")

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

    page.wait_for_timeout(5000)

    print("\nChecked:", size.is_checked())

    print("\nRequests after selection:")

    if not requests:
        print("No relevant XHR/fetch requests detected.")

    for request in requests:
        print("\n------------------------------")
        print("Method:", request.method)
        print("URL:", request.url)

        if request.post_data:
            print("Body:", request.post_data)

    input("\nPress Enter to close...")

    browser.close()