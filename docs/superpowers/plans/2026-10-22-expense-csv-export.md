# Expense CSV Export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Allow users to download current in-memory expenses as a CSV file from the homepage.

**Architecture:** Add a server-side `GET /expenses.csv` endpoint that serializes the expense records using Python's standard-library `csv` writer, plus a link on `/`. Add endpoint tests using the existing FastAPI `TestClient`.

**Tech Stack:** Python 3.12+, FastAPI, standard-library `csv`, pytest.

**Spec:** `docs/superpowers/specs/2026-10-22-expense-csv-export-design.md`

## Global Constraints

- Expenses remain in memory and are not preserved across restarts.
- Export one CSV row per expense, with description, PHP amount, payer, and sharers in one column.
- Preserve Decimal amounts to two decimal places and use Python's CSV writer for correct escaping.
- Keep the existing app stack and avoid adding dependencies.

## Review Focus

- Empty expense list: return a valid CSV with headers and no data rows; covered by `test_csv_export_is_empty_when_no_expenses_exist`.
- Commas and quotes in descriptions: parse back as one unchanged field; covered by `test_csv_export_quotes_descriptions_with_commas_and_quotes`.
- Newlines inside descriptions: preserve them within one CSV field/record; covered by `test_csv_export_preserves_newline_in_description`.
- Unicode descriptions and names: preserve text without ASCII conversion; covered by `test_csv_export_preserves_unicode`.
- Decimal amounts with trailing zeroes: serialize exactly two places; covered by `test_csv_export_uses_two_decimal_places`.

---

### Task 1: Add downloadable current-run expense CSV

**Files:**
- Modify: `app.py`
- Test: `test_app.py`

**Interfaces:**
- Consumes: module-level `expenses: list[Expense]`.
- Produces: `GET /expenses.csv`, returning an attachment named `expenses.csv` with columns `description`, `amount_php`, `paid_by`, `shared_by`; sharers are joined with `; `.

- [ ] **Step 1: Add failing CSV endpoint tests**

Add tests to `test_app.py` that:
- Request `/expenses.csv` with no expenses and parse the response as CSV; assert the only row is `["description", "amount_php", "paid_by", "shared_by"]`.
- Add a test expense and assert the parsed row is `["Groceries", "900.00", "Alex", "Alex; Bea"]`.
- Assert the response has a `text/csv` content type and `Content-Disposition` attachment filename `expenses.csv`.
- Verify descriptions containing commas and quotes, embedded newlines, and Unicode survive CSV parsing as one description value.
- Verify `10.10` is exported as `"10.10"`.
- Assert the homepage includes a link to `/expenses.csv`.

- [ ] **Step 2: Run the new endpoint tests and verify they fail**

Run: `pytest -q test_app.py`
Expected: FAIL because the CSV endpoint and homepage link do not exist.

- [ ] **Step 3: Implement the CSV download and homepage link in `app.py`**

Import `csv`, `io`, and `Response`. Add a `GET /expenses.csv` route that writes the exact header and each current expense to a `StringIO(newline="")` via `csv.writer`; format `amount_php` with `f"{amount:.2f}"` and join sharer names with `"; "`. Return a `Response` with `media_type="text/csv"` and `Content-Disposition: attachment; filename="expenses.csv"`. Add a visible download link on `/`.

- [ ] **Step 4: Run the test suite and linter**

Run: `pytest -q && ruff check .`
Expected: all tests pass and Ruff reports no issues.

- [ ] **Step 5: Review the diff**

Run: `git diff --check`
Expected: no whitespace errors.
