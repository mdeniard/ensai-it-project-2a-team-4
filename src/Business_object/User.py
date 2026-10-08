from datetime import datetime
from typing import Optional


class User():
    def __init__(
        self,
        username: str,
        email: str,
        password_hash: str,
        salt: str,
        first_name: str,
        last_name: str,
        is_admin: bool = False,
        id: Optional[int] = None
    ):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.salt = salt
        self.first_name = first_name
        self.last_name = last_name
        self.is_admin = is_admin
