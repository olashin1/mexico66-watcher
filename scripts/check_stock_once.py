from main import PRODUCT_URL, TARGET_SIZE, check_stock


result = check_stock(PRODUCT_URL, TARGET_SIZE)
print(f"Stock result for size {TARGET_SIZE}: {result}")
