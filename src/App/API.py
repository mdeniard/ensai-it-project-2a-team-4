import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from .AccountingController import admin_accounting_router
from .MovieController import admin_movie_router, movie_router
from .ReservationController import reservation_router
from .ReviewController import admin_review_router, review_router
from .RoomController import admin_room_router, room_router
from .ScreeningController import admin_screening_router, screening_router
from .TicketTypeController import admin_ticket_type_router, ticket_type_router
from .UserController import admin_user_router, user_router


def run_app():
    """Create the FastAPI application, add all the routers (public and admin)
    and start the server on the port 8000.
    """
    app = FastAPI(
        title="IT Project 2A",
        version="1.0.0",
        description=(
            "Backend API for **Cinéville Bruz** allowing users to browse movies, "
            "check screening schedules, book tickets, and leave reviews.\n\n"
            "**Authentication:** Log in via `/users/jwt` to get a JWT token, "
            "then click **Authorize** (`Bearer <token>`) to test protected or admin routes."
        ),
    )

    app.include_router(user_router)

    app.include_router(admin_user_router)

    app.include_router(movie_router)

    app.include_router(admin_movie_router)

    app.include_router(screening_router)

    app.include_router(admin_screening_router)

    app.include_router(room_router)

    app.include_router(admin_room_router)

    app.include_router(reservation_router)

    app.include_router(review_router)

    app.include_router(admin_review_router)

    app.include_router(admin_accounting_router)

    app.include_router(ticket_type_router)

    app.include_router(admin_ticket_type_router)

    @app.get("/", include_in_schema=False)
    async def redirect_to_docs():
        """Redirect to the API documentation"""
        return RedirectResponse(url="/docs")

    uvicorn.run(app, port=8000, host="0.0.0.0")
