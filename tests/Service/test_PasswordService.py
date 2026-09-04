from typing import Optional

import pytest

from src.Model.User import User
from src.Service.PasswordService import create_salt, hash_password, validate_username_password


def test_hash_password():
    password = "soleil1234"
    hashed_password = hash_password(password)
    assert hashed_password == "a88c648411492422ee9a1f4b03d3f5b71705499786f4415a59b51b255611ba50"


def test_hash_password_with_salt():
    password = "soleil1234"
    salt = "jambon"
    hashed_password = hash_password(password, salt)
    assert hashed_password == "56d25b0190eb6fcdab76f20550aa3e85a37ee48d520ac70385ae3615deb7d53a"


def test_create_salt():
    salt = create_salt()
    assert len(salt) == 256


class MockUserRepo:
    def get_by_username(self, username: str) -> Optional[User]:
        if username == "janjak":
            return User(
                id=4,
                username="janjak",
                salt="jambon",
                password="56d25b0190eb6fcdab76f20550aa3e85a37ee48d520ac70385ae3615deb7d53a",
            )
        else:
            return None


user_repo = MockUserRepo()


def test_validate_username_password_is_ok():
    janjak = validate_username_password("janjak", "soleil1234", user_repo)
    assert janjak.id == 4


def test_validate_username_password_unknown_user():
    with pytest.raises(Exception) as exception_info:
        validate_username_password("Jean-Jacques", "soleil1234", user_repo)
    assert str(exception_info.value) == "user with username Jean-Jacques not found"


def test_validate_username_password_incorrect_password():
    with pytest.raises(Exception) as exception_info:
        validate_username_password("janjak", "wrongpassword", user_repo)
    assert str(exception_info.value) == "Incorrect password"
