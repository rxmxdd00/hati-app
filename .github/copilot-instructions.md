# hati-app

## Stack

- Python 3.12, FastAPI, pytest

# Repository guidance

## Commands

- Install dependencies: `python3 -m pip install -r requirements.txt`
- Run the app: `python3 -m uvicorn app:app --reload`
- Run all tests: `pytest -q`
- Run one test: `pytest -q test_app.py::test_homepage_loads` (replace the test name as needed)
- Lint app and tests: `ruff check app.py test_app.py`

The project targets Python 3.12+ (`pyproject.toml`). `pytest` uses FastAPI's
`TestClient`; no separate test server is needed.

## Architecture

This is a small FastAPI app whose routes and server-rendered HTML live in
`app.py`. `GET /` builds the homepage from the module-level in-memory
`expenses` collection; `POST /expenses` validates form input, stores amounts as
`Decimal`, and redirects back to the page. `split_balances()` calculates
equal-share balances with cent-precise Decimal arithmetic, and the page shows
settlements and recent expenses. `GET /expenses.csv` exports the same current
in-memory records as a CSV attachment; data is lost when the process restarts.

`test_app.py` exercises the routes and balance calculation with a shared
`TestClient`. Its `setup_function()` clears the global expense list before
each test.

## Project-specific conventions

- Keep monetary values as `Decimal`; validate at most two decimal places and
  avoid converting money to `float`.
- Preserve cent-level split behavior: any remainder cents are assigned in
  sharer order.
- Escape user-provided text before interpolating it into the HTML built by
  `page()`.
- CSV exports use the standard-library `csv` writer, two-decimal amount strings,
  and spreadsheet-safe handling for user-entered text.
- Keep the existing server-rendered FastAPI approach; the homepage styling is
  inline in `page()` and should remain responsive and accessible on phones.
- Homepage behavior is covered by route tests. When updating its form or
  layout, preserve the `/expenses` form field names (`description`, `amount`,
  `payer`, `shares`), settlement display, expense history, and `/expenses.csv`
  download link.

## Before you say "done"

- Run pytest -q and show the result
