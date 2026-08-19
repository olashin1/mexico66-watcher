import httpx


PRODUCT_URL = (
    "https://www.onitsukatiger.com/jp/en-gl/"
    "product/mexico-66/1183C102_001.html"
)

TERMS = [
    "28.5",
    "1183C102_001_28.5",
    "salable",
    "is_salable",
    "available",
    "stock",
    "configurable",
    "product-addtocart-button",
]


response = httpx.get(
    PRODUCT_URL,
    follow_redirects=True,
    timeout=20,
    headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html",
    },
)

print("STATUS:", response.status_code)
print("HTML LENGTH:", len(response.text))

html = response.text

for term in TERMS:
    print()
    print("=" * 80)
    print(f"SEARCHING FOR: {term}")
    print("=" * 80)

    lower_html = html.lower()
    lower_term = term.lower()

    start_search = 0
    matches = 0

    while True:
        index = lower_html.find(lower_term, start_search)

        if index == -1:
            break

        matches += 1

        start = max(0, index - 500)
        end = min(len(html), index + 1500)

        print(f"\n--- MATCH {matches} ---")
        print(html[start:end])

        start_search = index + len(term)

        if matches >= 5:
            print("\nStopping after 5 matches.")
            break

    if matches == 0:
        print("NOT FOUND")