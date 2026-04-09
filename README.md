# ByteBites

ByteBites is a Python backend modeling customers, products, transactions, and purchase history for a restaurant-style ordering system. 
The project implements the object model and business logic, and I used it to tighten validation, bound resource usage, protect shared internal state, and make monetary calculations exact and reproducible.

## What I changed

- centralized text validation with stricter allowlist-based checks
- replaced float-based transaction totals with `Decimal`
- added explicit limits for catalog size, transaction size, purchase history, and text lengths
- changed catalog access to return an immutable tuple instead of a mutable list
- updated tests and sanity checks to verify the hardened behavior

## Security focus

The main hardening work in this project focused on:

- blocking malformed text and numeric input before storage
- preventing uncontrolled in-memory growth
- reducing accidental or unsafe mutation of shared internal state
- making monetary calculations exact instead of float-dependent

## Repo contents

- `models.py` - core data model and business logic
- `test_bytebites.py` - automated test coverage
- `tmp_sanity_check.py` - manual verification script
- `SECURITY_README.md` / change log - detailed hardening writeup
- case study document - summary of the hardening work

## Running the project

```bash
python -m pytest test_bytebites.py -q
python tmp_sanity_check.py
```

## Notes

This project was useful because the security work also improved correctness. The biggest example was moving transaction totals to `Decimal`, but the same pattern showed up elsewhere: stricter validation, clearer boundaries, and more predictable model behavior.
