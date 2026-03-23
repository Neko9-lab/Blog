from fastapi import APIRouter

from app.api.v1.endpoints import auth, posts, comments, users, admin, config, categories, uploads, notifications


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(config.router, prefix="/config", tags=["config"])
