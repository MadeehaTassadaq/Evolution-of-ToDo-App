"""
ChatKit API Endpoint

Official ChatKit streaming endpoint using Server-Sent Events (SSE).
Custom implementation matching ChatKit protocol for @openai/chatkit-react.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import StreamingResponse

from services.auth_service import get_current_user, get_current_user_optional
from services.chatkit_server import chatkit_server

router = APIRouter()


@router.post("/chatkit")
async def chatkit_endpoint(
    request: Request,
    current_user: str = Depends(get_current_user_optional)
):
    """
    Official ChatKit streaming endpoint.

    Handles ChatKit protocol requests and streams responses using Server-Sent Events.

    Returns:
        StreamingResponse with text/event-stream content type
    """
    import sys

    # Get raw request body
    request_body = await request.body()

    # Extract access token from request for passing to Phase II API
    # Try Authorization header first, then query parameter, then cookie
    access_token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        access_token = auth_header[7:]  # Remove "Bearer " prefix
    elif "token" in request.query_params:
        access_token = request.query_params["token"]
    else:
        access_token = request.cookies.get("authToken") or request.cookies.get("better-auth-token")

    # Build context from authenticated user and access token
    context = {
        "user_id": current_user,
        "access_token": access_token
    }

    print(f"[CHATKIT ENDPOINT] Request from {current_user}: {request_body[:200]}", flush=True)

    # Process request through ChatKit server and yield SSE events
    async def event_stream():
        async for event in chatkit_server.process_request(request_body, context):
            print(f"[CHATKIT ENDPOINT] Yielding: {event[:150]}", flush=True)
            yield event

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/chatkit/health")
async def chatkit_health_check():
    """Health check endpoint for ChatKit service."""
    return {
        "status": "healthy",
        "service": "chatkit",
        "server": "TodoChatKitServer",
        "protocol": "SSE"
    }


@router.post("/chatkit/test")
async def chatkit_test_endpoint(
    request: Request,
    current_user: str = Depends(get_current_user_optional)
):
    """Test endpoint that returns simple SSE events for debugging."""

    async def test_stream():
        """Simple test stream."""
        import json
        yield "event: test\ndata: {\"message\": \"test event 1\"}\n\n"
        yield "event: test\ndata: {\"message\": \"test event 2\"}\n\n"
        yield "event: done\ndata: {\"status\": \"complete\"}\n\n"

    return StreamingResponse(
        test_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/chatkit/history")
async def get_conversation_history(
    thread_id: Optional[str] = Query(None, description="Thread/conversation ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items"),
    current_user: str = Depends(get_current_user)
):
    """
    Get conversation history for a thread.

    Args:
        thread_id: The conversation/thread ID to fetch history for
        limit: Maximum number of messages to return
        current_user: Authenticated user ID (injected)

    Returns:
        {
            "items": [...messages...],
            "has_more": false
        }
    """
    try:
        if not thread_id:
            raise HTTPException(
                status_code=400,
                detail="thread_id is required"
            )

        # Load thread items from the ChatKit store
        context = {"user_id": current_user}
        result = await chatkit_server.store.load_thread_items(
            thread_id=thread_id,
            limit=limit,
            order="asc",
            context=context
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load conversation history: {str(e)}"
        )


@router.get("/chatkit/conversations")
async def list_conversations(
    current_user: str = Depends(get_current_user)
):
    """
    List all conversations for the current user.

    Returns:
        List of conversations with thread_id, title, and metadata
    """
    try:
        from database.session import get_session_context
        from database.models.conversation import Conversation
        from sqlmodel import select

        with get_session_context() as session:
            # Get all conversations for this user
            statement = select(Conversation).where(
                Conversation.user_id == current_user
            ).order_by(Conversation.updated_at.desc())

            conversations = session.exec(statement).all()

            # Format for response
            result = []
            for conv in conversations:
                result.append({
                    "id": conv.id,
                    "thread_id": conv.id,
                    "title": conv.title or "New Conversation",
                    "created_at": conv.created_at.isoformat() if conv.created_at else None,
                    "updated_at": conv.updated_at.isoformat() if conv.updated_at else None
                })

            return {"items": result}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list conversations: {str(e)}"
        )
