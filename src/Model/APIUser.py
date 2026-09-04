from pydantic import BaseModel


class APIUser(BaseModel):
    id: int
    username: str
