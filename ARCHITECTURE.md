# Architecture

``` mermaid
---
title:
---
graph LR
    User((User))

    subgraph App ["Python App"]
        CTL("Controllers")
        SVC("Services")
        DAO("DAO")
        MDL("Models")
    end

    DB[("Database<br/>(PostgreSQL)")]

    subgraph External ["External Services"]
        MDBAPI["TMDb API"]
    end
    
    SVC --> MDBAPI
    User --> CTL
    CTL --> SVC
    SVC --> DAO
    DAO --> DB

    MDL <-.- CTL
    MDL <-.- SVC
    MDL <-.- DAO
```