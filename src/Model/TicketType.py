from pydantic import BaseModel

class TicketType(BaseModel):
    id: int
    name: str
    price_multiplier: float
    active: bool
