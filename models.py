# Customers: Represents a user and links to their purchase history so the app can validate real users.
# PurchaseHistory: Stores a customer’s past transactions and supports checking whether purchases exist.
# Products: Represents menu items with name, price, category, and popularity rating for browsing/filtering.
# Transactions: Groups selected products into one purchase and calculates the total cost.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class Products:
    name: str
    price: float
    category: str
    popularityRating: float

    _catalog: ClassVar[list["Products"]] = []

    def __post_init__(self) -> None:
        """Validate product fields and register this item in the in-memory catalog."""
        if self.price < 0:
            raise ValueError("Product price cannot be negative.")
        if not (0 <= self.popularityRating <= 5):
            raise ValueError("Popularity rating must be between 0 and 5.")
        if not self.category.strip():
            raise ValueError("Product category cannot be empty.")
        if not self.name.strip():
            raise ValueError("Product name cannot be empty.")
        type(self)._catalog.append(self)

    @classmethod
    def filterByCategory(cls, category: str) -> list["Products"]:
        """Return catalog products whose category matches the input (case-insensitive)."""
        category_key = category.strip().lower()
        return [
            product
            for product in cls._catalog
            if product.category.strip().lower() == category_key
        ]

    @classmethod
    def clearCatalog(cls) -> None:
        """Remove all products from the in-memory catalog."""
        cls._catalog.clear()

    @classmethod
    def listCatalog(cls) -> list["Products"]:
        """Return a copy of all products in the in-memory catalog."""
        return list(cls._catalog)

    @classmethod
    def sortByPrice(cls, descending: bool = False) -> list["Products"]:
        """Return catalog products sorted by price, low-to-high by default."""
        return sorted(cls._catalog, key=lambda product: product.price, reverse=descending)

    @classmethod
    def sortByPopularity(cls, descending: bool = True) -> list["Products"]:
        """Return catalog products sorted by popularity, high-to-low by default."""
        return sorted(
            cls._catalog,
            key=lambda product: product.popularityRating,
            reverse=descending,
        )


@dataclass
class Transactions:
    selectedItems: list[Products] = field(default_factory=list)

    def addItem(self, product: Products) -> None:
        """Add a product to this transaction."""
        if not isinstance(product, Products):
            raise TypeError("Transactions can only include Products.")
        self.selectedItems.append(product)

    def calculateTotalCost(self) -> float:
        """Compute the total cost of all selected items."""
        return round(sum(product.price for product in self.selectedItems), 2)


@dataclass
class PurchaseHistory:
    transactions: list[Transactions] = field(default_factory=list)

    def addTransaction(self, new_transaction: Transactions) -> None:
        """Store a non-empty transaction in this purchase history."""
        if not isinstance(new_transaction, Transactions):
            raise TypeError("PurchaseHistory only accepts Transactions.")
        if len(new_transaction.selectedItems) == 0:
            raise ValueError("Cannot add an empty transaction to purchase history.")
        self.transactions.append(new_transaction)

    def hasPastPurchases(self) -> bool:
        """Return True when there is at least one stored non-empty transaction."""
        return any(len(transaction.selectedItems) > 0 for transaction in self.transactions)


@dataclass
class Customers:
    name: str
    purchaseHistory: PurchaseHistory = field(default_factory=PurchaseHistory)

    def __post_init__(self) -> None:
        """Validate required customer fields."""
        if not self.name.strip():
            raise ValueError("Customer name cannot be empty.")

    def addTransaction(self, new_transaction: Transactions) -> None:
        """Add a transaction to this customer's purchase history."""
        self.purchaseHistory.addTransaction(new_transaction)

    def isVerifiedUser(self) -> bool:
        """A customer is verified when they have at least one past purchase."""
        return self.purchaseHistory.hasPastPurchases()


if __name__ == "__main__":
    Products.clearCatalog()

    burger = Products("Spicy Burger", 8.99, "Entrees", 4.7)
    fries = Products("Seasoned Fries", 3.49, "Sides", 4.4)
    soda = Products("Large Soda", 2.49, "Drinks", 4.2)
    shake = Products("Chocolate Shake", 4.99, "Drinks", 4.8)

    menu_by_price = Products.sortByPrice()
    menu_by_popularity = Products.sortByPopularity()
    drinks_menu = Products.filterByCategory("drinks")

    order = Transactions()
    order.addItem(burger)
    order.addItem(soda)
    order.addItem(fries)

    customer = Customers("Ava")
    customer.addTransaction(order)

    print("Menu sorted by price:", [item.name for item in menu_by_price])
    print("Menu sorted by popularity:", [item.name for item in menu_by_popularity])
    print("Drinks category:", [item.name for item in drinks_menu])
    print("Order total:", order.calculateTotalCost())
    print("Customer verified:", customer.isVerifiedUser())
