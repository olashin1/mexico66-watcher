from main import check_stock


PRODUCT_URL = "https://www.onitsukatiger.com/jp/en-gl/product/gsm/1183a353_003.html"
EXPECTED = True


actual = check_stock(PRODUCT_URL, "28.5")
passed = actual is EXPECTED
print(f"{'PASS' if passed else 'FAIL'} | GSM / 28.5 | expected={EXPECTED} actual={actual}")
raise SystemExit(0 if passed else 1)
