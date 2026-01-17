from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import uuid

from ..middleware.auth import get_current_user
from ..models.user import User
from ..database import get_session
from sqlmodel import Session

router = APIRouter(prefix="/v1", tags=["chat"])
security = HTTPBearer()

# Models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: str

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: str

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    timestamp: str

# Mock database storage (in a real app, this would be stored in the database)
conversations_db = {}
messages_db = {}

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Handle chat requests - in a real implementation, this would connect to the AI agent
    For now, returning mock responses
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    # Get user from database using the user_id
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    # Generate or use conversation ID
    conversation_id = request.conversation_id or str(uuid.uuid4())

    # Store the user message (mock implementation)
    user_message_id = str(uuid.uuid4())
    if conversation_id not in messages_db:
        messages_db[conversation_id] = []

    messages_db[conversation_id].append({
        'id': user_message_id,
        'conversation_id': conversation_id,
        'role': 'user',
        'content': request.message,
        'timestamp': datetime.utcnow().isoformat()
    })

    # Generate a mock AI response (in a real implementation, this would call the AI agent)
    # For demo purposes, we'll return a simple response
    ai_response = f"I received your message: '{request.message}'. How can I help you with your tasks?"

    # Store the AI response
    ai_message_id = str(uuid.uuid4())
    messages_db[conversation_id].append({
        'id': ai_message_id,
        'conversation_id': conversation_id,
        'role': 'assistant',
        'content': ai_response,
        'timestamp': datetime.utcnow().isoformat()
    })

    # Create conversation if it doesn't exist
    if conversation_id not in conversations_db:
        conversations_db[conversation_id] = {
            'id': conversation_id,
            'user_id': str(user.id),
            'title': request.message[:50] + "..." if len(request.message) > 50 else request.message,
            'created_at': datetime.utcnow().isoformat()
        }

    return ChatResponse(
        response=ai_response,
        conversation_id=conversation_id,
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    List user's conversations
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    # Get user from database using the user_id
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    # Return conversations for this user
    user_conversations = [
        ConversationResponse(
            id=conv['id'],
            user_id=conv['user_id'],
            title=conv['title'],
            created_at=conv['created_at']
        )
        for conv in conversations_db.values()
        if conv['user_id'] == str(user.id)
    ]

    return user_conversations


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Get messages for a specific conversation
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    # Get user from database using the user_id
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    # Verify that the conversation belongs to the user
    conversation = conversations_db.get(conversation_id)
    if not conversation or conversation['user_id'] != str(user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get messages for this conversation
    messages = messages_db.get(conversation_id, [])
    return [
        MessageResponse(
            id=msg['id'],
            conversation_id=msg['conversation_id'],
            role=msg['role'],
            content=msg['content'],
            timestamp=msg['timestamp']
        )
        for msg in messages
    ]


# Mock initialization for testing
def init_mock_data():
    """Initialize some mock data for testing"""
    pass