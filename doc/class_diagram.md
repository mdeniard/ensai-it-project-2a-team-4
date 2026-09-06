```mermaid
---
title: Movie App
---
classDiagram
    class Movie{
        +name
        +date
        +describtion
        +duration
    }
    
    class User{
        <<abstract>>
        +name
        +password
    }

    class Customer {
    }

    class Administrator {
    }

    User <|-- Customer
    User <|-- Administrator

```