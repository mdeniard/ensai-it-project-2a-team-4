import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from .MovieController import movie_router
from .UserController import user_router


def run_app():
    app = FastAPI(title="Projet Info 2A", description="Example project for ENSAI students")

    app.include_router(user_router)

    app.include_router(movie_router)

    @app.get("/", include_in_schema=False)
    async def redirect_to_docs():
        """Redirect to the API documentation"""
        return RedirectResponse(url="/docs")

    uvicorn.run(app, port=8000, host="0.0.0.0")
