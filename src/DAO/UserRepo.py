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

    def create_user(self, user: User) -> User:
        raw_created_user = self.db_connector.sql_query(
        """
        INSERT INTO users (username, email, password_hash, salt, first_name, last_name, is_admin)
        VALUES (%(username)s, %(email)s, %(password_hash)s, %(salt)s, %(first_name)s, %(last_name)s, %(is_admin)s)
        RETURNING *;
        """,
            {"username": user.username,
            "email": user.email,
            "password_hash": user.password_hash,
            "salt": user.salt,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_admin": user.is_admin},
            "one",
        )
        # pyrefly: ignore
        return User(**raw_created_user)

    def update_user(self, user: User) -> User:
        raw_updated_user = self.db_connector.sql_query(
            """
            UPDATE users
            SET username = %(username)s,
                email = %(email)s,
                password_hash = %(password_hash)s,
                salt = %(salt)s,
                first_name = %(first_name)s,
                last_name = %(last_name)s,
                is_admin = %(is_admin)s
            WHERE id = %(id)s
            RETURNING *;
            """,
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "password_hash": user.password_hash,
                "salt": user.salt,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_admin": user.is_admin,
            },
            "one",
        )
        # pyrefly: ignore
        return User(**raw_updated_user)

    def update_password(self, user_id: int, password_hash: str, salt: str) -> bool:
        """
        Updates a user's password hash and salt.
        Returns True if a user was updated, False if no user matched.
        """
        raw_updated = self.db_connector.sql_query(
            """
            UPDATE users
            SET password_hash = %(password_hash)s,
                salt = %(salt)s
            WHERE id = %(id)s
            RETURNING id;
            """,
            {"id": user_id, "password_hash": password_hash, "salt": salt},
            "one",
        )
        return raw_updated is not None

    def delete_user(self, user_id: int) -> bool:
        """
        Deletes a user by id. Returns True if a user was deleted, False if no user matched.
        """
        raw_deleted_user = self.db_connector.sql_query(
            """
            DELETE FROM users
            WHERE id = %(id)s
            RETURNING id;
            """,
            {"id": user_id},
            "one",
        )
        # pyrefly: ignore
        return raw_deleted_user is not None
