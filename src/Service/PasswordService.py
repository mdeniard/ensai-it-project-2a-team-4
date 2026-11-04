from pydantic._internal._utils import ValueItems
import hashlib
import secrets
from typing import Optional

from src.DAO.UserRepo import UserRepo
from src.Business_object.User import User


def hash_password(password: str, salt="") -> str:
    password_bytes = password.encode("utf-8") + salt.encode("utf-8")
    hash_password = hashlib.sha256(password_bytes)
    return hash_password.hexdigest()


def create_salt() -> str:
    return secrets.token_hex(128)


def check_password_strength(password: str):
    if len(password) < 8:
        raise Exception("Password length must be at least 8 characters")

def compare_password(password, salt, hash):
    return hash_password(password, salt) == hash


class InvalidCredentialsError(Exception):
    """Base class for login failures"""

class UnknownUsernameError(InvalidCredentialsError):
    """Username not found"""

class WrongPasswordError(InvalidCredentialsError):
    """Password does not match"""

def validate_username_password(username: str, password: str, user_repo: UserRepo) -> User:
    user = user_repo.get_by_username(username=username)
    if user is None:
        raise UnknownUsernameError()
    if not compare_password(password, user.salt, user.password_hash):
        raise WrongPasswordError()
    return user
