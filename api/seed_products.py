import os
import random
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List

import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "alfredebube7@gmail.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "@178420443Aa")
SELLER_EMAIL = os.getenv("SELLER_EMAIL", "okigweebube7@gmail.com")
SELLER_PASSWORD = os.getenv("SELLER_PASSWORD", "@178420443Aa")
STORE_SLUG = os.getenv("STORE_SLUG", "ebube-electronics-venture")

# Number of sample products to create per subcategory
PER_SUBCAT = int(os.getenv("PER_SUBCAT", "2"))


def signin_and_get_headers(email: str, password: str) -> Dict[str, str]:
    with httpx.Client(base_url=API_BASE_URL, timeout=30) as client:
        res = client.post("/api/auth/signin", json={"email": email, "password": password}, timeout=20)
        if res.status_code != 200:
            raise RuntimeError(f"Signin failed for {email}: {res.status_code} {res.text}")
        token = res.cookies.get("access_token")
        if not token:
            raise RuntimeError("Signin did not return access_token cookie")
        return {"Authorization": f"Bearer {token}"}, client.cookies


def fetch_admin_categories(headers: Dict[str, str]) -> List[Dict[str, Any]]:
    with httpx.Client(base_url=API_BASE_URL, timeout=30) as client:
        res = client.get("/api/admin/cat/all", headers=headers, timeout=20)
        if res.status_code != 200:
            raise RuntimeError(f"Failed fetching admin categories: {res.status_code} {res.text}")
        return res.json()


def pick_value_for_form_type(form_type: str) -> Any:
    # Return a reasonable sample value based on the form_type
    if form_type == "text":
        return "Sample text"
    if form_type in {"select", "radio"}:
        # pick a sample option
        return random.choice(["Option A", "Option B", "Option C"])
    if form_type == "number":
        return random.randint(1, 100)
    if form_type == "boolean":
        return random.choice([True, False])
    if form_type == "date":
        return datetime.utcnow().isoformat() + "Z"
    if form_type == "multiple":
        return ["Option A", "Option B"]
    # fallback
    return "Sample"


def build_products_from_categories(categories: List[Dict[str, Any]], per_subcat: int = 2) -> List[Dict[str, Any]]:
    products: List[Dict[str, Any]] = []

    for parent in categories:
        parent_name = parent.get("name")
        parent_attrs = parent.get("attributes", [])
        subcats = parent.get("sub_categories") or []

        for sub in subcats:
            sub_name = sub.get("name")
            sub_id = sub.get("id")
            sub_attrs = sub.get("attributes", [])

            # combine parent and sub attributes
            combined_attrs = list(parent_attrs) + list(sub_attrs)

            for i in range(per_subcat):
                pname = f"{sub_name} Sample {i+1}"
                product_payload = {
                    "name": pname,
                    "price": str(Decimal(random.randint(1000, 10000)) / Decimal(100)),
                    "description": f"Auto-generated product for {sub_name}",
                    "condition": "brand new",
                    "available": True,
                    "category_id": sub_id,
                    "attributes": [],
                }

                for attr in combined_attrs:
                    # attr structure from AdminCategorySchema -> AttributeKeySchema
                    # expected keys: id, name, form_type
                    attr_id = attr.get("id")
                    form_type = attr.get("form_type", "text")
                    if not attr_id:
                        continue
                    value = pick_value_for_form_type(form_type)
                    product_payload["attributes"].append({
                        "attribute_id": attr_id,
                        "value": value,
                    })

                products.append(product_payload)
    return products


def post_products(products: List[Dict[str, Any]], seller_headers: Dict[str, str], cookies: httpx.Cookies, store_slug: str):
    with httpx.Client(base_url=API_BASE_URL, timeout=30, cookies=cookies) as client:
        for p in products:
            res = client.post(f"/api/store/products/{store_slug}", headers=seller_headers, json=p, timeout=30)
            if res.status_code in {200, 201}:
                print(f"Created product: {p['name']}")
            else:
                print(f"Failed to create {p['name']}: {res.status_code} {res.text}")


if __name__ == "__main__":
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        raise RuntimeError("Set ADMIN_EMAIL and ADMIN_PASSWORD env vars to read attribute IDs")
    if not SELLER_EMAIL or not SELLER_PASSWORD or not STORE_SLUG:
        raise RuntimeError("Set SELLER_EMAIL, SELLER_PASSWORD and STORE_SLUG env vars for product posting")

    # sign in as admin to fetch categories with attribute ids
    admin_headers, _ = signin_and_get_headers(ADMIN_EMAIL, ADMIN_PASSWORD)
    categories = fetch_admin_categories(admin_headers)

    if not categories:
        raise RuntimeError("No categories found from admin API")

    products = build_products_from_categories(categories, PER_SUBCAT)

    print(f"Built {len(products)} products to post.")

    seller_headers, seller_cookies = signin_and_get_headers(SELLER_EMAIL, SELLER_PASSWORD)

    post_products(products, seller_headers, seller_cookies, STORE_SLUG)
