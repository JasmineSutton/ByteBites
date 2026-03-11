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
        category_key = category.strip().lower()
        return [
            product
            for product in cls._catalog
            if product.category.strip().lower() == category_key
        ]


@dataclass
class Transactions:
    selectedItems: list[Products] = field(default_factory=list)

    def addItem(self, product: Products) -> None:
        if not isinstance(product, Products):
            raise TypeError("Transactions can only include Products.")
        self.selectedItems.append(product)

    def calculateTotalCost(self) -> float:
        return round(sum(product.price for product in self.selectedItems), 2)


@dataclass
class PurchaseHistory:
    transactions: list[Transactions] = field(default_factory=list)

    def addTransaction(self, new_transaction: Transactions) -> None:
        if not isinstance(new_transaction, Transactions):
            raise TypeError("PurchaseHistory only accepts Transactions.")
        if len(new_transaction.selectedItems) == 0:
            raise ValueError("Cannot add an empty transaction to purchase history.")
        self.transactions.append(new_transaction)

    def hasPastPurchases(self) -> bool:
        return any(len(transaction.selectedItems) > 0 for transaction in self.transactions)


@dataclass
class Customers:
    name: str
    purchaseHistory: PurchaseHistory = field(default_factory=PurchaseHistory)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Customer name cannot be empty.")

    def addTransaction(self, new_transaction: Transactions) -> None:
        self.purchaseHistory.addTransaction(new_transaction)

    def isVerifiedUser(self) -> bool:
        return self.purchaseHistory.hasPastPurchases()


if __name__ == "__main__":
    burger = Products("Spicy Burger", 8.99, "Entrees", 4.7)
    soda = Products("Large Soda", 2.49, "Drinks", 4.2)

    sample_transaction = Transactions()
    sample_transaction.addItem(burger)
    sample_transaction.addItem(soda)

    customer = Customers("Ava")
    customer.addTransaction(sample_transaction)

    print("Customer verified:", customer.isVerifiedUser())
    print("Transaction total:", sample_transaction.calculateTotalCost())
    print("Drink count:", len(Products.filterByCategory("drinks")))
