from models import Customers, Products, PurchaseHistory, Transactions


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    Products.clearCatalog()

    burger = Products("Spicy Burger", 8.99, "Entrees", 4.7)
    soda = Products("Large Soda", 2.49, "Drinks", 4.2)
    shake = Products("Chocolate Shake", 4.99, "Drinks", 4.5)

    order = Transactions()
    order.addItem(burger)
    order.addItem(soda)
    order.addItem(shake)

    history = PurchaseHistory()
    history.addTransaction(order)

    customer = Customers("Ava")
    customer.addTransaction(order)

    drinks = Products.filterByCategory("drinks")
    by_price = Products.sortByPrice()
    by_popularity = Products.sortByPopularity()
    full_catalog = Products.listCatalog()

    check(len(full_catalog) == 3, "Expected three products in the catalog.")
    check(len(drinks) == 2, "Expected two drink products in the catalog.")
    check(order.calculateTotalCost() == 16.47, "Unexpected total cost.")
    check(history.hasPastPurchases() is True, "History should report past purchases.")
    check(customer.isVerifiedUser() is True, "Customer should be verified after transaction.")
    check(by_price[0].name == "Large Soda", "Price sort should start with the cheapest item.")
    check(
        by_popularity[0].name == "Spicy Burger",
        "Popularity sort should start with the highest-rated item.",
    )

    snapshot = {
        "customer": customer.name,
        "verified": customer.isVerifiedUser(),
        "transaction_items": [item.name for item in order.selectedItems],
        "transaction_total": order.calculateTotalCost(),
        "drink_names": [product.name for product in drinks],
        "sorted_by_price": [product.name for product in by_price],
        "sorted_by_popularity": [product.name for product in by_popularity],
    }

    print("Sanity run passed.")
    print(snapshot)


if __name__ == "__main__":
    main()
