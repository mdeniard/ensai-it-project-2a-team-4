class TicketType:
    def __init__(
        self,
        id: int,
        name: str,
        price_multiplier: float,
        active: bool,
    ):
        self.id = id
        self.name = name
        self.price_multiplier = price_multiplier
        self.active = active
