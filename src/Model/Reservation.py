from datetime import datetime

class Reservation:
    def __init__(
        self,
        id: int,
        customer_id: int,
        screening_id: int,
        ticket_type_id: int,
        reserved_at: datetime
    ):
        self.id = id
        self.customer_id = customer_id
        self.screening_id = screening_id
        self.ticket_type_id = ticket_type_id
        self.reserved_at = reserved_at
