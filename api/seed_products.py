import os
import random
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List

import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "alfredebube7@gmail.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "@178420443Aa")
SELLER_EMAIL = os.getenv("SELLER_EMAIL", "okigweebube7@gmail.com")
SELLER_PASSWORD = os.getenv("SELLER_PASSWORD", "@178420443Aa")
STORE_SLUG = os.getenv("STORE_SLUG", "atlas-lifestyle")

# 25 Real-World Product Templates
REAL_WORLD_PRODUCTS = [
    {"name": "Apple iPhone 15 Pro Max 256GB", "price": "1199.99", "description": "Titanium design with A17 Pro chip, customizable Action button, and 48MP camera system.", "condition": "brand new"},
    {"name": "Samsung Galaxy S24 Ultra 512GB", "price": "1299.00", "description": "Galaxy AI powered flagship with built-in S Pen, 200MP camera, and Snapdragon 8 Gen 3.", "condition": "brand new"},
    {"name": "Sony WH-1000XM5 Wireless Headphones", "price": "398.00", "description": "Industry leading noise canceling headphones with Auto NC Optimizer and 30-hour battery life.", "condition": "brand new"},
    {"name": "MacBook Pro 16-inch M3 Max", "price": "3499.00", "description": "Ultimate performance laptop featuring Liquid Retina XDR display, 36GB unified memory, and 1TB SSD.", "condition": "brand new"},
    {"name": "Dell XPS 15 OLED Touch Laptop", "price": "1899.50", "description": "High performance 15.6 inch 3.5K OLED touchscreen laptop with Intel Core i9 and RTX 4060.", "condition": "brand new"},
    {"name": "Sony PlayStation 5 Slim Console", "price": "499.99", "description": "Next-gen gaming console with 1TB SSD storage, ultra-high speed I/O, and DualSense haptic feedback.", "condition": "brand new"},
    {"name": "Nintendo Switch OLED Model", "price": "349.99", "description": "7-inch vibrant OLED screen, wide adjustable stand, wired LAN dock, and 64GB storage.", "condition": "brand new"},
    {"name": "LG C3 65-inch 4K Smart OLED TV", "price": "1596.99", "description": "self-lit OLED pixels with α9 AI Processor Gen6, 120Hz refresh rate, and Dolby Vision.", "condition": "brand new"},
    {"name": "Apple iPad Air 11-inch M2 128GB", "price": "599.00", "description": "Redesigned iPad Air powered by M2 chip with Liquid Retina display and Wi-Fi 6E.", "condition": "brand new"},
    {"name": "Canon EOS R6 Mark II Mirrorless Camera", "price": "2299.00", "description": "Full-frame 24.2MP sensor with up to 40 fps continuous shooting and 4K 60p uncropped video.", "condition": "brand new"},
    {"name": "Apple Watch Series 9 GPS 45mm", "price": "429.00", "description": "Advanced health sensors, S9 SiP chip, Double Tap gesture control, and brighter display.", "condition": "brand new"},
    {"name": "Bose QuietComfort Ultra Earbuds", "price": "299.00", "description": "World-class spatial audio earbuds with custom tune technology and quiet mode.", "condition": "brand new"},
    {"name": "Asus ROG Zephyrus G16 Gaming Laptop", "price": "1999.99", "description": "Intel Core Ultra 9, RTX 4070, 2.5K 240Hz OLED display gaming powerhouse.", "condition": "brand new"},
    {"name": "GoPro HERO12 Black Action Camera", "price": "399.00", "description": "5.3K video resolution, HyperSmooth 6.0 stabilization, and extended battery runtime.", "condition": "brand new"},
    {"name": "Google Pixel 8 Pro 128GB", "price": "999.00", "description": "Google Tensor G3 chip, pro-level triple camera system, and 7 years of OS updates.", "condition": "brand new"},
    {"name": "Sonos Era 300 Smart Speaker", "price": "449.00", "description": "Spatial audio speaker with Dolby Atmos, Bluetooth, Wi-Fi, and voice control.", "condition": "brand new"},
    {"name": "Samsung Odyssey G9 49-inch Curved Monitor", "price": "1299.99", "description": "Dual QHD curved gaming monitor with 240Hz refresh rate and 1ms response time.", "condition": "brand new"},
    {"name": "Dyson V15 Detect Cordless Vacuum", "price": "749.99", "description": "Intelligent cordless vacuum with laser illumination that reveals invisible dust.", "condition": "brand new"},
    {"name": "Anker 737 Power Bank 24,000mAh", "price": "149.99", "description": "140W fast charging power bank with smart digital display and multi-device output.", "condition": "brand new"},
    {"name": "Keychron Q1 Max Wireless Custom Keyboard", "price": "209.00", "description": "Full aluminum QMK/VIA wireless mechanical keyboard with hot-swappable switches.", "condition": "brand new"},
    {"name": "Logitech MX Master 3S Wireless Mouse", "price": "99.99", "description": "Ergonomic performance mouse with 8K DPI tracking and quiet click switches.", "condition": "brand new"},
    {"name": "Kindle Paperwhite 16GB Signature Edition", "price": "189.99", "description": "6.8-inch display, auto-adjusting front light, wireless charging, and glare-free screen.", "condition": "brand new"},
    {"name": "Marshall Stanmore III Bluetooth Speaker", "price": "379.99", "description": "Home audio speaker with iconic vintage aesthetics, room-filling sound, and Bluetooth 5.2.", "condition": "brand new"},
    {"name": "Garmin Fenix 7 Pro Solar Multisport Watch", "price": "799.99", "description": "Solar powered multisport GPS watch with built-in flashlight and endurance score.", "condition": "brand new"},
    {"name": "DJI Mini 4 Pro Fly More Combo Drone", "price": "1099.00", "description": "Sub-249g mini camera drone with 4K 60fps HDR video and omnidirectional obstacle sensing.", "condition": "brand new"},
]


def signin_and_get_headers(email: str, password: str) -> tuple[dict[str, str], httpx.Cookies]:
    with httpx.Client(base_url=API_BASE_URL, timeout=30) as client:
        res = client.post("/api/v1/auth/signin", json={"email": email, "password": password}, timeout=20)
        if res.status_code != 200:
            raise RuntimeError(f"Signin failed for {email}: {res.status_code} {res.text}")
        token = res.cookies.get("access_token")
        if not token:
            raise RuntimeError("Signin did not return access_token cookie")
        return {"Authorization": f"Bearer {token}"}, res.cookies


def fetch_store_categories(store_slug: str, headers: dict[str, str], cookies: httpx.Cookies) -> list[dict[str, Any]]:
    with httpx.Client(base_url=API_BASE_URL, timeout=30, cookies=cookies) as client:
        res = client.get(f"/api/v1/store/{store_slug}/cat/all", headers=headers, timeout=20)
        if res.status_code != 200:
            raise RuntimeError(f"Failed fetching categories: {res.status_code} {res.text}")
        return res.json()


def fetch_category_attributes(store_slug: str, cat_id: int, headers: dict[str, str], cookies: httpx.Cookies) -> list[dict[str, Any]]:
    with httpx.Client(base_url=API_BASE_URL, timeout=30, cookies=cookies) as client:
        res = client.get(f"/api/v1/store/{store_slug}/cat/attr/{cat_id}", headers=headers, timeout=20)
        if res.status_code != 200:
            return []
        return res.json()


def pick_attribute_value(attr: dict[str, Any]) -> Any:
    form_type = attr.get("form_type", "text")
    options = attr.get("options") or []

    if form_type in {"select", "radio"} and options:
        return random.choice(options)
    elif form_type == "multiple" and options:
        return random.sample(options, k=min(len(options), 2))
    elif form_type == "boolean":
        return True
    elif form_type == "number":
        return random.randint(1, 256)
    elif form_type == "date":
        return datetime.utcnow().strftime("%Y-%m-%d")
    elif form_type in {"select", "radio", "multiple"}:
        return "Standard"
    else:
        name = str(attr.get("name", "")).lower()
        if "brand" in name:
            return random.choice(["Apple", "Samsung", "Sony", "Dell", "LG", "Bose", "Canon", "GoPro"])
        elif "color" in name:
            return random.choice(["Black", "Silver", "Midnight", "Titanium", "White"])
        elif "storage" in name or "memory" in name:
            return random.choice(["128GB", "256GB", "512GB", "1TB"])
        return "High Quality"


def seed_products() -> None:
    print(f"Signing in seller: {SELLER_EMAIL}...")
    seller_headers, seller_cookies = signin_and_get_headers(SELLER_EMAIL, SELLER_PASSWORD)

    print(f"Fetching store categories for {STORE_SLUG}...")
    categories = fetch_store_categories(STORE_SLUG, seller_headers, seller_cookies)

    if not categories:
        raise RuntimeError("No categories found! Please seed or create categories first.")

    # Flatten categories and subcategories into a target list
    target_categories: list[dict[str, Any]] = []
    for parent in categories:
        subcats = parent.get("sub_categories") or []
        if subcats:
            target_categories.extend(subcats)
        else:
            target_categories.append(parent)

    print(f"Found {len(target_categories)} target category nodes.")

    # Pre-fetch attributes for each target category
    cat_attributes_map: dict[int, list[dict[str, Any]]] = {}
    for cat in target_categories:
        cat_id = cat.get("id")
        if cat_id:
            cat_attributes_map[cat_id] = fetch_category_attributes(STORE_SLUG, cat_id, seller_headers, seller_cookies)

    created_count = 0
    failed_count = 0

    with httpx.Client(base_url=API_BASE_URL, timeout=30, cookies=seller_cookies) as client:
        for idx, template in enumerate(REAL_WORLD_PRODUCTS[:25]):
            # Assign category cyclically
            assigned_cat = target_categories[idx % len(target_categories)]
            cat_id = assigned_cat["id"]
            attrs = cat_attributes_map.get(cat_id, [])

            attributes_payload = []
            for attr in attrs:
                attr_id = attr.get("id")
                if attr_id:
                    val = pick_attribute_value(attr)
                    attributes_payload.append({
                        "attribute_id": attr_id,
                        "value": val,
                    })

            product_payload = {
                "name": template["name"],
                "price": str(Decimal(template["price"])),
                "description": template["description"],
                "condition": template["condition"],
                "available": True,
                "category_id": cat_id,
                "attributes": attributes_payload,
            }

            res = client.post(
                f"/api/v1/store/{STORE_SLUG}/products/",
                headers=seller_headers,
                json=product_payload,
                timeout=30,
            )

            if res.status_code in {200, 201}:
                res_json = res.json()
                slug = res_json.get("product_id") or res_json.get("slug")
                print(f"[{idx+1}/25] Created product: {template['name']} (Slug: {slug})")
                created_count += 1
            else:
                print(f"[{idx+1}/25] Failed to create {template['name']}: Status {res.status_code} - {res.text}")
                failed_count += 1

    print("\n--- Product Seeding Summary ---")
    print(f"Successfully Created: {created_count}")
    print(f"Failed: {failed_count}")


if __name__ == "__main__":
    seed_products()
