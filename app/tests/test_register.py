# app/tests/test_register.py
import pytest
from app.utils.password import hash_password
from asyncio import get_event_loop
from datetime import datetime

def test_register_customer_by_admin(client):
    db = client.app.state.db
    loop = get_event_loop()

    # Admin with created_at
    loop.run_until_complete(db.users.insert_one({
        "name": "Admin",
        "email": "admin@bank.com",
        "password": hash_password("Admin123!"),
        "role": "admin",
        "created_at": datetime.utcnow()
    }))

    # Login
    login = client.post("/auth/login", json={
        "email": "admin@bank.com",
        "password": "Admin123!"
    })
    assert login.status_code == 200
    token = login.json()["access_token"]

    # Register — auto created_at in API
    response = client.post("/auth/register", json={
        "name": "Ravi",
        "email": "ravi@customer.com",
        "password": "Ravi123!",
        "role": "customer"
        # ← NO created_at NEEDED IF API SETS IT
    }, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 201
    data = response.json()["user"]
    assert data["email"] == "ravi@customer.com"
    assert "created_at" in data
