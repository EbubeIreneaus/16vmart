import json
import os
from pathlib import Path
from typing import Any

import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
ADMIN_EMAIL = "alfredebube7@gmail.com"
ADMIN_PASSWORD = "@178420443Aa"

SEED_FILE = Path(__file__).with_name("seed_data") / "category_seed.json"


def load_category_seeds() -> list[dict[str, Any]]:
    with SEED_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


CATEGORY_SEEDS = load_category_seeds()


def get_auth_headers(client: httpx.Client) -> dict[str, str]:
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        raise RuntimeError(
            "Set ADMIN_EMAIL and ADMIN_PASSWORD environment variables to an existing admin account."
        )

    signin_response = client.post(
        f"{API_BASE_URL}/api/v1/auth/signin",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=20,
    )

    if signin_response.status_code != 200:
        raise RuntimeError(
            f"Authentication failed with status {signin_response.status_code}: {signin_response.text}"
        )

    token = signin_response.cookies.get("access_token")
    if not token:
        raise RuntimeError("The sign-in response did not include an access token cookie.")

    return {"Authorization": f"Bearer {token}"}


def get_existing_category_names(client: httpx.Client, headers: dict[str, str]) -> set[str]:
    response = client.get(f"{API_BASE_URL}/api/v1/cat/all", headers=headers, timeout=20)
    response.raise_for_status()

    categories = response.json()
    names: set[str] = set()

    for category in categories:
        names.add(str(category.get("name", "")).strip().lower())

    return names


def seed_categories() -> None:
    with httpx.Client(base_url=API_BASE_URL, timeout=30) as client:
        headers = get_auth_headers(client)
        existing_names = get_existing_category_names(client, headers)

        for payload in CATEGORY_SEEDS:
            name = payload["name"].strip().lower()
            if name in existing_names:
                print(f"Skipping existing parent category: {payload['name']}")
                continue

            response = client.post(
                "/api/v1/admin/cat/create-category",
                headers=headers,
                json=payload,
                timeout=30,
            )

            if response.status_code in {200, 201}:
                print(f"Created category: {payload['name']}")
            elif response.status_code == 409:
                print(f"Category already exists: {payload['name']}")
            else:
                print(f"Failed to create {payload['name']}: {response.status_code} {response.text}")


if __name__ == "__main__":
    seed_categories()
