# ByteBites Design Reference

## Behavioral Instructions

- Preserve the four core classes exactly: Customers, PurchaseHistory, Products, and Transactions.
- Treat `Products` as the single source of truth for menu data and catalog behavior.
- Use `Decimal` for all monetary values and totals; never model prices as plain floats in the design.
- Keep transaction-to-product relationships as `0..*` on the product side so a transaction may start empty and gain zero or more items.
- Keep the relationship between a customer and purchase history as a single owned history object.
- Design the catalog as a class-level collection named `_catalog` instead of introducing a separate `Menu` class; this reduces duplication and keeps filtering, sorting, and catalog access in one place.
- Prefer simple, explicit behavior over hidden complexity: filtering by category should be a direct catalog operation, and totals should compute from the selected items in a transaction.
- When in doubt, align the design with the feature request rather than expanding the system with extra responsibilities.

## Design Principle Notes

- `Products` holds the item definitions: name, price, category, and popularity rating.
- `Transactions` holds the chosen items for a single order and computes the order total.
- `PurchaseHistory` records completed transactions for a customer so verification can check whether they are real users.
- `Customers` stores their name and purchase history and exposes the verification check.
