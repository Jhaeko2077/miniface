from fastapi import APIRouter

from app.api.routes import auth, automation, posts, users

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(posts.router)
api_router.include_router(automation.router)
