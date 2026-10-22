# Expense CSV Export Design

## Intent

Let roommates download a spreadsheet-friendly export of expenses entered during
the current server run. Expenses remain in memory and are not preserved across
restarts.

## Goals and constraints

- Add a download link on `/` and a server-side `GET /expenses.csv` endpoint.
- Export one CSV row per expense, with description, PHP amount, payer, and
  sharers in one column.
- Preserve Decimal amounts to two decimal places and use Python's CSV writer
  for correct escaping.
- Keep the existing app stack and avoid adding dependencies.

Non-goals: persistence, exporting settlement balances, or changing how expenses
are entered or split.

## Approaches

- **Server-generated CSV endpoint (selected):** provides a direct downloadable
  file, uses the standard-library CSV writer, and exports the in-memory records
  directly.
- **Browser-generated CSV:** avoids a server route but couples export behavior
  to rendered page markup and can omit or misread data.

The server endpoint was selected for a reliable export based on the app's
underlying expense records.

## Design

Add a CSV response with a stable filename and headers `description`,
`amount_php`, `paid_by`, and `shared_by`. Format amounts with two decimal
places; join sharer names with `; ` in the final field. Add a download link to
the homepage. An empty expense list still returns a valid CSV containing its
headers. Add focused tests for headers and values, special-character escaping,
and the empty export.
