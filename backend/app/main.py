"""FastAPI application entry point."""

from fastapi import FastAPI

from app.routes import auth, users


app = FastAPI(title="Service Desk API")

# Include each route module in the application.
app.include_router(auth.router)
app.include_router(users.router)
