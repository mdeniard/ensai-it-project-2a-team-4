# Diagramme d'activité

``` mermaid
stateDiagram
    admin : Admin
    adminlogin : Login
    adminsignup : Sign Up
    menu_admin : Admin Menu
    customer : Customer
    customerlogin : Login
    customersignup : Sign Up
    menu_customer : Customer Menu

    menu_account : Account Menu
    menu_schedule : Schedule Menu
    admin_logout : Logout

    research : Research
    book : Book a session
    review : Review
    bymovie : By Movie
    bydate : By Date
    customer_logout : Logout
    
    [*] --> Home
    
    Home --> Profile
    Profile --> admin
    Profile --> customer

    admin --> adminlogin
    admin --> adminsignup

    customer --> customerlogin
    customer --> customersignup
    
    Home --> quit
    quit --> [*]

    adminlogin --> menu_admin
    
    state menu_admin {
        [*] --> menu_account
      [*] --> menu_schedule
        [*] --> admin_logout
        admin_logout --> [*]: return to home
    }

    customerlogin --> menu_customer

    state menu_customer {
        [*] --> research
      research --> bymovie
      bymovie --> book
      research --> bydate
      bydate --> book
        [*] --> review
        [*] --> customer_logout
        customer_logout --> [*]: return to home
    }
```