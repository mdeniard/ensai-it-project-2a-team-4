from pydantic import BaseModel


class ReservationModel(BaseModel):
    """What the customer sends to book a ticket.
    The customer is not sent: it is the logged-in user (found with the token).
    """

    screening_id: int
    ticket_type_id: int
