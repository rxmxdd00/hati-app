import csv
from decimal import Decimal
from io import StringIO

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


def test_csv_export_is_empty_when_no_expenses_exist():
    response = client.get("/expenses.csv")

    assert response.status_code == 200
    assert list(csv.reader(StringIO(response.text))) == [
        ["description", "amount_php", "paid_by", "shared_by"]
    ]


def test_csv_export_includes_expense_and_download_headers():
    expenses.append(
        {
            "description": "Groceries",
            "amount": Decimal("900.00"),
            "payer": "Alex",
            "shares": ["Alex", "Bea"],
        }
    )

    response = client.get("/expenses.csv")
    rows = list(csv.reader(StringIO(response.text)))

    assert rows[1] == ["Groceries", "900.00", "Alex", "Alex; Bea"]
    assert response.headers["content-type"].startswith("text/csv")
    assert response.headers["content-disposition"] == 'attachment; filename="expenses.csv"'


def test_csv_export_quotes_descriptions_with_commas_and_quotes():
    description = 'Groceries, "weekly"'
    expenses.append(
        {
            "description": description,
            "amount": Decimal("10.10"),
            "payer": "Alex",
            "shares": ["Alex"],
        }
    )

    rows = list(csv.reader(StringIO(client.get("/expenses.csv").text)))

    assert rows[1][0] == description
    assert rows[1][1] == "10.10"


def test_csv_export_preserves_newline_in_description():
    description = "Groceries\nand supplies"
    expenses.append(
        {
            "description": description,
            "amount": Decimal("1.00"),
            "payer": "Alex",
            "shares": ["Alex"],
        }
    )

    rows = list(csv.reader(StringIO(client.get("/expenses.csv").text)))

    assert len(rows) == 2
    assert rows[1][0] == description


def test_csv_export_preserves_unicode_and_homepage_link():
    expenses.append(
        {
            "description": "Kape at pagkain",
            "amount": Decimal("1.00"),
            "payer": "José",
            "shares": ["José", "李"],
        }
    )

    rows = list(csv.reader(StringIO(client.get("/expenses.csv").text)))

    assert rows[1] == ["Kape at pagkain", "1.00", "José", "José; 李"]
    assert 'href="/expenses.csv"' in client.get("/").text


def test_csv_export_neutralizes_formula_leading_text_fields():
    expenses.append(
        {
            "description": "=HYPERLINK(\"https://example.com\")",
            "amount": Decimal("1.00"),
            "payer": "\t@SUM(A1:A2)",
            "shares": ["=SUM(A1)", "Bea"],
        }
    )

    rows = list(csv.reader(StringIO(client.get("/expenses.csv").text)))

    assert rows[1] == [
        "'=HYPERLINK(\"https://example.com\")",
        "1.00",
        "'\t@SUM(A1:A2)",
        "'=SUM(A1); Bea",
    ]
