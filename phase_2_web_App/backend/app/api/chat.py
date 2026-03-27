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
@router.get("/chatkit")
async def chatkit_streaming_endpoint(
    request: Request,
    current_user: dict = Depends(get_current_user_from_request),
    db: Session = Depends(get_session)
):
    """
    Official ChatKit streaming endpoint using openai-chatkit Python SDK.

    Compatible with @openai/chatkit-react widget.

    Supports both POST and GET methods:
    - POST: For chat messages with SSE streaming
    - GET: For thread history and metadata requests

    Authentication:
    - Authorization: Bearer <token> header (standard)
    - ?token=<token> query parameter (for ChatKit widget)
    """
    logger.info(f"[ChatKit] ================================================")
    logger.info(f"[ChatKit] {request.method} {request.url.path}")
    logger.info(f"[ChatKit] Query params: {dict(request.query_params)}")
    logger.info(f"[ChatKit] Headers: {dict(request.headers)}")
    logger.info(f"[ChatKit] User: {current_user.get('email')}")
    logger.info(f"[ChatKit] ================================================")
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

        logger.info(f"[ChatKit] Request - Content-Type: {content_type}")
        logger.info(f"[ChatKit] Request body length: {len(request_body)} bytes")

        if len(request_body) > 0:
            try:
                body_json = json.loads(request_body)
                logger.info(f"[ChatKit] Request body JSON: {json.dumps(body_json, indent=2)}")
            except:
                logger.info(f"[ChatKit] Request body preview: {request_body[:500]}...")

        # Protocol translation: Handle old ChatKit widget format (v1.5.x) vs new SDK format (v1.6.x)
        # Old widget sends: {"type": "user_message", "item": {"id": "...", "thread_id": "...", "content": [...]}}
        # New SDK expects: {"type": "threads.add_user_message", "params": {"input": {...}, "thread_id": "..."}}
        if len(request_body) > 0:
            try:
                body_json = json.loads(request_body)
                request_type = body_json.get("type", "")

                # Translate old protocol to new protocol
                if request_type == "user_message":
                    logger.info(f"[ChatKit] Translating old protocol 'user_message' to 'threads.add_user_message'")
                    # Extract fields from the old format
                    item = body_json.get("item", {})
                    thread_id = item.get("thread_id")
                    content = item.get("content")

                    # Create new format with correct structure including required fields
                    translated_request = {
                        "type": "threads.add_user_message",
                        "params": {
                            "input": {
                                "content": content,
                                "attachments": [],  # Required by new SDK
                                "inference_options": {}  # Required by new SDK
                            },
                            "thread_id": thread_id
                        }
                    }
                    request_body = json.dumps(translated_request).encode('utf-8')
                    logger.info(f"[ChatKit] Translated request body: {json.dumps(translated_request, indent=2)}")

                logger.info(f"[ChatKit] Request body JSON: {json.dumps(body_json, indent=2)}")
            except:
                logger.info(f"[ChatKit] Request body preview: {request_body[:500]}...")

        # For GET requests with no body, create empty protocol request
        if request.method == "GET" and len(request_body) == 0:
            # Check if this is a threads list request
            if request.query_params.get("type") == "threads.list":
                threads_list_request = {
                    "type": "threads.list",
                    "params": {
                        "limit": int(request.query_params.get("limit", 20)),
                        "order": request.query_params.get("order", "desc")
                    }
                }
                request_body = json.dumps(threads_list_request).encode('utf-8')
                logger.info(f"[ChatKit] Converted GET request to: {json.dumps(threads_list_request)}")
            else:
                # Empty body for GET requests
                request_body = b'{}'

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
