import pytest

from src.Business_object.User import User
from src.Service.PasswordService import hash_password
from src.Service.UserService import UserService

# These tests use a fake repo instead of the database

# Hash of the password "soleil1234" with the salt "jambon" (the salt is added at the end of the password)
ALICE_HASH = "7877d4860ef88458096f549b618667d860540db5d59b1d153557d5cdbe1221e7"


class MockUserRepo:
    """Fake UserRepo: only the user 5 (alice, password "soleil1234") exists.
    It remembers what the service saved, so that we can check it in the tests.
    """

    def __init__(self):
        self.alice = User(
            username="alice",
            email="alice@test.fr",
            password_hash=ALICE_HASH,
            first_name="Alice",
            last_name="Martin",
            salt="jambon",
            id=5,
        )
        self.created_user = None
        self.updated_user = None
        self.new_password = None
        self.deleted_user_id = None

    def get_by_id(self, user_id):
        if user_id == 5:
            return self.alice
        return None

    def create_user(self, user):
        # The database would give an id to the new user
        user.id = 1
        self.created_user = user
        return user

    def update_user(self, user):
        self.updated_user = user
        return user

    def update_password(self, user_id, password_hash, salt):
        self.new_password = {"user_id": user_id, "password_hash": password_hash, "salt": salt}
        return True

    def delete_user(self, user_id):
        self.deleted_user_id = user_id
        return True


# ---------- get_all ----------


def test_get_all_returns_users():
    # GIVEN the repository has some users
    user_repo = MockUserRepo()
    user_repo.get_all = lambda: [user_repo.alice]
    user_service = UserService(user_repo)

    # WHEN we list the users
    result = user_service.get_all()

    # THEN we get them
    assert result == [user_repo.alice]


def test_get_all_returns_empty_list_when_no_users():
    # GIVEN there is no user in the database
    user_repo = MockUserRepo()
    user_repo.get_all = lambda: []
    user_service = UserService(user_repo)

    # WHEN we list the users
    result = user_service.get_all()

    # THEN we get an empty list
    assert result == []


# ---------- get_user ----------


def test_get_user_returns_user_when_found():
    # GIVEN alice exists
    user_repo = MockUserRepo()
    user_service = UserService(user_repo)

    # WHEN we look her up by id
    result = user_service.get_user(5)

    # THEN we get her
    assert result == user_repo.alice


def test_get_user_returns_none_when_not_found():
    # GIVEN user 99 does not exist
    user_repo = MockUserRepo()
    user_service = UserService(user_repo)

    # WHEN we look him up by id
    result = user_service.get_user(99)

    # THEN we get None
    assert result is None


# ---------- create_user ----------


def test_create_user_never_saves_the_password():
    # GIVEN a new user who wrote the password "soleil1234"
    user_repo = MockUserRepo()
    user_service = UserService(user_repo)
    new_user = User("bob", "bob@test.fr", "soleil1234", "Bob", "Durand")

    # WHEN he registers
    user_service.create_user(new_user)

    # THEN the password itself is not saved, only its hash with a new random salt
    saved_user = user_repo.created_user
    assert saved_user.password_hash != "soleil1234"
    assert len(saved_user.salt) == 256
    assert saved_user.password_hash == hash_password("soleil1234", saved_user.salt)


def test_create_user_password_too_short():
    # GIVEN a new user who wrote a password of less than 8 characters
    user_repo = MockUserRepo()
    user_service = UserService(user_repo)
    new_user = User("bob", "bob@test.fr", "court", "Bob", "Durand")

    # WHEN he registers / THEN ValueError and nothing is saved
    with pytest.raises(ValueError, match="at least 8 characters"):
        user_service.create_user(new_user)
    assert user_repo.created_user is None


# ---------- update_user ----------


def test_update_user_keeps_names_when_not_given():
    # GIVEN alice exists
    user_repo = MockUserRepo()
    user_service = UserService(user_repo)

    # WHEN she changes her username and email, without giving her first and last names
    updated = user_service.update_user(5, "alice2", "alice2@test.fr")

    # THEN the username and email change, but her first and last names are kept
    assert updated.username == "alice2"
    assert updated.email == "alice2@test.fr"
    assert updated.first_name == "Alice"
    assert updated.last_name == "Martin"


def test_update_user_changes_names_when_given():
    # GIVEN alice exists
    user_service = UserService(MockUserRepo())

    # WHEN she gives a new first name and a new last name
    updated = user_service.update_user(5, "alice", "alice@test.fr", first_name="Alicia", last_name="Durand")

    # THEN they are changed
    assert updated.first_name == "Alicia"
    assert updated.last_name == "Durand"


def test_update_user_unknown():
    # GIVEN user 99 does not exist
    user_repo = MockUserRepo()
    user_service = UserService(user_repo)

    # WHEN we update it / THEN ValueError and nothing is saved
    with pytest.raises(ValueError):
        user_service.update_user(99, "nobody", "nobody@test.fr")
    assert user_repo.updated_user is None


# ---------- change_password ----------


def test_change_password_ok():
    # GIVEN alice exists with the password "soleil1234"
    user_repo = MockUserRepo()
    user_service = UserService(user_repo)

    # WHEN she gives her current password and a new strong one
    user_service.change_password(5, "soleil1234", "nouveaumotdepasse")

    # THEN the new password is saved as a hash, with a new salt
    saved = user_repo.new_password
    assert saved["user_id"] == 5
    assert saved["salt"] != "jambon"
    assert saved["password_hash"] == hash_password("nouveaumotdepasse", saved["salt"])


def test_change_password_wrong_current_password():
    # GIVEN alice exists with the password "soleil1234"
    user_repo = MockUserRepo()
    user_service = UserService(user_repo)

    # WHEN she gives a wrong current password / THEN PermissionError and nothing is saved
    with pytest.raises(PermissionError):
        user_service.change_password(5, "wrongpassword", "nouveaumotdepasse")
    assert user_repo.new_password is None


def test_change_password_new_password_too_short():
    # GIVEN alice exists with the password "soleil1234"
    user_repo = MockUserRepo()
    user_service = UserService(user_repo)

    # WHEN her new password has less than 8 characters / THEN it is refused and nothing is saved
    with pytest.raises(ValueError, match="at least 8 characters"):
        user_service.change_password(5, "soleil1234", "court")
    assert user_repo.new_password is None


def test_change_password_unknown_user():
    # GIVEN user 99 does not exist
    user_repo = MockUserRepo()
    user_service = UserService(user_repo)

    # WHEN we change its password / THEN ValueError and nothing is saved
    with pytest.raises(ValueError):
        user_service.change_password(99, "soleil1234", "nouveaumotdepasse")
    assert user_repo.new_password is None


# ---------- delete_user ----------


def test_delete_user_ok():
    # GIVEN alice exists
    user_repo = MockUserRepo()
    user_service = UserService(user_repo)

    # WHEN she deletes her account / THEN it is deleted
    assert user_service.delete_user(5) is True
    assert user_repo.deleted_user_id == 5


def test_delete_user_unknown():
    # GIVEN user 99 does not exist
    user_repo = MockUserRepo()
    user_service = UserService(user_repo)

    # WHEN we delete it / THEN ValueError and nothing is deleted
    with pytest.raises(ValueError):
        user_service.delete_user(99)
    assert user_repo.deleted_user_id is None
