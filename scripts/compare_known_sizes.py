from main import check_stock


MEXICO_66 = "https://www.onitsukatiger.com/jp/en-gl/product/mexico-66/1183C102_001.html"
GSM = "https://www.onitsukatiger.com/jp/en-gl/product/gsm/1183a353_003.html"
CASES = [
    ("Mexico 66", MEXICO_66, "27.5", False),
    ("Mexico 66", MEXICO_66, "28.0", False),
    ("Mexico 66", MEXICO_66, "28.5", False),
    ("GSM", GSM, "28.5", True),
]


print("Product    Size   Expected  Actual    Result")
print("---------------------------------------------")
failures = 0
for name, product_url, size, expected in CASES:
    actual = check_stock(product_url, size)
    passed = actual is expected
    failures += not passed
    print(f"{name:<10} {size:<6} {str(expected):<9} {str(actual):<9} {'PASS' if passed else 'FAIL'}")

raise SystemExit(1 if failures else 0)
