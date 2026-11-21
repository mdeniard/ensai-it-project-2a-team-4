from typing import Optional


class TicketType:
    """A type of ticket (Normal, ENSAI Student...).
    The base price of the screening is multiplied by price_multiplier."""

    def __init__(
        self,
        name: str,
        price_multiplier: float,
        active: bool,
        id: Optional[int] = None,
    ):
        self.id = id
        self.name = name
        self.price_multiplier = price_multiplier
        self.active = active

    def __str__(self) -> str:
        status = "Active" if self.active else "Inactive"
        return f"TicketType #{self.id}: {self.name} (Multiplier: {self.price_multiplier}x, Status: {status})"
