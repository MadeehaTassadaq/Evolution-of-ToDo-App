"""
Official OpenAI ChatKit Endpoint

FastAPI endpoint that integrates ChatKitServer with the REST API.
Follows the official ChatKit protocol for POST /chatkit endpoint.
"""
from fastapi import APIRouter, Request, Response, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import Any
import json
import asyncio

from chatkit.server import ChatKitServer
from chatkit.agents import ThreadMetadata, UserMessageItem
from services.chatkit_server import TodoChatKitServer
from services.chatkit_store import RequestContext, ChatKitDatabaseStore
from services.auth_service import get_current_user
from database.session import get_session


router = APIRouter()


@router.post("/chatkit")
async def chatkit_endpoint(
    request: Request,
    current_user: str = Depends(get_current_user),
) -> Response:
    """
    Official ChatKit endpoint using POST /chatkit protocol.

    This endpoint:
    1. Receives ChatKit protocol requests (JSON body)
    2. Creates RequestContext with user_id and database session
    3. Processes through ChatKitServer.process()
    4. Returns streaming response (text/event-stream) or JSON response
    """
    from database.session import Session, engine
    from sqlmodel import select

    # Get request body
    body = await request.body()

    # Parse request to determine type
    try:
        request_data = json.loads(body) if body else {}
    except:
        request_data = {}

    # Determine request type (list_threads, create_thread, send_message, etc.)
    request_type = request_data.get("type", "")

    # Create database session
    db_session = Session(engine)

    try:
        # Create store instance
        store = ChatKitDatabaseStore()

        # Create request context with user_id and session
        context = RequestContext(user_id=current_user, session=db_session)

        # Create server instance
        server = TodoChatKitServer(store)

        # For direct JSON requests (list_threads, create_thread, get_thread, etc.)
        if request_type in ["list_threads", "create_thread", "get_thread", "delete_thread", "load_thread_items"]:
            # Handle synchronous operations
            if request_type == "list_threads" or request_type == "load_threads":
                limit = request_data.get("limit", 50)
                after = request_data.get("after")
                order = request_data.get("order", "desc")
                result = await store.load_threads(limit=limit, after=after, order=order, context=context)
                db_session.close()
                return Response(content=json.dumps(result), media_type="application/json")

            elif request_type == "create_thread":
                thread_id = store.generate_thread_id(context)
                thread = {
                    "id": thread_id,
                    "created_at": asyncio.get_event_loop().time(),
                    "updated_at": asyncio.get_event_loop().time(),
                    "metadata": request_data.get("metadata", {})
                }
                await store.save_thread(thread, context)
                db_session.close()
                return Response(content=json.dumps(thread), media_type="application/json")

            elif request_type == "get_thread" or request_type == "load_thread":
                thread_id = request_data.get("thread_id")
                thread = await store.load_thread(thread_id, context)
                db_session.close()
                if thread:
                    return Response(content=json.dumps(thread), media_type="application/json")
                else:
                    raise HTTPException(status_code=404, detail="Thread not found")

            elif request_type == "delete_thread":
                thread_id = request_data.get("thread_id")
                await store.delete_thread(thread_id, context)
                db_session.close()
                return Response(content='{"status": "deleted"}', media_type="application/json")

            elif request_type == "load_thread_items":
                thread_id = request_data.get("thread_id")
                after = request_data.get("after")
                limit = request_data.get("limit", 50)
                order = request_data.get("order", "asc")
                result = await store.load_thread_items(thread_id=thread_id, after=after, limit=limit, order=order, context=context)
                db_session.close()
                return Response(content=json.dumps(result), media_type="application/json")

        # For chat messages requiring streaming agent response
        # Process through ChatKit server
        result = await server.process(body, context)

        # Check if result is async iterator (streaming)
        if hasattr(result, '__aiter__'):
            async def event_stream():
                try:
                    async for chunk in result:
                        if isinstance(chunk, bytes):
                            yield chunk
                        elif isinstance(chunk, dict):
                            event_data = json.dumps(chunk)
                            yield f"data: {event_data}\n\n"
                        else:
                            event_data = str(chunk)
                            yield f"data: {event_data}\n\n"
                except Exception as e:
                    import traceback
                    print(f"Stream error: {e}")
                    traceback.print_exc()
                    error_event = {"error": str(e), "type": "error"}
                    yield f"data: {json.dumps(error_event)}\n\n"
                finally:
                    db_session.close()

            return StreamingResponse(
                event_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                }
            )
        else:
            # Return JSON response
            db_session.close()
            if isinstance(result, dict):
                return Response(content=json.dumps(result), media_type="application/json")
            elif isinstance(result, str):
                return Response(content=result, media_type="application/json")
            else:
                return Response(content=json.dumps({"result": str(result)}), media_type="application/json")

    except HTTPException:
        db_session.close()
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        db_session.close()
        raise HTTPException(
            status_code=500,
            detail=f"ChatKit processing error: {str(e)}"
        )


@router.get("/chatkit/health")
async def chatkit_health():
    """Health check for ChatKit endpoint."""
    return {
        "status": "ok",
        "service": "chatkit-official",
        "protocol": "openai-chatkit-python"
    }
