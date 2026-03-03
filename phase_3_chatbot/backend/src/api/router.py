"""
API Router - Main router for all API endpoints
"""
from fastapi import APIRouter
from api.v1 import chat, auth, chatkit_session, tools
from api.v1.chatkit_official import router as chatkit_official_router

# Create main router
router = APIRouter()

# Include v1 routers
router.include_router(chat.router, prefix="/v1", tags=["chat"])
router.include_router(auth.router, prefix="/v1", tags=["auth"])
# Use the official ChatKit SDK endpoint
router.include_router(chatkit_official_router, prefix="/v1", tags=["chatkit"])
router.include_router(tools.router, prefix="/v1", tags=["tools"])
# ChatKit session endpoint (no /v1 prefix - accessed directly at /api/chatkit/session)
router.include_router(chatkit_session.router, tags=["chatkit-session"])
