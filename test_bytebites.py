from models import Products, Transactions


def setup_function(_function) -> None:
    Products.clearCatalog()


def test_calculate_total_cost_sums_items_and_rounds_to_two_decimals() -> None:
    burger = Products("Spicy Burger", 8.99, "Entrees", 4.7)
    soda = Products("Large Soda", 2.49, "Drinks", 4.2)
    shake = Products("Chocolate Shake", 4.99, "Drinks", 4.5)

    order = Transactions()
    order.addItem(burger)
    order.addItem(soda)
    order.addItem(shake)

    assert order.calculateTotalCost() == 16.47


def test_calculate_total_cost_empty_transaction_returns_zero() -> None:
    order = Transactions()

    assert order.calculateTotalCost() == 0


def test_filter_by_category_is_case_insensitive_and_trims_input() -> None:
    Products("Spicy Burger", 8.99, "Entrees", 4.7)
    Products("Large Soda", 2.49, "Drinks", 4.2)
    Products("Chocolate Shake", 4.99, "Drinks", 4.5)

    drinks = Products.filterByCategory("  dRiNkS  ")

    assert len(drinks) == 2
    assert [product.name for product in drinks] == ["Large Soda", "Chocolate Shake"]
