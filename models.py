# Customers: Represents a user and links to their purchase history so the app can validate real users.
# PurchaseHistory: Stores a customer’s past transactions and supports checking whether purchases exist.
# Products: Represents menu items with name, price, category, and popularity rating for browsing/filtering.
# Transactions: Groups selected products into one purchase and calculates the total cost.

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import ClassVar

# --- Security constants ---
MAX_NAME_LENGTH = 100
MAX_CATEGORY_LENGTH = 50
MAX_CATALOG_SIZE = 10_000
MAX_TRANSACTION_ITEMS = 500
MAX_PURCHASE_HISTORY = 10_000
_SAFE_TEXT_RE = re.compile(r"^[\w\s\-'.&]+$", re.UNICODE)


def _sanitize_text(value: str, field_label: str, max_length: int) -> str:
    """Validate and sanitize a text field: type-check, strip, enforce length and character whitelist."""
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


def _to_decimal(value: float | int | str | Decimal, field_label: str) -> Decimal:
    """Convert a numeric value to a two-decimal-place Decimal safely."""
    if isinstance(value, float):
        value = str(round(value, 2))
    try:
        dec = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"{field_label} must be a valid number.")
    return dec


@dataclass
class Products:
    name: str
    price: float
    category: str
    popularityRating: float

    _catalog: ClassVar[list["Products"]] = []

    def __post_init__(self) -> None:
        """Validate and sanitize product fields, then register in the in-memory catalog."""
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
    def listCatalog(cls) -> tuple["Products", ...]:
        """Return an immutable snapshot of all products in the in-memory catalog."""
        return tuple(cls._catalog)

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
        """Add a product to this transaction after type-checking and enforcing size limits."""
        if not isinstance(product, Products):
            raise TypeError("Transactions can only include Products.")
        if len(self.selectedItems) >= MAX_TRANSACTION_ITEMS:
            raise OverflowError(f"A transaction cannot contain more than {MAX_TRANSACTION_ITEMS} items.")
        self.selectedItems.append(product)

    def calculateTotalCost(self) -> Decimal:
        """Compute the total cost using Decimal arithmetic to avoid floating-point errors."""
        total = sum(
            (_to_decimal(product.price, "price") for product in self.selectedItems),
            Decimal("0.00"),
        )
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass
class PurchaseHistory:
    transactions: list[Transactions] = field(default_factory=list)

    def addTransaction(self, new_transaction: Transactions) -> None:
        """Store a non-empty transaction in this purchase history with size-limit enforcement."""
        if not isinstance(new_transaction, Transactions):
            raise TypeError("PurchaseHistory only accepts Transactions.")
        if len(new_transaction.selectedItems) == 0:
            raise ValueError("Cannot add an empty transaction to purchase history.")
        if len(self.transactions) >= MAX_PURCHASE_HISTORY:
            raise OverflowError(f"Purchase history cannot exceed {MAX_PURCHASE_HISTORY} transactions.")
        self.transactions.append(new_transaction)

    def hasPastPurchases(self) -> bool:
        """Return True when there is at least one stored non-empty transaction."""
        return any(len(transaction.selectedItems) > 0 for transaction in self.transactions)


@dataclass
class Customers:
    name: str
    purchaseHistory: PurchaseHistory = field(default_factory=PurchaseHistory)

    def __post_init__(self) -> None:
        """Validate and sanitize the customer name."""
        self.name = _sanitize_text(self.name, "Customer name", MAX_NAME_LENGTH)

    def addTransaction(self, new_transaction: Transactions) -> None:
        """Add a transaction to this customer's purchase history."""
        self.purchaseHistory.addTransaction(new_transaction)

    def isVerifiedUser(self) -> bool:
        """A customer is verified when they have at least one past purchase."""
        return self.purchaseHistory.hasPastPurchases()


if __name__ == "__main__":
    Products.clearCatalog()

    Products("Spicy Burger", 8.99, "Entrees", 4.7)
    Products("Seasoned Fries", 3.49, "Sides", 4.4)
    Products("Large Soda", 2.49, "Drinks", 4.2)
    Products("Chocolate Shake", 4.99, "Drinks", 4.8)

    customers: list[Customers] = []

    def print_menu() -> None:
        menu = Products.listCatalog()
        print("\n--- ByteBites Menu ---")
        for i, item in enumerate(menu, start=1):
            print(f"  {i}. {item.name:<22} ${item.price:.2f}  ({item.category})")
        print("----------------------")

    def take_order(all_customers: list[Customers]) -> None:
        while True:
            raw_name = input("\nEnter your name: ").strip()
            try:
                customer = Customers(raw_name)
                break
            except (ValueError, TypeError) as e:
                print(f"  Invalid name: {e}")

        all_customers.append(customer)
        order = Transactions()

        while True:
            print_menu()
            menu = Products.listCatalog()
            while True:
                choice = input(f"Enter the number of the item to add (1-{len(menu)}): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(menu):
                    break
                print(f"  Please enter a number between 1 and {len(menu)}.")
            selected = menu[int(choice) - 1]
            order.addItem(selected)
            print(f"  Added: {selected.name}")

            again = input("Add another item? (yes/no): ").strip().lower()
            if again not in ("yes", "y"):
                break

        customer.addTransaction(order)
        print(f"\nOrder total: ${order.calculateTotalCost()}")
        print(f"Thanks, {customer.name}! Enjoy your meal!")

    while True:
        take_order(customers)
        done = input("\nNew customer, or is the entire order finished? (new/done): ").strip().lower()
        if done in ("done", "d"):
            print(f"\nAll orders complete. Customers served: {[c.name for c in customers]}")
            print("Goodbye!")
            break
