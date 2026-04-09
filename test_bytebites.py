from decimal import Decimal

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

    assert order.calculateTotalCost() == Decimal("16.47")


def test_calculate_total_cost_empty_transaction_returns_zero() -> None:
    order = Transactions()

    assert order.calculateTotalCost() == Decimal("0.00")


def test_filter_by_category_is_case_insensitive_and_trims_input() -> None:
    Products("Spicy Burger", 8.99, "Entrees", 4.7)
    Products("Large Soda", 2.49, "Drinks", 4.2)
    Products("Chocolate Shake", 4.99, "Drinks", 4.5)

    drinks = Products.filterByCategory("  dRiNkS  ")

    assert len(drinks) == 2
    assert [product.name for product in drinks] == ["Large Soda", "Chocolate Shake"]


def test_filter_by_category_returns_empty_list_for_unknown_category() -> None:
    Products("Spicy Burger", 8.99, "Entrees", 4.7)

    result = Products.filterByCategory("Desserts")

    assert result == []


def test_sort_by_price_returns_items_low_to_high() -> None:
    Products("Chocolate Shake", 4.99, "Drinks", 4.8)
    Products("Large Soda", 2.49, "Drinks", 4.2)
    Products("Spicy Burger", 8.99, "Entrees", 4.7)

    sorted_items = Products.sortByPrice()

    assert [item.name for item in sorted_items] == ["Large Soda", "Chocolate Shake", "Spicy Burger"]


def test_sort_by_popularity_returns_items_high_to_low() -> None:
    Products("Large Soda", 2.49, "Drinks", 4.2)
    Products("Spicy Burger", 8.99, "Entrees", 4.7)
    Products("Chocolate Shake", 4.99, "Drinks", 4.8)

    sorted_items = Products.sortByPopularity()

    assert [item.name for item in sorted_items] == ["Chocolate Shake", "Spicy Burger", "Large Soda"]


def test_sort_by_price_with_single_item_returns_that_item() -> None:
    Products("Spicy Burger", 8.99, "Entrees", 4.7)

    sorted_items = Products.sortByPrice()

    assert len(sorted_items) == 1
    assert sorted_items[0].name == "Spicy Burger"
