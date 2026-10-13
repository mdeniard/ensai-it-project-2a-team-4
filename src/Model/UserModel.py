from pydantic import BaseModel
from typing import Optional


class UserModel(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str

class UpdateUserModel(BaseModel):
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class ChangeUserPasswordModel(BaseModel):
    old_password: str
    new_password: str
