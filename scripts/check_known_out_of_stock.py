from main import check_stock


PRODUCT_URL = "https://www.onitsukatiger.com/jp/en-gl/product/mexico-66/1183C102_001.html"
EXPECTED = False


actual = check_stock(PRODUCT_URL, "28.5")
passed = actual is EXPECTED
print(f"{'PASS' if passed else 'FAIL'} | Mexico 66 / 28.5 | expected={EXPECTED} actual={actual}")
raise SystemExit(0 if passed else 1)
