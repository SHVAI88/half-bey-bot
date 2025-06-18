import json
import os

PRODUCTS_FILE = "products.json"
CARTS_FILE = "carts.json"

# === Товары ===
if os.path.exists(PRODUCTS_FILE):
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)
else:
    products = []

def save_products():
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

# === Корзины ===
if os.path.exists(CARTS_FILE):
    with open(CARTS_FILE, "r", encoding="utf-8") as f:
        carts = json.load(f)
else:
    carts = {}

def save_carts():
    with open(CARTS_FILE, "w", encoding="utf-8") as f:
        json.dump(carts, f, ensure_ascii=False, indent=2)