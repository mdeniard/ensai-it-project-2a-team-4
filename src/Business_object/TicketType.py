from typing import Optional


class TicketType:
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
        return (
            f"TicketType #{self.id}: {self.name} "
            f"(Multiplier: {self.price_multiplier}x, Status: {status})"
        )
