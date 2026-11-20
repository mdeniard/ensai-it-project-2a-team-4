from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from psycopg2.errors import UniqueViolation

from src.Business_object.User import User
from src.Model.APIUser import APIUser
from src.Model.JWTResponse import JWTResponse
from src.Model.UserModel import ChangeUserPasswordModel, UpdateUserModel, UserModel
from src.Service.PasswordService import UnknownUsernameError, WrongPasswordError, validate_username_password

from .init_app import jwt_service, user_repo, user_service
from .JWTBearer import JWTBearer

# ---------- Helpers used by every protected route ----------


def to_api_user(user: User) -> APIUser:
    """Keep only the public fields of a user (id and username), to send them in a response.
    Args:
        user (User): A user read from the database (so they always have an id).
    Returns:
        The APIUser of this user.
    """
    # pyrefly: ignore
    return APIUser(username=user.username, id=user.id)


def get_user_from_credentials(credentials: HTTPAuthorizationCredentials) -> APIUser:
    """Find the logged-in user from the token sent with the request.
    Args:
        credentials (HTTPAuthorizationCredentials): The token, already checked by JWTBearer.
    Returns:
        The APIUser (id and username) of the logged-in user.
        Raises a 404 error if the user of the token does not exist anymore (account deleted).
    """
    token = credentials.credentials
    user_id = int(jwt_service.validate_user_jwt(token))
    user: User | None = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return to_api_user(user)


def get_admin_from_credentials(credentials: HTTPAuthorizationCredentials) -> APIUser:
    """Find the logged-in user from the token, and check that they are an administrator.
    Args:
        credentials (HTTPAuthorizationCredentials): The token, already checked by JWTBearer.
    Returns:
        The APIUser (id and username) of the administrator.
        Raises a 404 error if the user does not exist, and a 403 error if they are not an administrator.
    """
    token = credentials.credentials
    user_id = int(jwt_service.validate_user_jwt(token))
    user: User | None = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return to_api_user(user)


def require_admin(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
) -> APIUser:
    """Dependency of the admin routers (dependencies=[Depends(require_admin)]):
    the route is only run if the request comes from a logged-in administrator.
    """
    return get_admin_from_credentials(credentials)


# ---------- Routes ----------

user_router = APIRouter(prefix="/users", tags=["Users"])

admin_user_router = APIRouter(
    prefix="/admin/users",
    tags=["Users"],
    dependencies=[Depends(require_admin)],
)


@user_router.post("/", summary="Create a user", status_code=status.HTTP_201_CREATED)
def create_user(u: UserModel) -> APIUser:
    """
    Register a new user. The username and the email must be unique, and the password must have at least 8 characters.
    """
    new_user = User(u.username, u.email, u.password, u.first_name, u.last_name)
    try:
        user = user_service.create_user(new_user)
    except ValueError as error:
        # Password too short
        raise HTTPException(status_code=400, detail=str(error)) from error
    except UniqueViolation as error:
        # The database refuses a username or an email that is already used
        raise HTTPException(status_code=409, detail="Username or email already in use") from error

    return to_api_user(user)


@user_router.post("/jwt", summary="Login", status_code=status.HTTP_200_OK)
def login(username: str, password: str) -> JWTResponse:
    """
    Log in and get a JWT access token, valid for 10 minutes.
    Use this token in the "Authorize" button, or in the Authorization header (Bearer) of the other routes.

    Args:

    * username: the username of the account
    * password: the password of the account
    """
    try:
        user = validate_username_password(username, password, user_repo)
    except UnknownUsernameError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown username",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
    except WrongPasswordError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    # A user read from the database always has an id
    # pyrefly: ignore
    return jwt_service.encode_jwt(user.id)


@admin_user_router.get("/", summary="List users")
def list_users() -> list[APIUser]:
    """
    List all the users (administrators only).
    """
    users = user_service.get_all()
    return [to_api_user(user) for user in users]


@user_router.get("/me", summary="Get own profile")
def get_own_profile(credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())]) -> APIUser:
    """
    Get the profile (id and username) of the logged-in user.
    """
    return get_user_from_credentials(credentials)


@user_router.put("/me", summary="Update own profile")
def update_own_profile(
    u: UpdateUserModel, credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())]
) -> APIUser:
    """
    Update the profile of the logged-in user.

    Args:

    * u: the new data (username and email are required, first_name and last_name are optional)
    """
    current_user = get_user_from_credentials(credentials)
    try:
        user = user_service.update_user(
            user_id=current_user.id,
            username=u.username,
            email=u.email,
            first_name=u.first_name,
            last_name=u.last_name,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail="User not found") from error
    except UniqueViolation as error:
        raise HTTPException(status_code=409, detail="Username or email already in use") from error

    return to_api_user(user)


@user_router.put("/me/password", summary="Change own password", status_code=status.HTTP_204_NO_CONTENT)
def change_own_password(
    m: ChangeUserPasswordModel,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
) -> None:
    """
    Change the password of the logged-in user.
    The current password must be given, and the new one must have at least 8 characters.

    Args:

    * m: the current password (old_password) and the new password (new_password)
    """
    current_user = get_user_from_credentials(credentials)
    try:
        user_service.change_password(current_user.id, m.old_password, m.new_password)
    except PermissionError as error:
        raise HTTPException(status_code=403, detail="Wrong current password") from error
    except ValueError as error:
        # New password too short
        raise HTTPException(status_code=400, detail=str(error)) from error


@user_router.delete("/me", summary="Delete own profile", status_code=status.HTTP_204_NO_CONTENT)
def delete_own_profile(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
    confirm: bool = False,
) -> None:
    """
    Delete the profile of the logged-in user, with all their reservations and reviews.

    Args:

    * confirm: must be true to confirm the deletion (default false, the request is then refused)
    """
    if not confirm:
        raise HTTPException(
            status_code=409,
            detail="Confirmation required: repeat the request with confirm=True",
        )
    current_user = get_user_from_credentials(credentials)
    try:
        is_deleted = user_service.delete_user(current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail="User not found") from error
    if not is_deleted:
        raise HTTPException(status_code=404, detail="User not found")
