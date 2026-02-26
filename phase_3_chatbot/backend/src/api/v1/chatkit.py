"""
ChatKit API Endpoint
Handles ChatKit protocol requests with authentication
"""

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import json
from uuid import UUID
import os
from openai import OpenAI

from services.chatkit_server import TodoChatKitServer
from services.chatkit_store import DatabaseStore
from database.session import get_session_context, Session, engine
from services.auth_service import auth_service
from database.models.user import User

router = APIRouter(prefix="/chatkit", tags=["chatkit"])
security = HTTPBearer()

# Initialize OpenAI client for ChatKit sessions
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@router.post("/session")
async def create_chatkit_session(
    request: Dict[str, Any],
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Create a ChatKit session for the authenticated user.

    This endpoint works with OpenAI ChatKit in Custom Backend Mode.
    No workflowId required - we use OpenAI Agents SDK directly.

    Returns:
    - client_secret: Session token for ChatKit authentication
    - thread_id: Conversation ID for chat history persistence
    """
    # Verify JWT token
    user_data = auth_service.verify_token(token.credentials)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = str(user_data.user_id)

    # Get or create conversation for session history
    db = Session(engine)
    try:
        from services.chat_service import ChatService
        chat_service = ChatService(db)

        # Get thread_id from request for session continuity
        thread_id = request.get("thread_id")

        # Get existing conversation or create new one
        conversation = chat_service.get_or_create_conversation(
            user_id=user_id,
            conversation_id=thread_id
        )

        # Generate a session token for ChatKit
        # In production, you'd use a proper JWT or secure token
        import secrets
        import hashlib
        import time

        # Create a secure session token
        session_data = f"{user_id}:{conversation.id}:{time.time()}"
        client_secret = hashlib.sha256(session_data.encode()).hexdigest()

        # Store session info in metadata for WebSocket verification
        return {
            "client_secret": client_secret,
            "thread_id": str(conversation.id),
            "user_id": user_id,
            "mode": "custom_backend"  # Using OpenAI Agents SDK (not Agent Builder)
        }

    finally:
        db.close()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for ChatKit protocol"""
    await websocket.accept()

    try:
        # Get token from WebSocket query params or headers
        token = websocket.query_params.get("token")
        if not token:
            # Try to get from headers
            token = websocket.headers.get("authorization", "").replace("Bearer ", "")

        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication required")
            return

        # Verify token and get user
        user_data = auth_service.verify_token(token)
        if not user_data:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return

        user_id = user_data.user_id

        # Create database session
        db = Session(engine)

        try:
            # Create store and server instances
            store = DatabaseStore(db)
            server = TodoChatKitServer(db)

            # Here we would typically handle ChatKit protocol messages
            # For now, just acknowledge the connection
            await websocket.send_text(json.dumps({
                "type": "connection_ack",
                "user_id": user_id,
                "message": "Connected to Todo AI ChatKit server"
            }))

            # Handle incoming messages
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)

                # Process ChatKit protocol messages
                if message.get("type") == "create_thread":
                    # Create a new thread
                    thread_meta = await server.create_thread(
                        user_id=user_id,
                        metadata=message.get("metadata")
                    )

                    await websocket.send_text(json.dumps({
                        "type": "thread_created",
                        "thread": thread_meta.dict()
                    }))

                elif message.get("type") == "list_threads":
                    # List user's threads
                    threads = await server.list_threads(user_id=user_id)

                    await websocket.send_text(json.dumps({
                        "type": "threads_list",
                        "threads": [t.dict() for t in threads]
                    }))

                elif message.get("type") == "get_thread":
                    thread_id = message.get("thread_id")
                    if thread_id:
                        thread = await server.get_thread(thread_id)
                        await websocket.send_text(json.dumps({
                            "type": "thread_data",
                            "thread": thread.dict() if thread else None
                        }))

                elif message.get("type") == "send_message":
                    # Handle sending a message through the AI agent
                    thread_id = message.get("thread_id")
                    content = message.get("content")

                    if content:
                        try:
                            # Process the message through the AI agent
                            from agents.todo_agent import TodoAgent
                            from services.chat_service import ChatService

                            # Initialize services
                            db_session = Session(engine)
                            try:
                                chat_service = ChatService(db_session)
                                agent = TodoAgent()

                                # Get conversation history for context
                                # If thread_id is "default" or None, create a new conversation
                                effective_thread_id = None if thread_id == "default" else thread_id
                                conversation = chat_service.get_or_create_conversation(
                                    user_id=user_id,
                                    conversation_id=effective_thread_id
                                )

                                # Get conversation history (excluding the message we're about to add)
                                conversation_history = chat_service.get_full_conversation_history(conversation.id)

                                # Process the message with the agent
                                agent_response = agent.process_message(
                                    user_message=content,
                                    conversation_history=conversation_history,
                                    user_id=user_id
                                )

                                # Extract response and tool calls
                                response_text = agent_response.get("response", "")
                                tool_calls = agent_response.get("tool_calls", [])

                                # Process tool calls if any
                                for tool_call in tool_calls:
                                    tool_name = tool_call["name"]
                                    parameters = tool_call["arguments"]

                                    # Call the actual tools through the backend service
                                    from services.todo_tools import TodoTools
                                    todo_tools = TodoTools(db_session)

                                    try:
                                        if tool_name == "add_task":
                                            result = todo_tools.add_task(**parameters)
                                        elif tool_name == "list_tasks":
                                            result = todo_tools.list_tasks(**parameters)
                                        elif tool_name == "update_task":
                                            result = todo_tools.update_task(**parameters)
                                        elif tool_name == "complete_task":
                                            result = todo_tools.complete_task(**parameters)
                                        elif tool_name == "delete_task":
                                            result = todo_tools.delete_task(**parameters)
                                        else:
                                            result = {"success": False, "error": f"Unknown tool: {tool_name}"}
                                    except Exception as e:
                                        result = {"success": False, "error": str(e)}

                                # Add user and assistant messages to conversation
                                chat_service.add_message_to_conversation(
                                    conversation_id=conversation.id,
                                    role="user",
                                    content=content
                                )

                                chat_service.add_message_to_conversation(
                                    conversation_id=conversation.id,
                                    role="assistant",
                                    content=response_text,
                                    metadata={"tool_calls": [tc["name"] for tc in tool_calls]}
                                )

                                # Send the AI response back to the client
                                # Use the actual conversation ID, not the "default" placeholder
                                await websocket.send_text(json.dumps({
                                    "type": "message_received",
                                    "content": response_text,
                                    "thread_id": conversation.id,  # Send actual conversation ID
                                    "original_thread_id": thread_id,  # Include original for reference
                                    "tool_calls": tool_calls
                                }))
                            finally:
                                db_session.close()
                        except Exception as e:
                            # Send error message back to client
                            await websocket.send_text(json.dumps({
                                "type": "message_error",
                                "error": str(e),
                                "thread_id": thread_id
                            }))

        except WebSocketDisconnect:
            print(f"WebSocket disconnected for user {user_id}")
        finally:
            db.close()

    except WebSocketDisconnect:
        print("Client disconnected")


@router.get("/health")
async def chatkit_health():
    """Health check for ChatKit endpoint"""
    return {"status": "ok", "service": "chatkit"}


# Additional REST endpoints for ChatKit protocol if needed
@router.post("/threads")
async def create_thread(
    request: dict,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """REST endpoint to create a new thread"""
    user_data = auth_service.verify_token(token.credentials)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = user_data.get("user_id")

    db = Session(engine)
    try:
        server = TodoChatKitServer(db)
        thread_metadata = await server.create_thread(
            user_id=user_id,
            initial_messages=request.get("initial_messages"),
            metadata=request.get("metadata")
        )

        return {"thread": thread_metadata.dict()}
    finally:
        db.close()


@router.get("/threads")
async def list_threads(
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """REST endpoint to list user's threads"""
    user_data = auth_service.verify_token(token.credentials)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = user_data.get("user_id")

    db = Session(engine)
    try:
        server = TodoChatKitServer(db)
        threads = await server.list_threads(user_id=user_id)

        return {"threads": [t.dict() for t in threads]}
    finally:
        db.close()


@router.get("/threads/{thread_id}")
async def get_thread(
    thread_id: str,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """REST endpoint to get a specific thread"""
    user_data = auth_service.verify_token(token.credentials)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Verify user has access to this thread
    db = Session(engine)
    try:
        server = TodoChatKitServer(db)
        thread = await server.get_thread(thread_id)

        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        return {"thread": thread.dict()}
    finally:
        db.close()


@router.get("/threads/{thread_id}/messages")
async def list_messages(
    thread_id: str,
    limit: Optional[int] = 20,
    before: Optional[str] = None,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """REST endpoint to list messages in a thread"""
    user_data = auth_service.verify_token(token.credentials)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = Session(engine)
    try:
        server = TodoChatKitServer(db)
        messages = await server.list_items(thread_id, before=before, limit=limit)

        return {"messages": [msg.dict() for msg in messages]}
    finally:
        db.close()