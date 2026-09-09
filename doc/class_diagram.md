```mermaid
---
title: Movie App - Python Class Diagram
---
classDiagram
    class User {
        <<abstract>>
        +id: uuid.UUID
        +email: str
        +password_hash: str
        +first_name: str
        +last_name: str
        +created_at: datetime.datetime
    }

    class Customer {
    }

    class Administrator {
    }
    
    User <|-- Customer
    User <|-- Administrator

    class Movie {
        +id: uuid.UUID
        +imdb_id: str
        +title: str
        +description: str
        +duration_minutes: int
        +release_date: datetime.date
        +rating: decimal.Decimal
        +poster_url: str
    }

    class Room {
        +id: uuid.UUID
        +room_number: int
        +capacity: int
    }

    class Screening {
        +id: uuid.UUID
        +movie_id: uuid.UUID
        +room_id: uuid.UUID
        +start_time: datetime.datetime
        +end_time: datetime.datetime
        +ticket_price: decimal.Decimal
    }

    class Reservation {
        +id: uuid.UUID
        +customer_id: uuid.UUID
        +screening_id: uuid.UUID
        +total_amount: decimal.Decimal
        +payment_status: str
        +reserved_at: datetime.datetime
    }

    class Review {
        +id: uuid.UUID
        +customer_id: uuid.UUID
        +movie_id: uuid.UUID
        +rating: int
        +comment: str
        +created_at: datetime.datetime
    }

    class PaymentTransaction {
        +id: uuid.UUID
        +reservation_id: uuid.UUID
        +stripe_payment_intent_id: str
        +amount: decimal.Decimal
        +status: str
        +created_at: datetime.datetime
    }
```