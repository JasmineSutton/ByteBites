# ByteBites Security Hardening - Detailed Change Log

This document explains the security changes made to the ByteBites codebase. It is organized by file and includes the line ranges affected, what each change does, what issue it fixes, and which security frameworks it maps to.

---

## Frameworks Referenced

| Abbreviation | Full Name | Description |
|---|---|---|
| **OWASP Top 10** | Open Worldwide Application Security Project Top 10 (2021) | A widely used list of the most critical web and application security risks. |
| **NIST SP 800-53** | NIST Special Publication 800-53 Rev. 5 | A catalog of federal security and privacy controls for information systems. |
| **CWE** | Common Weakness Enumeration | A standardized list of common software and hardware weakness types. |
| **OWASP ASVS** | OWASP Application Security Verification Standard v4 | A framework of detailed security requirements used for testing and validation. |

---

## File: `models.py`

### Change 1 - New imports and security constants (Lines 8–19)

**What was added:**

```python
import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

MAX_NAME_LENGTH = 100
MAX_CATEGORY_LENGTH = 50
MAX_CATALOG_SIZE = 10_000
MAX_TRANSACTION_ITEMS = 500
MAX_PURCHASE_HISTORY = 10_000
_SAFE_TEXT_RE = re.compile(r"^[\w\s\-'.&]+$", re.UNICODE)
```

**What it does:**
This adds the `re` module for regular-expression input validation and `Decimal` for precise monetary calculations. It also defines limits for text fields and in-memory collection sizes. The regex creates an allowlist that only permits word characters, spaces, hyphens, apostrophes, periods, and ampersands.

**Why it helps:**
The original code did not place clear limits on user-controlled values. That meant someone could submit extremely large inputs or flood collections with excessive data, which could create a denial-of-service problem. The regex also helps block malicious input such as script tags or SQL-style payloads before it is stored.

**Frameworks:**

| Framework | Control / ID | Relevance |
|---|---|---|
| OWASP Top 10 | **A03:2021 - Injection** | The allowlist helps block injection-style payloads in stored text. |
| OWASP Top 10 | **A04:2021 - Insecure Design** | Explicit limits support secure-by-design development. |
| CWE | **CWE-770** (Allocation of Resources Without Limits) | Prevents uncontrolled memory growth. |
| CWE | **CWE-20** (Improper Input Validation) | Enforces validation of allowed characters. |
| NIST SP 800-53 | **SI-10** (Information Input Validation) | Inputs are validated before they are accepted. |
| NIST SP 800-53 | **SC-5** (Denial-of-Service Protection) | Resource limits reduce DoS risk. |

---

### Change 2 - `_sanitize_text()` helper function (Lines 22–33)

**What was added:**

```python
def _sanitize_text(value: str, field_label: str, max_length: int) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_label} must be a string.")
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_label} cannot be empty.")
    if len(cleaned) > max_length:
        raise ValueError(f"{field_label} exceeds maximum length of {max_length} characters.")
    if not _SAFE_TEXT_RE.match(cleaned):
        raise ValueError(f"{field_label} contains invalid characters.")
    return cleaned
```

**What it does:**
This helper function centralizes text validation. It checks that the input is actually a string, removes leading and trailing whitespace, rejects blank values, enforces a maximum length, and rejects characters outside the approved pattern.

**Why it helps:**
Before this, validation was minimal and inconsistent. For example, a simple `strip()` check could reject empty input, but it would still allow overly long values or dangerous characters. Moving validation into one reusable function makes the code easier to audit and harder to bypass.

**Frameworks:**

| Framework | Control / ID | Relevance |
|---|---|---|
| OWASP Top 10 | **A03:2021 - Injection** | Allowlist validation is a direct defense against injection. |
| CWE | **CWE-20** (Improper Input Validation) | Applies structured validation at each input point. |
| CWE | **CWE-79** (Cross-site Scripting) | Rejects characters commonly used in stored XSS payloads. |
| NIST SP 800-53 | **SI-10** (Information Input Validation) | Covers type, length, and character-set validation. |
| OWASP ASVS | **5.1.3** | Supports positive allowlist validation. |

---

### Change 3 - `_to_decimal()` helper function (Lines 36–44)

**What was added:**

```python
def _to_decimal(value: float | int | str | Decimal, field_label: str) -> Decimal:
    if isinstance(value, float):
        value = str(round(value, 2))
    try:
        dec = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"{field_label} must be a valid number.")
    return dec
```

**What it does:**
This converts numeric input into a `Decimal` rounded to two places. If the input is a float, it is rounded and converted to a string first so that Python’s floating-point precision issues do not carry over into the calculation. Invalid values raise an error.

**Why it helps:**
Using native floats for money can cause subtle rounding issues. Those small errors are not just messy, they can become real business logic problems in financial code. Using `Decimal` makes the calculations exact and avoids the precision problems that come with float arithmetic.

**Frameworks:**

| Framework | Control / ID | Relevance |
|---|---|---|
| OWASP Top 10 | **A04:2021 - Insecure Design** | Exact arithmetic is a design requirement in financial logic. |
| CWE | **CWE-681** (Incorrect Conversion between Numeric Types) | Avoids precision loss in type conversion. |
| CWE | **CWE-682** (Incorrect Calculation) | Prevents incorrect monetary totals. |
| NIST SP 800-53 | **SI-10** (Information Input Validation) | Ensures numeric values are validated and normalized. |

---

### Change 4 - `Products.__post_init__()` hardened (Lines 57–71)

**What changed (before → after):**

*Before:*

```python
def __post_init__(self) -> None:
    if self.price < 0:
        raise ValueError("Product price cannot be negative.")
    if not (0 <= self.popularityRating <= 5):
        raise ValueError("Popularity rating must be between 0 and 5.")
    if not self.category.strip():
        raise ValueError("Product category cannot be empty.")
    if not self.name.strip():
        raise ValueError("Product name cannot be empty.")
    type(self)._catalog.append(self)
```

*After:*

```python
def __post_init__(self) -> None:
    self.name = _sanitize_text(self.name, "Product name", MAX_NAME_LENGTH)
    self.category = _sanitize_text(self.category, "Product category", MAX_CATEGORY_LENGTH)
    self.price = float(_to_decimal(self.price, "Product price"))
    if self.price < 0:
        raise ValueError("Product price cannot be negative.")
    if not isinstance(self.popularityRating, (int, float)):
        raise TypeError("Popularity rating must be a number.")
    if not (0 <= self.popularityRating <= 5):
        raise ValueError("Popularity rating must be between 0 and 5.")
    if len(type(self)._catalog) >= MAX_CATALOG_SIZE:
        raise OverflowError(f"Catalog cannot exceed {MAX_CATALOG_SIZE} items.")
    type(self)._catalog.append(self)
```

**What it does:**
This update strengthens product validation by sanitizing name and category, normalizing price, checking that popularityRating is actually numeric, and enforcing a maximum catalog size.

**Why it helps:**
The earlier version only checked a few conditions and left a lot of room for bad input. It would accept dangerous characters in names and categories, allowed weak typing around popularity ratings, and placed no limit on catalog growth. This version closes those gaps and makes the object safer from the start.

**Frameworks:**

| Framework | Control / ID | Relevance |
|---|---|---|
| OWASP Top 10 | **A03:2021 - Injection** | Sanitized product fields reduce injection risk. |
| OWASP Top 10 | **A04:2021 - Insecure Design** | Adds defensive controls and resource boundaries. |
| CWE | **CWE-20** (Improper Input Validation) | Improves validation for multiple fields. |
| CWE | **CWE-770** (Allocation of Resources Without Limits) | Caps catalog size. |
| CWE | **CWE-1287** (Improper Validation of Specified Type of Input) | Verifies the expected data type. |
| NIST SP 800-53 | **SI-10** (Information Input Validation) | Validates data before storage. |
| NIST SP 800-53 | **SC-5** (Denial-of-Service Protection) | Prevents unbounded collection growth. |

---

### Change 5 - `Products.listCatalog()` returns immutable tuple (Lines 89–91)

**What changed (before → after):**

*Before:*

```python
def listCatalog(cls) -> list["Products"]:
    return list(cls._catalog)
```

*After:*

```python
def listCatalog(cls) -> tuple["Products", ...]:
    return tuple(cls._catalog)
```

**What it does:**
This changes the return type from a mutable list to an immutable tuple.

**Why it helps:**
Returning a tuple makes it clear that callers are only supposed to read the catalog, not change it. That helps protect internal state and reduces the chance of accidental or unauthorized modification.

**Frameworks:**

| Framework | Control / ID | Relevance |
|---|---|---|
| OWASP Top 10 | **A04:2021 - Insecure Design** | Supports least-privilege design. |
| CWE | **CWE-1262** (Improper Access Control to Shared Resource) | Reduces the chance of outside mutation. |
| NIST SP 800-53 | **AC-3** (Access Enforcement) | Helps enforce read-only behavior. |

---

### Change 6 - `Transactions.addItem()` size limit (Lines 105–109)

**What changed (before → after):**

*Before:*

```python
def addItem(self, product: Products) -> None:
    if not isinstance(product, Products):
        raise TypeError("Transactions can only include Products.")
    self.selectedItems.append(product)
```

*After:*

```python
def addItem(self, product: Products) -> None:
    if not isinstance(product, Products):
        raise TypeError("Transactions can only include Products.")
    if len(self.selectedItems) >= MAX_TRANSACTION_ITEMS:
        raise OverflowError(f"A transaction cannot contain more than {MAX_TRANSACTION_ITEMS} items.")
    self.selectedItems.append(product)
```

**What it does:**
This adds a maximum number of items allowed in a transaction.

**Why it helps:**
Without a limit, a transaction could keep growing until it consumed excessive memory. That creates an obvious resource-exhaustion risk. The size check makes the transaction safer and more predictable.

**Frameworks:**

| Framework | Control / ID | Relevance |
|---|---|---|
| OWASP Top 10 | **A04:2021 - Insecure Design** | Adds missing size-limit protections. |
| CWE | **CWE-770** (Allocation of Resources Without Limits) | Prevents unbounded list growth. |
| NIST SP 800-53 | **SC-5** (Denial-of-Service Protection) | Reduces memory exhaustion risk. |
| NIST SP 800-53 | **SI-10** (Information Input Validation) | Validates count before accepting new input. |

---

### Change 7 - `Transactions.calculateTotalCost()` uses Decimal (Lines 111–117)

**What changed (before → after):**

*Before:*

```python
def calculateTotalCost(self) -> float:
    return round(sum(product.price for product in self.selectedItems), 2)
```

*After:*

```python
def calculateTotalCost(self) -> Decimal:
    total = sum(
        (_to_decimal(product.price, "price") for product in self.selectedItems),
        Decimal("0.00"),
    )
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

**What it does:**
This changes total-cost calculation from float arithmetic to Decimal arithmetic.

**Why it helps:**
For money, float is just not the right tool. Small rounding errors can creep in, especially after repeated calculations. `Decimal` keeps the math exact, which matters for both correctness and security.

**Frameworks:**

| Framework | Control / ID | Relevance |
|---|---|---|
| OWASP Top 10 | **A04:2021 - Insecure Design** | Correct financial logic depends on exact arithmetic. |
| CWE | **CWE-682** (Incorrect Calculation) | Prevents calculation errors. |
| CWE | **CWE-681** (Incorrect Conversion between Numeric Types) | Uses the correct type for money. |
| NIST SP 800-53 | **SI-10** (Information Input Validation) | Supports validated and normalized numeric processing. |

---

### Change 8 - `PurchaseHistory.addTransaction()` size limit (Lines 124–130)

**What changed (before → after):**

*Before:*

```python
def addTransaction(self, new_transaction: Transactions) -> None:
    if not isinstance(new_transaction, Transactions):
        raise TypeError("PurchaseHistory only accepts Transactions.")
    if len(new_transaction.selectedItems) == 0:
        raise ValueError("Cannot add an empty transaction to purchase history.")
    self.transactions.append(new_transaction)
```

*After:*

```python
def addTransaction(self, new_transaction: Transactions) -> None:
    if not isinstance(new_transaction, Transactions):
        raise TypeError("PurchaseHistory only accepts Transactions.")
    if len(new_transaction.selectedItems) == 0:
        raise ValueError("Cannot add an empty transaction to purchase history.")
    if len(self.transactions) >= MAX_PURCHASE_HISTORY:
        raise OverflowError(f"Purchase history cannot exceed {MAX_PURCHASE_HISTORY} transactions.")
    self.transactions.append(new_transaction)
```

**What it does:**
This adds a maximum size for the purchase-history collection.

**Why it helps:**
Just like the transaction item limit, this prevents uncontrolled growth in memory. That makes the system more resilient against abuse and accidental overuse.

**Frameworks:**

| Framework | Control / ID | Relevance |
|---|---|---|
| CWE | **CWE-770** (Allocation of Resources Without Limits) | Prevents unbounded growth of stored transactions. |
| NIST SP 800-53 | **SC-5** (Denial-of-Service Protection) | Helps protect against resource exhaustion. |
| OWASP Top 10 | **A04:2021 - Insecure Design** | Adds a design-level resource limit. |

---

### Change 9 - `Customers.__post_init__()` sanitization (Lines 140–142)

**What changed (before → after):**

*Before:*

```python
def __post_init__(self) -> None:
    if not self.name.strip():
        raise ValueError("Customer name cannot be empty.")
```

*After:*

```python
def __post_init__(self) -> None:
    self.name = _sanitize_text(self.name, "Customer name", MAX_NAME_LENGTH)
```

**What it does:**
This replaces the simple empty-string check with the full sanitization process.

**Why it helps:**
A name field might look harmless, but it is still user input. If it is not validated properly, it can become a place to store script content, malformed values, or other dangerous input. This update treats the customer name the same way as other important text fields.

**Frameworks:**

| Framework | Control / ID | Relevance |
|---|---|---|
| OWASP Top 10 | **A03:2021 - Injection** | Validates customer names against injection-style input. |
| CWE | **CWE-20** (Improper Input Validation) | Strengthens user-input validation. |
| CWE | **CWE-79** (Cross-site Scripting) | Helps prevent stored XSS-style payloads. |
| NIST SP 800-53 | **SI-10** (Information Input Validation) | Enforces consistent validation rules. |
| OWASP ASVS | **5.1.3** | Uses allowlist validation. |

---

## File: `test_bytebites.py`

### Change 10 - Updated assertions to use Decimal (Lines 1, 19, 25)

**What changed:**

```python
from decimal import Decimal

assert order.calculateTotalCost() == Decimal("16.47")
assert order.calculateTotalCost() == Decimal("0.00")
```

**What it does:**
The test file was updated so that it now checks for `Decimal` results instead of float values.

**Why it helps:**
Once the application logic moved to `Decimal`, the tests needed to reflect that change too. Otherwise, the tests would no longer be validating the actual behavior of the hardened code.

**Frameworks:**

| Framework | Control / ID | Relevance |
|---|---|---|
| NIST SP 800-53 | **SA-11** (Developer Testing and Evaluation) | Confirms that the security-related logic works as intended. |
| OWASP ASVS | **14.2.2** | Security controls should be tested, not just added. |

---

## File: `tmp_sanity_check.py`

### Change 11 - Sanity check rebuilt for comprehensive validation

**What changed:**
The sanity check was rebuilt so it now works as a full manual smoke test for all four classes. It checks catalog immutability, category filtering, sort behavior, total-cost calculation, transaction history, user verification behavior, and rejection of invalid input such as empty names, injection characters, invalid ratings, negative prices, and empty transactions. It also uses `Decimal` for monetary assertions.

**Why it helps:**
This provides a readable way to manually confirm that the hardening changes are doing what they are supposed to do. The automated tests are still important, but the sanity check gives a broader picture of how the application behaves after the changes.

**Frameworks:**

| Framework | Control / ID | Relevance |
|---|---|---|
| NIST SP 800-53 | **SA-11** (Developer Testing and Evaluation) | Supports validation of implemented security controls. |

---

## Summary Table of All Security Changes

| # | File | Lines | What Changed | Vulnerability Addressed | Primary Framework(s) |
|---|---|---|---|---|---|
| 1 | `models.py` | 8–19 | Added `re`, `Decimal`, security limits, and regex allowlist | Injection, DoS, input validation issues | OWASP A03, CWE-770, CWE-20, NIST SI-10, NIST SC-5 |
| 2 | `models.py` | 22–33 | Added `_sanitize_text()` | Injection, XSS, improper validation | OWASP A03, CWE-20, CWE-79, NIST SI-10, ASVS 5.1.3 |
| 3 | `models.py` | 36–44 | Added `_to_decimal()` | Float precision problems, incorrect calculations | OWASP A04, CWE-681, CWE-682, NIST SI-10 |
| 4 | `models.py` | 57–71 | Hardened `Products.__post_init__()` | Injection, DoS, weak type validation | OWASP A03/A04, CWE-20/770/1287, NIST SI-10/SC-5 |
| 5 | `models.py` | 89–91 | Changed `listCatalog()` to return a tuple | Unauthorized mutation of internal state | OWASP A04, CWE-1262, NIST AC-3 |
| 6 | `models.py` | 105–109 | Added transaction item size limit | Resource exhaustion | CWE-770, NIST SC-5, OWASP A04 |
| 7 | `models.py` | 111–117 | Switched `calculateTotalCost()` to `Decimal` | Incorrect monetary calculations | OWASP A04, CWE-682, CWE-681 |
| 8 | `models.py` | 124–130 | Added purchase history size limit | Resource exhaustion | CWE-770, NIST SC-5, OWASP A04 |
| 9 | `models.py` | 140–142 | Sanitized customer name input | Injection, XSS | OWASP A03, CWE-20/79, NIST SI-10, ASVS 5.1.3 |
| 10 | `test_bytebites.py` | 1, 19, 25 | Updated tests to use `Decimal` | Misaligned security test coverage | NIST SA-11, ASVS 14.2.2 |
| 11 | `tmp_sanity_check.py` | All | Rebuilt sanity check for broader validation | Incomplete manual verification | NIST SA-11, OWASP A03, A04 |

---

## How to Verify Security Controls

Two commands can be used to confirm that the security hardening is working:

```bash
python -m pytest test_bytebites.py -v
python tmp_sanity_check.py
```

Expected results:
- pytest: **7 passed, 0 failed**
- sanity check: `All sanity checks passed.`

> Note: Running `python models.py` confirms that the CLI still works, but it is not part of the actual security verification process.
