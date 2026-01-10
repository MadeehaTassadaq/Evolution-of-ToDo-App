from fastapi import APIRouter
from .v1.chat import router as chat_router
from .v1.auth import router as auth_router


# Create main API router
router = APIRouter()

# Include all API version routers
router.include_router(chat_router, prefix="/v1", tags=["chat"])
router.include_router(auth_router, prefix="/v1", tags=["auth"])