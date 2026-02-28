"""
ChatKit API Endpoint

Official ChatKit streaming endpoint using Server-Sent Events (SSE).
Implements the ChatKit protocol for compatibility with @openai/chatkit-react.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import StreamingResponse

from services.auth_service import get_current_user
from services.chatkit_server import chatkit_server

router = APIRouter()


@router.post("/chatkit")
async def chatkit_endpoint(
    request: Request,
    current_user: str = Depends(get_current_user)
):
    """
    Official ChatKit streaming endpoint.

    Handles ChatKit protocol requests and streams responses using Server-Sent Events.

    Expected request format:
    {
        "thread_id": "optional-conversation-id",
        "message": "user message"
    }

    Returns:
        StreamingResponse with text/event-stream content type
    """
    async def event_stream():
        """Generator function that yields SSE events."""
        try:
            # Get raw request body
            request_body = await request.body()

            # Build context from authenticated user
            context = {"user_id": current_user}

            # Process request through ChatKit server and yield SSE events
            async for event in chatkit_server.process_request(request_body, context):
                yield event

        except Exception as e:
            # Send error event
            import json
            error_data = json.dumps({"error": str(e)})
            yield f"event: error\ndata: {error_data}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
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
