import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    payload = {
        "fullname": "Test User",
        "email": "testuser@example.com",
        "password": "Password123!"
    }
    response = await client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient):
    payload = {
        "fullname": "Test User",
        "email": "duplicate@example.com",
        "password": "Password123!"
    }
    resp1 = await client.post("/api/v1/auth/signup", json=payload)
    assert resp1.status_code == 200

    resp2 = await client.post("/api/v1/auth/signup", json=payload)
    assert resp2.status_code == 409
    assert resp2.json()["detail"] == "Email already exist"

@pytest.mark.asyncio
async def test_signin_success(client: AsyncClient):
    email = "signinuser@example.com"
    password = "SecurePassword123!"
    await client.post("/api/v1/auth/signup", json={
        "fullname": "Signin Test User",
        "email": email,
        "password": password
    })

    signin_payload = {
        "email": email,
        "password": password
    }
    response = await client.post("/api/v1/auth/signin", json=signin_payload)
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

@pytest.mark.asyncio
async def test_signin_invalid_password(client: AsyncClient):
    email = "wrongpass@example.com"
    await client.post("/api/v1/auth/signup", json={
        "fullname": "Wrong Pass User",
        "email": email,
        "password": "CorrectPassword123!"
    })

    response = await client.post("/api/v1/auth/signin", json={
        "email": email,
        "password": "WrongPassword999!"
    })
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    signup_resp = await client.post("/api/v1/auth/signup", json={
        "fullname": "Refresh User",
        "email": "refresh@example.com",
        "password": "Password123!"
    })
    assert signup_resp.status_code == 200
    refresh_cookie = signup_resp.cookies.get("refresh_token")
    assert refresh_cookie is not None

    client.cookies.set("refresh_token", refresh_cookie)
    refresh_resp = await client.post("/api/v1/auth/refresh-token")
    assert refresh_resp.status_code == 200
    assert refresh_resp.json().get("success") is True
    assert "access_token" in refresh_resp.cookies

@pytest.mark.asyncio
async def test_signout(client: AsyncClient):
    signup_resp = await client.post("/api/v1/auth/signup", json={
        "fullname": "Signout User",
        "email": "signout@example.com",
        "password": "Password123!"
    })
    assert signup_resp.status_code == 200

    signout_resp = await client.post("/api/v1/auth/signout")
    assert signout_resp.status_code == 200
    assert signout_resp.json().get("success") is True
