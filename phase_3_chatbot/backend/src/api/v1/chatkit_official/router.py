"""
ChatKit API Endpoint using Official SDK

Official ChatKit endpoint using the ChatKit Python SDK's process method.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from services.auth_service import get_current_user_optional
from services.chatkit_server_official import todo_chatkit_server

router = APIRouter()


@router.post("/chatkit")
async def chatkit_endpoint(
    request: Request,
    current_user: str = Depends(get_current_user_optional)
):
    """
    Official ChatKit endpoint using the SDK's process method.

    Handles ChatKit protocol requests using the official ChatKit Python SDK.
    """
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

    # Build context
    context = {
        "user_id": current_user,
        "access_token": access_token
    }

    print(f"[CHATKIT OFFICIAL] Request from {current_user}: {request_body[:200] if len(request_body) > 200 else request_body}", flush=True)

    # Process request through ChatKit SDK server
    async def event_stream():
        async for event in todo_chatkit_server.process(request_body, context):
            # The SDK returns proper event objects
            # Convert to SSE format
            event_dict = event.model_dump()
            event_type = event_dict.pop("type", "message")
            import json
            data_str = json.dumps(event_dict, default=str)
            yield f"event: {event_type}\ndata: {data_str}\n\n"
            print(f"[CHATKIT OFFICIAL] Yielding: {event_type}", flush=True)

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
        "server": "TodoChatKitServer (Official SDK)",
        "protocol": "ChatKit Python SDK"
    }

