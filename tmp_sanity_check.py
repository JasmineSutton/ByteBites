# Purpose: Manual smoke test that exercises all four ByteBites classes end-to-end,
# verifying happy-path behavior, edge cases, and input validation across every
# security control in models.py. Run with: python tmp_sanity_check.py

from decimal import Decimal

from models import Customers, Products, PurchaseHistory, Transactions


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    Products.clearCatalog()

    # --- Seed catalog ---
    burger = Products("Spicy Burger", 8.99, "Entrees", 4.7)
    fries = Products("Seasoned Fries", 3.49, "Sides", 4.4)
    soda = Products("Large Soda", 2.49, "Drinks", 4.2)
    shake = Products("Chocolate Shake", 4.99, "Drinks", 4.8)

    # --- Catalog checks ---
    full_catalog = Products.listCatalog()
    check(len(full_catalog) == 4, "Expected four products in the catalog.")
    check(isinstance(full_catalog, tuple), "listCatalog() should return an immutable tuple.")

    # --- Filtering ---
    drinks = Products.filterByCategory("drinks")
    check(len(drinks) == 2, "Expected two drink products.")
    check(all(p.category.lower() == "drinks" for p in drinks), "Filter returned a non-drink item.")

    no_results = Products.filterByCategory("Desserts")
    check(no_results == [], "Unknown category should return empty list.")

    # --- Sorting ---
    by_price = Products.sortByPrice()
    check(by_price[0].name == "Large Soda", "Cheapest item should be first when sorting by price.")
    check(by_price[-1].name == "Spicy Burger", "Most expensive item should be last when sorting by price.")

    by_popularity = Products.sortByPopularity()
    check(by_popularity[0].name == "Chocolate Shake", "Most popular item should be first.")
    check(by_popularity[-1].name == "Large Soda", "Least popular item should be last.")

    # --- Transaction: total cost ---
    order = Transactions()
    order.addItem(burger)
    order.addItem(soda)
    order.addItem(shake)
    check(order.calculateTotalCost() == Decimal("16.47"), "Unexpected total cost for three-item order.")

    empty_order = Transactions()
    check(empty_order.calculateTotalCost() == Decimal("0.00"), "Empty transaction should total $0.00.")

    # --- PurchaseHistory ---
    history = PurchaseHistory()
    check(history.hasPastPurchases() is False, "New history should report no past purchases.")
    history.addTransaction(order)
    check(history.hasPastPurchases() is True, "History should report past purchases after adding a transaction.")

    # --- Customer: unverified then verified ---
    customer = Customers("Ava")
    check(customer.isVerifiedUser() is False, "New customer with no purchases should not be verified.")
    customer.addTransaction(order)
    check(customer.isVerifiedUser() is True, "Customer should be verified after adding a transaction.")
    check(customer.name == "Ava", "Customer name should be stored as provided.")

    # --- Input validation: reject bad names ---
    rejected = False
    try:
        Customers("")
    except (ValueError, TypeError):
        rejected = True
    check(rejected, "Empty customer name should be rejected.")

    rejected = False
    try:
        Customers("<script>alert('xss')</script>")
    except (ValueError, TypeError):
        rejected = True
    check(rejected, "Customer name with injection characters should be rejected.")

    # --- Input validation: reject bad product fields ---
    rejected = False
    try:
        Products("", 5.00, "Drinks", 4.0)
    except (ValueError, TypeError):
        rejected = True
    check(rejected, "Empty product name should be rejected.")

    rejected = False
    try:
        Products("Soda", -1.00, "Drinks", 4.0)
    except ValueError:
        rejected = True
    check(rejected, "Negative product price should be rejected.")

    rejected = False
    try:
        Products("Soda", 5.00, "Drinks", 6.0)
    except ValueError:
        rejected = True
    check(rejected, "Popularity rating above 5 should be rejected.")

    # --- Transaction: reject empty transaction in purchase history ---
    rejected = False
    try:
        history.addTransaction(Transactions())
    except ValueError:
        rejected = True
    check(rejected, "Adding an empty transaction to purchase history should be rejected.")

    print("All sanity checks passed.")


if __name__ == "__main__":
    main()
