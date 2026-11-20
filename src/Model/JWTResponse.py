from pydantic import BaseModel


class JWTResponse(BaseModel):
    """Response of the login: the JWT access token."""

    access_token: str
