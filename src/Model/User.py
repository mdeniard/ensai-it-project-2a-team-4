from pydantic import BaseModel
from datetime import datetime


class User(BaseModel):
    id: int
    user: str
    email: str
    password_hash: str
    first_name: str
    last_name: str
    created_at: datetime
    is_admin: bool
