# ByteBites UML Class Diagram (Draft)

Source: bytebites_spec.md (Customer management, product fields, item collection/filtering, and transaction total-cost behavior).

```mermaid
classDiagram
    class Customer {
        +String name
        +PurchaseHistory purchaseHistory
        +bool isVerifiedUser()
    }

    class PurchaseHistory {
        +Transaction[] transactions
        +void addTransaction(transaction)
        +Transaction[] getTransactions()
    }

    class Product {
        +String name
        +decimal price
        +String category
        +int popularityRating
    }

    class Transaction {
        +Product[] selectedItems
        +void addItem(product)
        +decimal computeTotalCost()
    }

    Customer "1" *-- "1" PurchaseHistory : has
    PurchaseHistory "1" *-- "0..*" Transaction : stores
    Transaction "1" o-- "1..*" Product : contains
    Customer "1" --> "0..*" Transaction : initiates
```

Assumptions:
- Class names are normalized to singular UML style from the provided candidate list.
- Relationships and multiplicities include sensible inferences from the feature request text.