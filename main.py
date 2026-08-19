import json
import logging
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright


# ============================================================
# Configuration
# ============================================================

load_dotenv()

PRODUCT_URL = os.getenv("PRODUCT_URL")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

TARGET_SIZE = "28.5"
PRODUCT_NAME = "Onitsuka Tiger Mexico 66 Black/White"

CHECK_INTERVAL = int(
    os.getenv("CHECK_INTERVAL", "300")
)

STATE_FILE = Path("state.json")


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


# ============================================================
# Persistent state
# ============================================================

def load_state() -> bool:
    """Load the previous stock state."""

    if not STATE_FILE.exists():
        return False

    try:
        data = json.loads(
            STATE_FILE.read_text()
        )

        return bool(
            data.get("in_stock", False)
        )

    except (json.JSONDecodeError, OSError):
        return False


def save_state(in_stock: bool) -> None:
    """Save the current stock state."""

    STATE_FILE.write_text(
        json.dumps(
            {
                "in_stock": in_stock
            },
            indent=2,
        )
    )


# ============================================================
# Discord
# ============================================================

def send_discord_notification() -> None:
    """Send a restock notification to Discord."""

    payload = {
        "content": (
            "🚨 **RESTOCK ALERT** 🚨\n\n"
            f"**{PRODUCT_NAME}**\n"
            f"Size **{TARGET_SIZE} cm** is back in stock!\n\n"
            f"{PRODUCT_URL}"
        )
    }

    response = requests.post(
        DISCORD_WEBHOOK_URL,
        json=payload,
        timeout=15,
    )

    response.raise_for_status()

    logging.info(
        "Discord notification sent successfully."
    )


# ============================================================
# Stock detection
# ============================================================

def check_stock(page) -> bool:
    """
    Check whether size 28.5 appears to be available.
    """

    logging.info(
        "Opening product page..."
    )

    page.goto(
        PRODUCT_URL,
        wait_until="domcontentloaded",
        timeout=60_000,
    )

    # Give JavaScript time to render the product.
    page.wait_for_timeout(3_000)

    logging.info(
        "Looking for size %s...",
        TARGET_SIZE,
    )

    elements = page.locator(
        "button, "
        "label, "
        "[role='button'], "
        "option, "
        "input"
    )

    for i in range(elements.count()):

        element = elements.nth(i)

        try:

            if not element.is_visible():
                continue

            text = (
                element.inner_text()
                .strip()
                .lower()
            )

            value = (
                element.get_attribute("value")
                or ""
            ).strip().lower()

            aria_label = (
                element.get_attribute(
                    "aria-label"
                )
                or ""
            ).strip().lower()

            class_name = (
                element.get_attribute("class")
                or ""
            ).lower()

            combined = " ".join(
                [
                    text,
                    value,
                    aria_label,
                ]
            )

            # Is this the 28.5 size?
            if TARGET_SIZE not in combined:
                continue

            logging.info(
                "Found size element: %r",
                combined,
            )

            # ----------------------------------------------
            # Disabled checks
            # ----------------------------------------------

            if element.is_disabled():

                logging.info(
                    "Size %s is disabled.",
                    TARGET_SIZE,
                )

                return False

            if (
                element.get_attribute(
                    "disabled"
                )
                is not None
            ):

                logging.info(
                    "Size %s has disabled attribute.",
                    TARGET_SIZE,
                )

                return False

            if (
                element.get_attribute(
                    "aria-disabled"
                )
                == "true"
            ):

                logging.info(
                    "Size %s is aria-disabled.",
                    TARGET_SIZE,
                )

                return False

            # ----------------------------------------------
            # Common unavailable classes
            # ----------------------------------------------

            unavailable_classes = [
                "disabled",
                "unavailable",
                "out-of-stock",
                "outofstock",
                "sold-out",
                "soldout",
            ]

            if any(
                word in class_name
                for word in unavailable_classes
            ):

                logging.info(
                    "Size %s appears unavailable.",
                    TARGET_SIZE,
                )

                return False

            # If the size exists and isn't disabled,
            # consider it available.

            logging.info(
                "🎉 Size %s appears AVAILABLE!",
                TARGET_SIZE,
            )

            return True

        except Exception:
            # The page can change while we're examining it.
            continue

    logging.warning(
        "Could not determine availability for size %s.",
        TARGET_SIZE,
    )

    return False


# ============================================================
# Configuration validation
# ============================================================

def validate_config() -> None:

    required = {
        "PRODUCT_URL": PRODUCT_URL,
        "DISCORD_WEBHOOK_URL": DISCORD_WEBHOOK_URL,
    }

    missing = [
        name
        for name, value in required.items()
        if not value
    ]

    if missing:

        raise RuntimeError(
            "Missing environment variables:\n"
            + "\n".join(
                f"  - {name}"
                for name in missing
            )
        )


# ============================================================
# Main watcher
# ============================================================

def main() -> None:

    validate_config()

    previous_stock = load_state()

    logging.info("=" * 60)
    logging.info(
        "Onitsuka Tiger Stock Watcher"
    )
    logging.info("=" * 60)
    logging.info(
        "Product: %s",
        PRODUCT_NAME,
    )
    logging.info(
        "Size: %s cm",
        TARGET_SIZE,
    )
    logging.info(
        "Check interval: %s seconds",
        CHECK_INTERVAL,
    )
    logging.info("=" * 60)

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        try:

            while True:

                try:

                    logging.info(
                        "Checking stock..."
                    )

                    current_stock = check_stock(
                        page
                    )

                    status = (
                        "IN STOCK"
                        if current_stock
                        else "OUT OF STOCK"
                    )

                    logging.info(
                        "Mexico 66 Black/White | "
                        "Size %s | %s",
                        TARGET_SIZE,
                        status,
                    )

                    # --------------------------------------
                    # Restock detection
                    # --------------------------------------
                    #
                    # Only send a notification when:
                    #
                    # OUT OF STOCK
                    #       ↓
                    #   IN STOCK
                    #
                    # This prevents repeated Discord
                    # notifications every 5 minutes.
                    # --------------------------------------

                    if (
                        current_stock
                        and not previous_stock
                    ):

                        logging.info(
                            "🚨 RESTOCK DETECTED!"
                        )

                        send_discord_notification()

                    save_state(
                        current_stock
                    )

                    previous_stock = (
                        current_stock
                    )

                except Exception:

                    logging.exception(
                        "Error while checking stock."
                    )

                logging.info(
                    "Next check in %s seconds...",
                    CHECK_INTERVAL,
                )

                time.sleep(
                    CHECK_INTERVAL
                )

        finally:

            browser.close()


if __name__ == "__main__":
    main()