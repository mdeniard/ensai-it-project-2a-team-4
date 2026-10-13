from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from src.Business_object.User import User
from src.Model.APIUser import APIUser
from src.Model.JWTResponse import JWTResponse
from src.Model.UserModel import UserModel, UpdateUserModel, ChangeUserPasswordModel
from src.Service.PasswordService import check_password_strength, validate_username_password
from src.Service.UserService import UserService

from .init_app import jwt_service, user_repo, user_service
from .JWTBearer import JWTBearer

if TYPE_CHECKING:
    from src.Model.User import User

user_router = APIRouter(prefix="/users", tags=["Users"])

@user_router.get("/")
def list_users(
    credentials: Annotated[HTTPAuthorizationCredentials,
    Depends(JWTBearer())]
) -> list[APIUser]:
    """
    List all users (admin only)
    """
    get_admin_from_credentials(credentials)
    users = user_service.get_all()
    return [APIUser(id=u.id, username=u.username) for u in users]

@user_router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(u: UserModel) -> APIUser:
    """
    Performs validation on the username and password
    """
    try:
        check_password_strength(password=u.password)
    except Exception:
        raise HTTPException(status_code=400, detail="Password too weak") from Exception
    try:
        user: User = UserService().create_user(User(u.username, u.email, u.password, u.first_name, u.last_name))
    except Exception as error:
        raise HTTPException(status_code=409, detail="Username already exists") from error

    return APIUser(id=user.id, username=user.username)

@user_router.put("/me", dependencies=[Depends(JWTBearer())])
def update_own_profile(
    u: UpdateUserModel,
    credentials: Annotated[HTTPAuthorizationCredentials,
    Depends(JWTBearer())]) -> APIUser:
    """
    Update the authenticated user's profile
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
    except Exception as error:
        raise HTTPException(status_code=409, detail="Username or email already in use") from error

    return APIUser(id=user.id, username=user.username)

@user_router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_own_password(
    m: ChangeUserPasswordModel,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
) -> None:
    current_user = get_user_from_credentials(credentials)
    try:
        user_service.change_password(current_user.id, m.old_password, m.new_password)
    except PermissionError as error:
        raise HTTPException(status_code=403, detail="Wrong current password") from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Password too weak") from error

@user_router.delete("/me", dependencies=[Depends(JWTBearer())])
def delete_own_profile(
    credentials: Annotated[HTTPAuthorizationCredentials,
    Depends(JWTBearer())]) -> None:
    """
    Delete the authenticated user's profile
    """
    current_user = get_user_from_credentials(credentials)
    try:
        succes = user_service.delete_user(current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail="User not found") from error
    except Exception as error:
        raise HTTPException(status_code=409, detail="Username or email already in use") from error

@user_router.post("/jwt", status_code=status.HTTP_201_CREATED)
def login(username: str, password: str) -> JWTResponse:
    """
    Authenticate with username and password and obtain a token
    """
    try:
        user = validate_username_password(username=username, password=password, user_repo=user_repo)
    except Exception as error:
        raise HTTPException(status_code=403, detail="Invalid username and password combination") from error

    return jwt_service.encode_jwt(user.id)


@user_router.get("/me", dependencies=[Depends(JWTBearer())])
def get_user_own_profile(credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())]) -> APIUser:
    """
    Get the authenticated user profile
    """
    return get_user_from_credentials(credentials)


def get_user_from_credentials(credentials: HTTPAuthorizationCredentials) -> APIUser:
    token = credentials.credentials
    user_id = int(jwt_service.validate_user_jwt(token))
    user: User | None = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return APIUser(id=user.id, username=user.username)

def get_admin_from_credentials(credentials: HTTPAuthorizationCredentials) -> APIUser:
    token = credentials.credentials
    user_id = int(jwt_service.validate_user_jwt(token))
    user: User | None = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return APIUser(id=user.id, username=user.username)
