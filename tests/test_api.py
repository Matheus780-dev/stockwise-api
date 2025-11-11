import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine
from app.main import app
from app import deps


TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={
                            "check_same_thread": False})


@pytest.fixture(autouse=True)
def setup_db(monkeypatch):

    monkeypatch.setattr(deps, "engine", test_engine)
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)


client = TestClient(app)


def test_flow_create_user_login_create_product_and_sale():

    r = client.post("/users/", params={"username": "u1", "password": "pass"})
    assert r.status_code == 201

    r = client.post("/token", data={"username": "u1", "password": "pass"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post(
        "/products/", params={"name": "Mouse", "price": 50, "quantity": 10},
        headers=headers)
    assert r.status_code == 201
    prod = r.json()
    pid = prod["id"]

    r = client.post(
        "/sales/", params={"product_id": pid, "quantity": 3}, headers=headers)
    assert r.status_code == 201
    sale = r.json()
    assert sale["quantity"] == 3
    assert float(sale["total_value"]) == 150.0

    r = client.get("/products/", headers=headers)
    assert r.status_code == 200
    prods = r.json()
    assert any(p["id"] == pid and p["quantity"] == 7 for p in prods)

    r = client.get("/reports/sales/csv", headers=headers)
    assert r.status_code == 200
    assert r.json()["rows"] >= 1

    r = client.get("/reports/sales/pdf", headers=headers)
    assert r.status_code == 200
    assert r.json()["rows"] >= 1
