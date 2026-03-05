"""
Chat API endpoints for Phase II backend.

Implements the ChatKit SSE protocol for compatibility with @openai/chatkit-react.
"""

import logging
import json
from typing import AsyncIterator, Dict, Any
from datetime import datetime, timezone
import uuid as uuid_lib

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session

from ..middleware.auth import get_current_user, get_current_user_from_request
from ..database import get_session
from ..models.user import User
from ..models.task import Task
from sqlmodel import select

from openai import OpenAI
import os

router = APIRouter(prefix="/v1", tags=["chat"])
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Import the official ChatKit server
from ..services.official_chatkit_server import TodoChatKitServer

# Create global ChatKit server instance
chatkit_server = TodoChatKitServer()

logger.info("[Chat API] Official ChatKit server initialized")


# ============================================================================
# Data Models
# ============================================================================

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: str


# ============================================================================
# Helper Functions
# ============================================================================

def utc_now():
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


# ============================================================================
# ChatKit Streaming Endpoint (Official Protocol)
# ============================================================================

@router.post("/chatkit")
async def chatkit_streaming_endpoint(
    request: Request,
    current_user: dict = Depends(get_current_user_from_request),
    db: Session = Depends(get_session)
):
    """
    Official ChatKit streaming endpoint using openai-chatkit Python SDK.

    Compatible with @openai/chatkit-react widget.

    Authentication:
    - Authorization: Bearer <token> header (standard)
    - ?token=<token> query parameter (for ChatKit widget)
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            logger.error("[ChatKit] Missing user_id in current_user")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        user = db.get(User, user_id)
        if not user:
            logger.error(f"[ChatKit] User not found for user_id={user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        logger.info(f"[ChatKit] Request from user_id={user_id}, email={user.email}")

        # Read request body
        request_body = await request.body()
        content_type = request.headers.get("content-type", "")
        logger.info(f"[ChatKit] Request - Content-Type: {content_type}, Method: {request.method}")
        logger.info(f"[ChatKit] Request body length: {len(request_body)} bytes")
        if len(request_body) > 0:
            try:
                body_json = json.loads(request_body)
                logger.info(f"[ChatKit] Request body JSON: {json.dumps(body_json, indent=2)}")
            except:
                logger.info(f"[ChatKit] Request body preview: {request_body[:500]}...")

        # Build context for ChatKit server
        context = {
            "user_id": user_id,
            "email": user.email,
            "db": db
        }

        logger.info("[ChatKit] Calling chatkit_server.process()...")

        # Use official ChatKit server.process() method
        try:
            result = await chatkit_server.process(request_body, context)
            logger.info(f"[ChatKit] process() completed successfully")
        except Exception as process_error:
            logger.exception(f"[ChatKit] process() raised exception: {process_error}")
            raise

        logger.info(f"[ChatKit] process() result type: {type(result)}")
        logger.info(f"[ChatKit] process() result: {result}")

        # Check if result is streaming or non-streaming
        from chatkit.server import StreamingResult, NonStreamingResult

        if isinstance(result, StreamingResult):
            # StreamingResult is an async generator that yields SSE bytes
            logger.info("[ChatKit] Returning streaming response")
            return StreamingResponse(
                result,
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        elif isinstance(result, NonStreamingResult):
            # NonStreamingResult contains JSON bytes
            logger.info("[ChatKit] Returning non-streaming JSON response")
            logger.info(f"[ChatKit] NonStreamingResult content preview: {result.json[:500] if result.json else b'empty'}...")
            from fastapi.responses import Response
            return Response(content=result.json, media_type="application/json")
        elif result is None:
            # Handle None result
            logger.error("[ChatKit] process() returned None")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ChatKit server returned no response"
            )
        else:
            # Unknown result type
            logger.error(f"[ChatKit] Unknown result type: {type(result)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"ChatKit server returned unexpected result type: {type(result)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[ChatKit] Unexpected error processing request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ChatKit processing error: {str(e)}"
        )


# ============================================================================
# Legacy Chat Endpoint (for backward compatibility)
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Legacy chat endpoint for backward compatibility.
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    # Simple response (legacy)
    ai_response = f"I received: '{request.message}'. Please use the ChatKit widget for full AI features."

    return ChatResponse(
        response=ai_response,
        conversation_id=request.conversation_id or "legacy",
        timestamp=datetime.utcnow().isoformat()
    )
