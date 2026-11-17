"""Functions to hash and check passwords, and to validate the credentials of a login."""

from pydantic._internal._utils import ValueItems
import hashlib
import secrets
from typing import Optional

from src.DAO.UserRepo import UserRepo
from src.Business_object.User import User


def hash_password(password: str, salt="") -> str:
    """Hash a password with SHA-256, after adding the salt at its end.
    Args:
        password (str): The password to hash.
        salt (str): The random text added to the password before hashing (empty by default).
    Returns:
        The hash as a string of 64 hexadecimal characters.
    """
    password_bytes = password.encode("utf-8") + salt.encode("utf-8")
    hash_password = hashlib.sha256(password_bytes)
    return hash_password.hexdigest()


def create_salt() -> str:
    """Create a random salt, so that two users with the same password have different hashes.
    Returns:
        A random string of 256 hexadecimal characters.
    """
    return secrets.token_hex(128)


def check_password_strength(password: str):
    """Check that a password is long enough. The password is refused if it has less than 8 characters.
    Args:
        password (str): The password to check.
    """
    if len(password) < 8:
        raise Exception("Password length must be at least 8 characters")


def compare_password(password, salt, hash):
    """Check that a password matches a saved hash.
    Args:
        password (str): The password written by the user.
        salt (str): The salt saved with the user.
        hash (str): The hash saved in the database.
    Returns:
        True if the password, hashed with the salt, gives the saved hash, False otherwise.
    """
    return hash_password(password, salt) == hash


class InvalidCredentialsError(Exception):
    """Base class for login failures"""


class UnknownUsernameError(InvalidCredentialsError):
    """Username not found"""


class WrongPasswordError(InvalidCredentialsError):
    """Password does not match"""


def validate_username_password(username: str, password: str, user_repo: UserRepo) -> User:
    """Check the credentials of a user who wants to log in.
    The login is refused if the username is unknown or if the password is wrong.
    Args:
        username (str): The username written by the user.
        password (str): The password written by the user.
        user_repo (UserRepo): Access to the users in the database.
    Returns:
        The User whose credentials are correct.
    """
    user = user_repo.get_by_username(username=username)
    if user is None:
        raise UnknownUsernameError()
    if not compare_password(password, user.salt, user.password_hash):
        raise WrongPasswordError()
    return user