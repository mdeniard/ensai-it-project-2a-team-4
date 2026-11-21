import os
import time

import jwt
from jwt import ExpiredSignatureError

from src.Model.JWTResponse import JWTResponse


class JwtService:
    """Handler for JWT (JSON Web Token) creation and validation.
    A token is signed with a secret key, so that nobody can create or change one without knowing the secret.
    """

    def __init__(self, secret: str = "", algorithm: str = "HS256"):
        """Create the service.
        Args:
            secret (str): The secret key used to sign and check the tokens.
                If none is given, it is read from the JWT_SECRET variable of the .env file.
            algorithm (str): The signing algorithm (HS256 by default).
        """
        if secret == "":
            self.secret = os.environ["JWT_SECRET"]
        else:
            self.secret = secret
        self.algorithm = algorithm

    def encode_jwt(self, user_id: int) -> JWTResponse:
        """Create an access token for a user, valid for 10 minutes.
        Args:
            user_id (int): The database id of the user who has just logged in.
        Returns:
            A JWTResponse containing the access token.
        """
        payload = {"user_id": user_id, "expiry_timestamp": time.time() + 600}
        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)

        return JWTResponse(access_token=token)

    def decode_jwt(self, token: str) -> dict:
        """Read the content of a token. The token is refused if its signature is not valid
        (token changed, or signed with another secret). The expiry time is not checked here.
        Args:
            token (str): The access token sent by the user.
        Returns:
            The content of the token as a dict (user_id and expiry_timestamp).
        """
        return jwt.decode(token, self.secret, algorithms=[self.algorithm])

    def validate_user_jwt(self, token: str) -> str:
        """Check a token and find the user it belongs to.
        The token is refused if it is invalid or expired.
        Args:
            token (str): The access token sent by the user.
        Returns:
            The id of the user authenticated by the token.
        """
        decoded_jwt = self.decode_jwt(token)
        if decoded_jwt["expiry_timestamp"] < time.time():
            raise ExpiredSignatureError("Expired JWT")
        return decoded_jwt["user_id"]
