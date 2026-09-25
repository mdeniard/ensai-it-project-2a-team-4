from datetime import datetime
from pydantic import BaseModel

class Reservation(BaseModel):
    id: int
    customer_id: int
    screening_id: int
    ticket_type_id: int
    reserved_at: datetime
