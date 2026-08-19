import httpx

from main import check_stock


PRODUCT_URL = "https://www.onitsukatiger.com/jp/en-gl/product/mexico-66/1183C102_001.html"
request_urls = []


def record_request(request):
    request_urls.append(str(request.url))


with httpx.Client(
    timeout=httpx.Timeout(20, connect=10),
    follow_redirects=True,
    event_hooks={"request": [record_request]},
) as client:
    result = check_stock(PRODUCT_URL, "28.5", client)

cart_requests = [url for url in request_urls if "/checkout/cart/add/" in url.lower()]
passed = result is not None and not cart_requests
print(f"{'PASS' if passed else 'FAIL'} | result={result} | requests={len(request_urls)}")
if cart_requests:
    print("Cart mutation request(s):")
    print(*cart_requests, sep="\n")
raise SystemExit(0 if passed else 1)
