from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlmodel import Session, func, select
from database.session import get_session
from services.chat_service import ChatService
from agents.todo_agent import TodoAgent
from database.models.message import Message
from database.models.conversation import Conversation
from services.auth_service import get_current_user
import uuid
from datetime import datetime


router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    conversation_id: Optional[str] = None


class ToolCallResponse(BaseModel):
    """Model for tool call response."""
    tool_name: str
    parameters: Dict[str, Any]
    result: Dict[str, Any]


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    conversation_id: str
    response: str
    tool_calls: List[ToolCallResponse]
    timestamp: str


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Chat endpoint that processes natural language input and returns AI-generated responses
    with potential task operations via MCP tools.

    Args:
        request: The chat request containing the message and optional conversation ID
        current_user: The authenticated user ID
        session: Database session for database operations

    Returns:
        ChatResponse with conversation ID, AI response, and any tool calls made
    """
    try:
        # Initialize services
        chat_service = ChatService(session)
        agent = TodoAgent()

        # Get or create conversation
        conversation = chat_service.get_or_create_conversation(
            user_id=current_user,
            conversation_id=request.conversation_id
        )

        # Get conversation history
        conversation_history = chat_service.get_full_conversation_history(conversation.id)

        # Add user message to conversation
        chat_service.add_message_to_conversation(
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )

        # Process the message with the agent
        agent_response = agent.process_message(
            user_message=request.message,
            conversation_history=conversation_history,
            user_id=current_user
        )

        # Extract response and tool calls
        response_text = agent_response.get("response", "")
        tool_calls = agent_response.get("tool_calls", [])

        # Process tool calls if any
        processed_tool_calls = []
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            parameters = tool_call["arguments"]

            # Call the actual tools through the backend service
            from services.todo_tools import TodoTools
            todo_tools = TodoTools(session)

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

                processed_tool_calls.append({
                    "tool_name": tool_name,
                    "parameters": parameters,
                    "result": result
                })
            except Exception as e:
                processed_tool_calls.append({
                    "tool_name": tool_name,
                    "parameters": parameters,
                    "result": {"success": False, "error": str(e)}
                })

        # If tools were called, generate a human-readable response based on tool results
        if processed_tool_calls and not response_text:
            # Format tool results for the AI to summarize
            tool_results_summary = []
            for tc in processed_tool_calls:
                result = tc["result"]
                if tc["tool_name"] == "list_tasks":
                    tasks = result.get("tasks", [])
                    if tasks:
                        task_lines = []
                        for task in tasks:
                            status_icon = "✅" if task.get("status") == "completed" else "📝"
                            task_lines.append(f"{status_icon} {task.get('title', 'Untitled')}")
                        response_text = f"Here are your tasks:\n" + "\n".join(task_lines)
                    else:
                        response_text = "You don't have any tasks yet. Would you like me to add one?"
                elif tc["tool_name"] == "add_task":
                    if result.get("success"):
                        response_text = f"✅ Task added: {result.get('task', {}).get('title', 'New task')}"
                    else:
                        response_text = f"Sorry, I couldn't add the task: {result.get('error', 'Unknown error')}"
                elif tc["tool_name"] == "complete_task":
                    if result.get("success"):
                        response_text = "✅ Task marked as completed!"
                    else:
                        response_text = f"Sorry, I couldn't complete the task: {result.get('error', 'Unknown error')}"
                elif tc["tool_name"] == "delete_task":
                    if result.get("success"):
                        response_text = "🗑️ Task deleted successfully."
                    else:
                        response_text = f"Sorry, I couldn't delete the task: {result.get('error', 'Unknown error')}"
                elif tc["tool_name"] == "update_task":
                    if result.get("success"):
                        response_text = "✅ Task updated successfully!"
                    else:
                        response_text = f"Sorry, I couldn't update the task: {result.get('error', 'Unknown error')}"

        # Add assistant response to conversation
        chat_service.add_message_to_conversation(
            conversation_id=conversation.id,
            role="assistant",
            content=response_text,
            metadata={"tool_calls": [tc["tool_name"] for tc in processed_tool_calls]}
        )

        # Prepare response
        return ChatResponse(
            conversation_id=conversation.id,
            response=response_text,
            tool_calls=processed_tool_calls,
            timestamp=datetime.utcnow().isoformat()
        )

    except ValueError as ve:
        # Handle value errors (e.g., conversation not found, permission issues)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        # Handle any other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred processing your request: {str(e)}"
        )


class GetMessageHistoryRequest(BaseModel):
    """Request model for getting message history with pagination."""
    limit: int = 50
    offset: int = 0


class MessageResponse(BaseModel):
    """Model for individual message response."""
    id: str
    role: str
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


class MessageHistoryResponse(BaseModel):
    """Response model for message history."""
    conversation_id: str
    messages: List[MessageResponse]
    pagination: Dict[str, int]


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    current_user: str = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session)
):
    """
    Retrieve message history for a specific conversation.

    Args:
        conversation_id: The ID of the conversation to retrieve messages for
        current_user: The authenticated user ID
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        session: Database session for database operations

    Returns:
        MessageHistoryResponse with conversation messages and pagination info
    """
    try:
        # Initialize service
        chat_service = ChatService(session)

        # Get conversation to verify user has access
        conversation = chat_service.get_conversation_by_id(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        if conversation.user_id != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You don't have permission to access this conversation"
            )

        # Get messages
        messages = chat_service.get_messages_for_conversation(
            conversation_id=conversation_id,
            limit=min(limit, 100),  # Cap limit at 100
            offset=offset
        )

        # Format messages
        formatted_messages = [
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp.isoformat() if msg.timestamp else None,
                metadata=msg.metadata_
            )
            for msg in messages
        ]

        # Get total count for pagination
        total_count_statement = select(func.count(Message.id)).where(
            Message.conversation_id == conversation_id
        )
        total_count = session.exec(total_count_statement).one()

        return {
            "conversation_id": conversation_id,
            "messages": formatted_messages,
            "pagination": {
                "limit": min(limit, 100),
                "offset": offset,
                "total_count": total_count,
                "has_more": offset + len(messages) < total_count
            }
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred retrieving message history: {str(e)}"
        )


class ConversationResponse(BaseModel):
    """Response model for conversation data."""
    id: str
    title: str
    user_id: str
    created_at: str
    updated_at: str
    message_count: Optional[int] = None


class ListConversationsResponse(BaseModel):
    """Response model for listing conversations."""
    conversations: List[ConversationResponse]
    pagination: Dict[str, int]


@router.get("/conversations")
async def list_user_conversations(
    current_user: str = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session)
):
    """
    List all conversations for the current user with pagination.

    Args:
        current_user: The authenticated user ID
        limit: Maximum number of conversations to return
        offset: Number of conversations to skip
        session: Database session for database operations

    Returns:
        ListConversationsResponse with user's conversations and pagination info
    """
    try:
        # Calculate total count of user's conversations
        total_count_statement = select(func.count(Conversation.id)).where(
            Conversation.user_id == current_user
        )
        total_count = session.exec(total_count_statement).one()

        # Get user's conversations with pagination
        conversations_statement = (
            select(Conversation)
            .where(Conversation.user_id == current_user)
            .order_by(Conversation.created_at.desc())
            .offset(offset)
            .limit(min(limit, 100))  # Cap limit at 100
        )
        conversations = session.exec(conversations_statement).all()

        # Format conversations
        formatted_conversations = []
        for conv in conversations:
            # Count messages in each conversation
            message_count_stmt = select(func.count(Message.id)).where(
                Message.conversation_id == conv.id
            )
            msg_count = session.exec(message_count_stmt).one()

            formatted_conversations.append(
                ConversationResponse(
                    id=conv.id,
                    title=conv.title,
                    user_id=conv.user_id,
                    created_at=conv.created_at.isoformat(),
                    updated_at=conv.updated_at.isoformat(),
                    message_count=msg_count
                )
            )

        return {
            "conversations": formatted_conversations,
            "pagination": {
                "limit": min(limit, 100),
                "offset": offset,
                "total_count": total_count,
                "has_more": offset + len(conversations) < total_count
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred retrieving conversations: {str(e)}"
        )


@router.put("/conversations/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    request: dict,  # Using dict for flexibility to update title only
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a conversation (currently supports updating the title).

    Args:
        conversation_id: The ID of the conversation to update
        request: Request containing the updates (e.g., {"title": "new title"})
        current_user: The authenticated user ID
        session: Database session for database operations

    Returns:
        Updated ConversationResponse
    """
    try:
        # Get conversation to verify user has access
        chat_service = ChatService(session)
        conversation = chat_service.get_conversation_by_id(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        if conversation.user_id != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You don't have permission to update this conversation"
            )

        # Update title if provided
        if "title" in request and isinstance(request["title"], str):
            updated_conversation = chat_service.update_conversation_title(
                conversation_id=conversation_id,
                title=request["title"]
            )

            # Count messages in the conversation
            message_count_stmt = select(func.count(Message.id)).where(
                Message.conversation_id == updated_conversation.id
            )
            msg_count = session.exec(message_count_stmt).one()

            return ConversationResponse(
                id=updated_conversation.id,
                title=updated_conversation.title,
                user_id=updated_conversation.user_id,
                created_at=updated_conversation.created_at.isoformat(),
                updated_at=updated_conversation.updated_at.isoformat(),
                message_count=msg_count
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only title updates are currently supported"
            )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred updating conversation: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a conversation and all its associated messages.

    Args:
        conversation_id: The ID of the conversation to delete
        current_user: The authenticated user ID
        session: Database session for database operations

    Returns:
        Confirmation message
    """
    try:
        # Get conversation to verify user has access
        chat_service = ChatService(session)
        conversation = chat_service.get_conversation_by_id(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        if conversation.user_id != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You don't have permission to delete this conversation"
            )

        # Delete all messages in the conversation first
        from sqlmodel import delete
        stmt = delete(Message).where(Message.conversation_id == conversation_id)
        session.exec(stmt)

        # Then delete the conversation itself
        stmt = delete(Conversation).where(Conversation.id == conversation_id)
        result = session.exec(stmt)
        session.commit()

        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        return {
            "message": "Conversation deleted successfully",
            "conversation_id": conversation_id
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred deleting conversation: {str(e)}"
        )