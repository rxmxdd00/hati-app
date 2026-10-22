import csv
import io
from decimal import ROUND_DOWN, Decimal, InvalidOperation
from html import escape
from typing import TypedDict

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

CENT = Decimal("0.01")


def spreadsheet_safe_text(value: str) -> str:
    first_significant = next(
        (char for char in value if not char.isspace() and char.isprintable()),
        "",
    )
    if first_significant in {"=", "+", "-", "@"}:
        return f"'{value}"
    return value


class Expense(TypedDict):
    description: str
    amount: Decimal
    payer: str
    shares: list[str]


app = FastAPI()
expenses: list[Expense] = []


def split_balances() -> list[tuple[str, str, Decimal]]:
    balances: dict[str, Decimal] = {}
    for expense in expenses:
        shares = expense["shares"]
        amount = expense["amount"]
        payer = expense["payer"]
        share = (amount / len(shares)).quantize(CENT, rounding=ROUND_DOWN)
        remainder = int((amount - share * len(shares)) / CENT)
        balances[payer] = balances.get(payer, Decimal(0)) + amount
        for index, person in enumerate(shares):
            owed_share = share + (CENT if index < remainder else Decimal(0))
            balances[person] = balances.get(person, Decimal(0)) - owed_share

    creditors = [[name, amount] for name, amount in balances.items() if amount > 0]
    debtors = [[name, -amount] for name, amount in balances.items() if amount < 0]
    settlements = []
    while debtors and creditors:
        debtor, debt = debtors[0]
        creditor, credit = creditors[0]
        amount = min(debt, credit)
        settlements.append((str(debtor), str(creditor), amount))
        debtors[0][1] -= amount
        creditors[0][1] -= amount
        if not debtors[0][1]:
            debtors.pop(0)
        if not creditors[0][1]:
            creditors.pop(0)
    return settlements


def page(message: str = "") -> str:
    rows = "".join(
        f"<li>{escape(item['description'])}: ₱{item['amount']:.2f} — paid by "
        f"{escape(item['payer'])}; shared by "
        f"{', '.join(escape(person) for person in item['shares'])}</li>"
        for item in expenses
    )
    owes = "".join(
        f"<li>{escape(debtor)} owes {escape(creditor)} ₱{amount:.2f}</li>"
        for debtor, creditor, amount in split_balances()
    ) or "<li>All settled up.</li>"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Roommate expense splitter</title>
  <style>
    body {{ font: 16px system-ui, sans-serif; max-width: 700px; margin: 3rem auto; padding: 0 1rem; color: #222; }}
    input {{ box-sizing: border-box; display: block; width: 100%; margin: .3rem 0 1rem; padding: .6rem; }}
    button {{ padding: .65rem 1rem; }} li {{ margin: .4rem 0; }} .error {{ color: #a00; }}
  </style>
</head>
<body>
  <h1>Roommate expense splitter</h1>
  <p>Enter amounts in Philippine pesos. Shares are split equally, down to the cent.</p>
  <p><a href="/expenses.csv">Download expenses as CSV</a></p>
  <p class="error">{escape(message)}</p>
  <form method="post" action="/expenses">
    <label>Description <input name="description" required maxlength="120"></label>
    <label>Amount (PHP) <input name="amount" type="number" min="0.01" step="0.01" required></label>
    <label>Who paid? <input name="payer" required placeholder="e.g. Alex"></label>
    <label>Who shares it? <input name="shares" required placeholder="Comma-separated names"></label>
    <button type="submit">Add expense</button>
  </form>
  <h2>Expenses</h2><ul>{rows or "<li>No expenses yet.</li>"}</ul>
  <h2>Who owes whom</h2><ul>{owes}</ul>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return page()


@app.get("/expenses.csv")
async def export_expenses():
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["description", "amount_php", "paid_by", "shared_by"])
    for expense in expenses:
        writer.writerow(
            [
                spreadsheet_safe_text(expense["description"]),
                f"{expense['amount']:.2f}",
                spreadsheet_safe_text(expense["payer"]),
                "; ".join(spreadsheet_safe_text(person) for person in expense["shares"]),
            ]
        )
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="expenses.csv"'},
    )


@app.post("/expenses")
async def add_expense(request: Request):
    form = await request.form()
    description = str(form.get("description", "")).strip()
    payer = str(form.get("payer", "")).strip()
    shares = list(dict.fromkeys(name.strip() for name in str(form.get("shares", "")).split(",") if name.strip()))
    try:
        amount = Decimal(str(form.get("amount", "")))
        if not amount.is_finite() or amount != amount.quantize(CENT) or amount <= 0:
            raise ValueError
    except (InvalidOperation, ValueError):
        return HTMLResponse(page("Enter a valid amount greater than zero, with at most two decimal places."), status_code=400)
    if not description or not payer or not shares or len(description) > 120:
        return HTMLResponse(page("Enter a description, payer, and at least one person sharing the expense."), status_code=400)
    if payer not in shares:
        shares.append(payer)
    expenses.append({"description": description, "amount": amount, "payer": payer, "shares": shares})
    return RedirectResponse("/", status_code=303)
