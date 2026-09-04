from typing import Optional

from src.DAO.UserRepo import UserRepo
from src.Model.User import User
from src.Service.PasswordService import check_password_strength, create_salt, hash_password


class UserService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    def create_user(self, username: str, password: str) -> User:
        ## TODO

        return

    def get_user(self, user_id: int) -> User | None:
        return self.user_repo.get_by_id(user_id)
