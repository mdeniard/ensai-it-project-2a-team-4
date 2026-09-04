import hashlib
import secrets
from typing import Optional

from src.DAO.UserRepo import UserRepo
from src.Model.User import User


def hash_password(password: str, salt: Optional[str] = None) -> str:
    ## TODO

    return "1234"


def create_salt() -> str:
    return secrets.token_hex(128)


def check_password_strength(password: str):
    if len(password) < 8:
        raise Exception("Password length must be at least 8 characters")


def validate_username_password(username: str, password: str, user_repo: UserRepo) -> User:
    user_with_username: Optional[User] = user_repo.get_by_username(username=username)
    ## TODO

    return user_with_username
