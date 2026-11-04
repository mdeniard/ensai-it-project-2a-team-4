from datetime import datetime
from typing import Optional

class Reservation:
    def __init__(
        self,
        customer_id: int,
        screening_id: int,
        ticket_type_id: int,
        reserved_at: datetime,
        id: Optional[int] = None,
    ):
        self.id = id
        self.customer_id = customer_id
        self.screening_id = screening_id
        self.ticket_type_id = ticket_type_id
        self.reserved_at = reserved_at

    def __str__(self) -> str:
        date_str = self.reserved_at.strftime("%Y-%m-%d %H:%M")
        return (
            f"Reservation #{self.id} "
            f"(Customer: {self.customer_id}, Screening: {self.screening_id}, Ticket Type: {self.ticket_type_id}) "
            f"made on {date_str}"
        )
