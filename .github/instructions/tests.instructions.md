---
applyTo: "tests/**/*.py"
---

# Rules for tests/**/*.py

- Every test has one clear assertion about behaviour.
- Use fixtures from tests/conftest.py; don't create new database setups.
- Name tests test_<what>_<when>_<expected>.
