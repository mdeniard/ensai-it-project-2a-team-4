from typing import Optional

from src.DAO.UserRepo import UserRepo
from src.Business_object.User import User
from src.Service.PasswordService import check_password_strength, create_salt, hash_password, compare_password


class UserService:
    """Service that manages the users (registration, profile and password)."""

    def __init__(
        self,
        user_repo: Optional[UserRepo] = None,
    ):
        """Create the service.
        Args:
            user_repo (UserRepo, optional): Access to the users in the database.
                If none is given, a new UserRepo is created.
        """
        self.user_repo = user_repo or UserRepo()

    def get_all(self):
        """List the users of the database.
        Returns:
            list[User] of the users (the first 100, sorted by id), or an empty list if there is none.
        """
        return self.user_repo.get_all()

    def create_user(self, user: User) -> User:
        """Register a new user. The password is never saved as it is: a random salt is created
        and only the hash of the password and the salt is saved.
        Args:
            user (User): The user to create. Its password_hash field must still contain
                the password written by the user, it is replaced by its hash here.
        Returns:
            The saved User, with its id.
        """
        user.salt = create_salt()
        user.password_hash = hash_password(password=user.password_hash, salt=user.salt)
        return self.user_repo.create_user(user)

    def update_user(
        self, user_id: int, username: str, email: str, first_name: Optional[str] = None, last_name: Optional[str] = None
    ) -> User:
        """Update the profile of a user. The first name and the last name are only changed if they are given.
        Args:
            user_id (int): The id of the user to update.
            username (str): The new username.
            email (str): The new email.
            first_name (str, optional): The new first name (unchanged if none is given).
            last_name (str, optional): The new last name (unchanged if none is given).
        Returns:
            The updated User.
        """
        existing_user = self.user_repo.get_by_id(user_id)
        if not existing_user:
            raise ValueError("Utilisateur introuvable")

        existing_user.username = username
        existing_user.email = email
        if first_name is not None:
            existing_user.first_name = first_name
        if last_name is not None:
            existing_user.last_name = last_name

        return self.user_repo.update_user(existing_user)

    def change_password(self, user_id: int, old_password: str, new_password: str) -> None:
        """Change the password of a user. The current password must be given and the new one
        must be strong enough. A new salt is created for the new password.
        Args:
            user_id (int): The id of the user.
            old_password (str): The current password, to check that the user is the owner of the account.
            new_password (str): The new password (at least 8 characters).
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if not compare_password(old_password, user.salt, user.password_hash):
            raise PermissionError("Wrong current password")

        check_password_strength(password=new_password)

        new_salt = create_salt()
        new_hash = hash_password(new_password, new_salt)
        self.user_repo.update_password(user_id, new_hash, new_salt)

    def delete_user(self, user_id: int) -> bool:
        """Delete a user. His reservations and his reviews are deleted too.
        Args:
            user_id (int): The id of the user to delete.
        Returns:
            True if the user was deleted.
        """
        if not self.user_repo.get_by_id(user_id):
            raise ValueError("Utilisateur introuvable")
        return self.user_repo.delete_user(user_id)

    def get_user(self, user_id: int) -> User | None:
        """Find a user by his id.
        Args:
            user_id (int): The id of the user.
        Returns:
            The User, or None if no user has this id.
        """
        return self.user_repo.get_by_id(user_id)