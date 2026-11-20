from pydantic import BaseModel


class APIUser(BaseModel):
    """Public data of a user sent in the responses (never the password or the email)."""

    id: int
    username: str
