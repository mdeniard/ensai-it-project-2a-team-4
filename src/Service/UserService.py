from typing import Optional

from src.DAO.UserRepo import UserRepo
from src.Business_object.User import User
from src.Service.PasswordService import check_password_strength, create_salt, hash_password, check_password


class UserService:
    def __init__(
        self,
        user_repo: Optional[UserRepo] = None,
    ):
        self.user_repo = user_repo or UserRepo()

    def create_user(self, user: User) -> User:
        user.salt = create_salt()
        user.password_hash = hash_password(password=user.password_hash, salt=user.salt)
        return self.user_repo.create_user(user)

    def update_user(
        self,
        user_id: int,
        username: str,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        existing_user = self.user_repo.get_by_id(user_id)
        if not existing_user:
            raise ValueError("Utilisateur introuvable")

        existing_user.username = username
        existing_user.email = email
        existing_user.first_name = first_name
        existing_user.last_name = last_name

        return self.user_repo.update_user(existing_user)

    def change_password(self, user_id: int, old_password: str, new_password: str) -> None:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if not check_password(old_password, user.salt, user.password_hash):
            raise PermissionError("Wrong current password")

        check_password_strength(password=new_password)

        new_salt = create_salt()
        new_hash = hash_password(new_password, new_salt)
        self.user_repo.update_password(user_id, new_hash, new_salt)

    def delete_user(
        self,
        user_id: int
    ) -> bool:
        if not self.user_repo.get_by_id(user_id):
            raise ValueError("Utilisateur introuvable")
        return self.user_repo.delete_user(user_id)

    def get_user(self, user_id: int) -> User | None:
        return self.user_repo.get_by_id(user_id)
