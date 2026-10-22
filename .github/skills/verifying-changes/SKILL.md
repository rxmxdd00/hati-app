---
name: verifying-changes
description: Verifies code changes by running relevant tests, exercising the changed feature, and reporting concrete evidence. Use when a code change is finished or the user asks to verify changes, test this, check that it works, confirm the fix, or prove it works. Not for Implementing new features, brainstorming designs, or reviewing code style without a verification request.
argument-hint: "[feature or page]"
allowed-tools: Keep the defaults that support file reading and terminal commands
---

# Verifying Changes

## Inputs

You need:

- **feature**: the page, endpoint, or behavior to verify, only if it cannot be identified from the changes

Take them from the user's message. If a required input is missing, ask for all missing inputs in one question. Use defaults only where one is listed. Do not guess.

## Steps

1. Run pytest -q and paste the summary line
2. Start the app and wait until it responds
3. Open the changed page or call the changed endpoint, and go through the flow a user would follow
4. Try one invalid input and one empty input on the changed feature
5. Check the app logs for new errors or warnings
6. Stop the app

## Done when

- Report lists every command run, with its result
- At least one real use of the changed feature, with what you saw
- Says clearly: verified, or not verified and why

## Example output

```
Ran: pytest -q  ->  14 passed
Opened /expenses, added PHP 900 split 3 ways: each shows PHP 300
Empty amount: shows 'Amount is required'
Logs: no new errors
Verified.
```
