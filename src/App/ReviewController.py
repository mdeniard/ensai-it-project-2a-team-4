from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from src.Business_object.Review import Review
from src.Model.ReviewModel import ReviewModel
from src.Service.ReviewService import ReviewService

from .JWTBearer import JWTBearer
from .UserController import get_user_from_credentials, require_admin

review_router = APIRouter(prefix="/reviews", tags=["Reviews"])

admin_review_router = APIRouter(
    prefix="/admin/reviews",
    tags=["Reviews"],
    dependencies=[Depends(require_admin)],
)


# ---------- Public routes ----------

@review_router.get("/movies/{movie_id}", summary="Get the reviews of a movie", status_code=status.HTTP_200_OK)
def get_movie_reviews(movie_id: int):
    """
    List the reviews of a movie, the most recent first.

    Args:

    * movie_id: the id of the movie in our database
    """
    try:
        return ReviewService().get_movie_reviews(movie_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


# ---------- Customer routes (logged-in users) ----------

@review_router.post("/", summary="Write a review", status_code=status.HTTP_201_CREATED)
def create_review(
    r: ReviewModel,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
):
    """
    Write a review for a movie. The author is the logged-in user.

    Args:

    * r: the movie_id, the rating (from 1 to 10) and an optional comment
    """
    current_user = get_user_from_credentials(credentials)

    review = Review(
        customer_id=current_user.id,
        movie_id=r.movie_id,
        rating=r.rating,
        comment=r.comment,
    )

    try:
        return ReviewService().create_review(review)
    except LookupError as e:
        # The movie does not exist
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except ValueError as e:
        # The movie has not been seen or has already been reviewed
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e


@review_router.get("/me", summary="Get my reviews", status_code=status.HTTP_200_OK)
def get_my_reviews(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
):
    """
    List all the reviews written by the logged-in user, the most recent first.
    """
    current_user = get_user_from_credentials(credentials)
    return ReviewService().get_customer_reviews(current_user.id)


@review_router.delete("/movies/{movie_id}", summary="Delete my review of a movie", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_review(
    movie_id: int,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
) -> None:
    """
    Delete my review of a movie.

    Args:

    * movie_id: the id of the movie in our database
    """
    current_user = get_user_from_credentials(credentials)
    try:
        ReviewService().delete_review(movie_id, current_user.id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


# ---------- Admin routes ----------

@admin_review_router.delete("/{review_id}", summary="Delete any review", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    confirm: bool = False,
) -> None:
    """
    Delete a review of any customer (moderation).

    Args:

    * review_id: the id of the review
    * confirm: must be true to confirm the deletion (default false, the request is then refused)
    """
    if not confirm:
        raise HTTPException(
            status_code=409,
            detail="Confirmation required: repeat the request with confirm=True",
        )
    try:
        ReviewService().delete_review_as_admin(review_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
