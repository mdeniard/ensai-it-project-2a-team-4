from typing import Optional

from src.Business_object.User import User

from .DBConnector import DBConnector


class UserRepo:
    db_connector: DBConnector

    def __init__(self, db_connector: Optional[DBConnector] = None) -> None:
        self.db_connector = db_connector or DBConnector()

    def get_by_id(self, user_id: int) -> Optional[User]:
        raw_user = self.db_connector.sql_query("SELECT * from users WHERE id=%s", [user_id], "one")
        if raw_user is None:
            return None
        # pyrefly: ignore
        return User(**raw_user)

    def get_by_username(self, username: str) -> Optional[User]:
        raw_user = self.db_connector.sql_query("SELECT * from users WHERE username=%s", [username], "one")
        if raw_user is None:
            return None
        # pyrefly: ignore
        return User(**raw_user)

    def insert_into_db(self, user: User) -> User:
        raw_created_user = self.db_connector.sql_query(
        """
        INSERT INTO users (username, email, password_hash, salt, first_name, last_name, is_admin)
        VALUES (%(username)s, %(email)s, %(password_hash)s, %(salt)s, %(fisrt_name)s, %(last_name)s, %(is_admin)s)
        RETURNING *;
        """,
            {"username": user.username,
            "email": user.email,
            "password_hash": user.password_hash,
            "salt": user.salt,
            "fisrt_name": user.first_name,
            "last_name": user.last_name,
            "is_admin": user.is_admin},
            "one",
        )
        # pyrefly: ignore
        return User(**raw_created_user)
