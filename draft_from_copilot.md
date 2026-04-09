```mermaid
classDiagram
    class Products {
        +String name
        +float price
        +String category
        +float popularityRating
        -List~Products~ _catalog$
        +filterByCategory(category: str) List~Products~$
        +listCatalog() tuple~Products~$
        +clearCatalog() None$
        +sortByPrice(descending: bool) List~Products~$
        +sortByPopularity(descending: bool) List~Products~$
    }

    class Transactions {
        +List~Products~ selectedItems
        +addItem(product: Products) None
        +calculateTotalCost() Decimal
    }

    class PurchaseHistory {
        +List~Transactions~ transactions
        +addTransaction(new_transaction: Transactions) None
        +hasPastPurchases() bool
    }

    class Customers {
        +String name
        +PurchaseHistory purchaseHistory
        +addTransaction(new_transaction: Transactions) None
        +isVerifiedUser() bool
    }

    Customers "1" *-- "1" PurchaseHistory : has
    PurchaseHistory "1" *-- "0..*" Transactions : stores
    Transactions "1" o-- "0..*" Products : contains
```

**Relationship notes:**
- `Customers ──* PurchaseHistory` — composition; a customer owns exactly one history
- `PurchaseHistory ──* Transactions` — composition; history is nothing without its transactions
- `Transactions ──o Products` — aggregation; items exist independently in the catalog, a transaction just references them

The `$` marker on `Products` methods denotes class-level (`@classmethod`) operations, since the catalog is a `ClassVar` shared across all instances.