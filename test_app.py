from decimal import Decimal

from fastapi.testclient import TestClient

from app import app, expenses, split_balances

client = TestClient(app)


def setup_function():
    expenses.clear()


def test_homepage_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "Roommate expense splitter" in response.text


def test_expense_creates_owes_whom_summary():
    response = client.post(
        "/expenses",
        data={"description": "Groceries", "amount": "900", "payer": "Alex", "shares": "Alex, Bea, Cam"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    page = client.get("/").text
    assert "Groceries" in page
    assert "Bea owes Alex ₱300.00" in page
    assert "Cam owes Alex ₱300.00" in page


def test_remainder_is_allocated_without_losing_cents():
    client.post(
        "/expenses",
        data={"description": "Taxi", "amount": "10.01", "payer": "Alex", "shares": "Alex, Bea, Cam"},
    )
    assert split_balances() == [
        ("Bea", "Alex", Decimal("3.34")),
        ("Cam", "Alex", Decimal("3.33")),
    ]
