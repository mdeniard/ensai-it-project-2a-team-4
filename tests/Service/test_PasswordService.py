from typing import Optional

import pytest

from src.Business_object.User import User
from src.Service.PasswordService import (
    UnknownUsernameError,
    WrongPasswordError,
    create_salt,
    hash_password,
    validate_username_password,
)

# Hash of the password "soleil1234" with the salt "jambon".
# hash_password adds the salt at the END of the password, so this is the SHA-256 of "soleil1234jambon".
JANJAK_HASH = "7877d4860ef88458096f549b618667d860540db5d59b1d153557d5cdbe1221e7"


# ---------- hash_password and create_salt ----------


def test_hash_password():
    # GIVEN a password and no salt
    # WHEN we hash it / THEN we get its SHA-256 hash
    assert hash_password("soleil1234") == "a88c648411492422ee9a1f4b03d3f5b71705499786f4415a59b51b255611ba50"


def test_hash_password_with_salt():
    # GIVEN a password and a salt
    # WHEN we hash them / THEN we get the hash of the password followed by the salt
    assert hash_password("soleil1234", "jambon") == JANJAK_HASH


def test_create_salt():
    # WHEN we create a salt / THEN it has 256 characters
    assert len(create_salt()) == 256


# ---------- validate_username_password (login) ----------


class MockUserRepo:
    """Fake UserRepo: only the user janjak exists, with the password "soleil1234" and the salt "jambon"."""

    def get_by_username(self, username: str) -> Optional[User]:
        if username == "janjak":
            return User(
                username="janjak",
                email="janjak@test.fr",
                password_hash=JANJAK_HASH,
                first_name="Jean",
                last_name="Jacques",
                salt="jambon",
                id=4,
            )
        return None


def test_validate_username_password_is_ok():
    # GIVEN janjak exists
    # WHEN he logs in with the right password
    janjak = validate_username_password("janjak", "soleil1234", MockUserRepo())

    # THEN we get his user
    assert janjak.id == 4


def test_validate_username_password_unknown_user():
    # GIVEN nobody is called Jean-Jacques
    # WHEN he tries to log in / THEN the login is refused
    with pytest.raises(UnknownUsernameError):
        validate_username_password("Jean-Jacques", "soleil1234", MockUserRepo())


def test_validate_username_password_incorrect_password():
    # GIVEN janjak exists
    # WHEN he logs in with a wrong password / THEN the login is refused
    with pytest.raises(WrongPasswordError):
        validate_username_password("janjak", "wrongpassword", MockUserRepo())
