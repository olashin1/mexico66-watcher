import json
import logging
import os
import time
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import httpx
from dotenv import load_dotenv


load_dotenv()

PRODUCT_URL = os.getenv("PRODUCT_URL")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

TARGET_SIZE = "28.5"
PRODUCT_NAME = "Onitsuka Tiger Mexico 66 Black/White"
CHECK_INTERVAL = max(int(os.getenv("CHECK_INTERVAL", "900")), 300)
MAX_ATTEMPTS = 3
RETRY_DELAYS = (5, 15)
STATE_FILE = Path("state.json")

GLOBAL_E_DATA = json.dumps(
    {
        "countryISO": "US",
        "currencyCode": "USD",
        "cultureCode": "en-US",
        "isOperatedByGlobalE": True,
        "isSupportsFixedPrice": False,
    },
    separators=(",", ":"),
)

STORE_COOKIES = {
    "GlobalE_Data": GLOBAL_E_DATA,
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def load_state():
    if not STATE_FILE.exists():
        return None

    try:
        value = json.loads(STATE_FILE.read_text()).get("in_stock")
    except (json.JSONDecodeError, OSError):
        return None

    return value if isinstance(value, bool) else None


def save_state(in_stock):
    STATE_FILE.write_text(json.dumps({"in_stock": in_stock}))


def product_sku(product_url):
    filename = Path(urlsplit(product_url).path).stem

    if not filename:
        raise ValueError("PRODUCT_URL does not contain a product SKU.")

    return filename.upper()


def stock_endpoint(product_url):
    parts = urlsplit(product_url)
    path_parts = parts.path.strip("/").split("/")

    if len(path_parts) < 3 or path_parts[2] != "product":
        raise ValueError("PRODUCT_URL is not an Onitsuka product-page URL.")

    path = f"/{path_parts[0]}/{path_parts[1]}/mobilestock/index/stock"

    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            path,
            "",
            "",
        )
    )


def retry_delay(response, attempt):
    if response is not None and response.status_code == 429:
        try:
            return max(
                float(response.headers.get("Retry-After", "0")),
                60,
            )
        except ValueError:
            return 60

    return RETRY_DELAYS[attempt]


def create_client():
    timeout = httpx.Timeout(
        20,
        connect=10,
    )

    return httpx.Client(
        timeout=timeout,
        follow_redirects=True,
        cookies=STORE_COOKIES,
    )


def check_stock(product_url, target_size, client=None):
    """Return True, False, or None when the response cannot be trusted."""

    if client is None:
        with create_client() as temporary_client:
            return check_stock(
                product_url,
                target_size,
                temporary_client,
            )

    sku = f"{product_sku(product_url)}_{target_size}"
    endpoint = stock_endpoint(product_url)

    headers = {
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": product_url,
        "User-Agent": "mexico66-watcher/1.0",
    }

    for attempt in range(MAX_ATTEMPTS):
        response = None

        try:
            response = client.get(
                endpoint,
                params={
                    "isAjax": "1",
                    "skus": sku,
                },
                headers=headers,
            )

            if response.is_success:
                data = response.json()

                stock = data.get("stock", {}).get(sku)

                value = (
                    stock.get("value")
                    if isinstance(stock, dict)
                    else None
                )

                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                ):
                    logging.warning(
                        "Stock response did not contain "
                        "a numeric value for %s.",
                        sku,
                    )
                    return None

                logging.info(
                    "%s reports inventory value %s for %s.",
                    endpoint,
                    value,
                    sku,
                )

                return value > 0

            if response.status_code not in (
                429,
                500,
                502,
                503,
                504,
            ):
                logging.warning(
                    "Stock endpoint returned HTTP %s.",
                    response.status_code,
                )
                return None

            logging.warning(
                "Stock endpoint returned HTTP %s "
                "(attempt %s/%s).",
                response.status_code,
                attempt + 1,
                MAX_ATTEMPTS,
            )

        except (
            httpx.HTTPError,
            ValueError,
            TypeError,
            json.JSONDecodeError,
        ) as error:
            logging.warning(
                "Stock request failed "
                "(attempt %s/%s): %s",
                attempt + 1,
                MAX_ATTEMPTS,
                error,
            )

        if attempt < MAX_ATTEMPTS - 1:
            delay = retry_delay(
                response,
                attempt,
            )

            logging.info(
                "Retrying stock request in %s seconds.",
                delay,
            )

            time.sleep(delay)

    return None


def send_notification(client):
    payload = {
        "content": (
            "@everyone\n"
            "**RESTOCK ALERT**\n\n"
            f"**{PRODUCT_NAME}**\n"
            f"Size **{TARGET_SIZE} cm** is back in stock!\n\n"
            f"{PRODUCT_URL}"
        )
    }

    for attempt in range(MAX_ATTEMPTS):
        response = None

        try:
            response = client.post(
                DISCORD_WEBHOOK_URL,
                json=payload,
            )

            response.raise_for_status()

            logging.info(
                "Discord notification sent."
            )

            return

        except httpx.HTTPError as error:
            logging.warning(
                "Discord notification failed "
                "(attempt %s/%s): %s",
                attempt + 1,
                MAX_ATTEMPTS,
                error,
            )

        if attempt < MAX_ATTEMPTS - 1:
            delay = retry_delay(
                response,
                attempt,
            )

            logging.info(
                "Retrying Discord notification "
                "in %s seconds.",
                delay,
            )

            time.sleep(delay)

    raise RuntimeError(
        "Discord notification could not be sent."
    )


def apply_stock_result(
    previous_stock,
    current_stock,
    client,
    notify=send_notification,
    persist=save_state,
):
    """Persist a known result and notify only on an out-of-stock to in-stock transition."""

    if current_stock is None:
        return previous_stock

    if previous_stock is False and current_stock is True:
        logging.info(
            "Restock detected."
        )

        notify(client)

    persist(current_stock)

    return current_stock


def main():
    if not PRODUCT_URL or not DISCORD_WEBHOOK_URL:
        raise RuntimeError(
            "PRODUCT_URL and DISCORD_WEBHOOK_URL must be set."
        )

    previous_stock = load_state()

    with create_client() as client:
        while True:
            try:
                current_stock = check_stock(
                    PRODUCT_URL,
                    TARGET_SIZE,
                    client,
                )

                if current_stock is None:
                    logging.warning(
                        "Could not determine stock; "
                        "saved state is unchanged."
                    )
                else:
                    status = (
                        "IN STOCK"
                        if current_stock
                        else "OUT OF STOCK"
                    )

                    logging.info(
                        "%s | Size %s | %s",
                        PRODUCT_NAME,
                        TARGET_SIZE,
                        status,
                    )

                    previous_stock = apply_stock_result(
                        previous_stock,
                        current_stock,
                        client,
                    )

            except Exception:
                logging.exception(
                    "Stock check failed; "
                    "saved state is unchanged."
                )

            logging.info(
                "Checking again in %s seconds.",
                CHECK_INTERVAL,
            )

            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()