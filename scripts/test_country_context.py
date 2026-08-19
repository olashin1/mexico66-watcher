import httpx

PRODUCT_URL = (
    "https://www.onitsukatiger.com/jp/en-gl/"
    "product/mexico-66/1183C102_001.html"
)

STOCK_URL = (
    "https://www.onitsukatiger.com/jp/en-gl/"
    "mobilestock/index/stock"
)

SKU = "1183C102_001_28.5"

headers = {
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": PRODUCT_URL,
    "User-Agent": "Mozilla/5.0",
}


def check(name, cookies=None):
    with httpx.Client(
        headers=headers,
        cookies=cookies or {},
        follow_redirects=True,
        timeout=20,
    ) as client:
        response = client.get(
            STOCK_URL,
            params={
                "isAjax": "1",
                "skus": SKU,
            },
        )

        data = response.json()
        value = data["stock"][SKU]["value"]

        print(f"{name:<30} value={value}")


check("No cookies")

check(
    "user_country only",
    {
        "user_country": "US",
    },
)

check(
    "GlobalE_Data only",
    {
        "GlobalE_Data": (
            '{"countryISO":"US","currencyCode":"USD",'
            '"cultureCode":"en-US","isOperatedByGlobalE":true,'
            '"isSupportsFixedPrice":false}'
        ),
    },
)

check(
    "Both country cookies",
    {
        "user_country": "US",
        "GlobalE_Data": (
            '{"countryISO":"US","currencyCode":"USD",'
            '"cultureCode":"en-US","isOperatedByGlobalE":true,'
            '"isSupportsFixedPrice":false}'
        ),
    },
)