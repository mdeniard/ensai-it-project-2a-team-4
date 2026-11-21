from typing import Optional

from pydantic import BaseModel


class UserModel(BaseModel):
    """Body of the request to register a new user."""

    username: str
    email: str
    password: str
    first_name: str
    last_name: str


class UpdateUserModel(BaseModel):
    """Body of the request to update one's profile (first and last names are optional)."""

    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class ChangeUserPasswordModel(BaseModel):
    """Body of the request to change one's password."""

    old_password: str
    new_password: str
