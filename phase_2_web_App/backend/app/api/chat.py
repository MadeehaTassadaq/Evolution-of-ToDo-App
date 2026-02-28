from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, AsyncIterator, List
import uuid
import json
import os

from ..middleware.auth import get_current_user
from ..models.user import User
from ..database import get_session
from sqlmodel import Session, select
from ..models.task import Task

router = APIRouter(prefix="/v1", tags=["chat"])
security = HTTPBearer()

# OpenAI API integration
from openai import OpenAI

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================================================================
# Data Models
# ============================================================================

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

# ============================================================================
# ChatKit Streaming Endpoint with Real AI Integration
# ============================================================================

@router.post("/chatkit")
async def chatkit_streaming_endpoint(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    ChatKit streaming endpoint with real OpenAI AI integration and MCP tools.

    Expected request format:
    {
        "thread_id": "optional-conversation-id",
        "message": "user message"
    }
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    async def event_stream() -> AsyncIterator[str]:
        """Generator function that yields SSE events."""
        try:
            # Get raw request body
            request_body = await request.body()
            request_data = json.loads(request_body) if request_body else {}
            user_message = request_data.get("message", "")
            thread_id = request_data.get("thread_id", str(uuid.uuid4()))

            if not user_message:
                # Send greeting if no message
                greeting_msg_id = str(uuid.uuid4())
                greeting = "Hi! I'm your Todo AI Assistant. I can help you:\n\n• Add a new task\n• Show your tasks\n• Update a task\n• Mark a task complete\n• Delete a task\n\nWhat would you like to do?"

                yield f"event: thread.message.item.created\ndata: {json.dumps({'id': greeting_msg_id, 'thread_id': thread_id, 'role': 'assistant', 'content': [{'type': 'text', 'text': greeting}], 'created_at': datetime.utcnow().isoformat()})}\n\n"
                yield f"event: thread.item.done\ndata: {json.dumps({'item_id': greeting_msg_id})}\n\n"
                return

            # Get conversation history for context
            messages = [
                {"role": "system", "content": f"""You are a helpful todo management assistant for a task management app. You help users manage their tasks through natural language.

Available tools you can use:
1. add_task(title: str, description: str = None) - Add a new task
2. list_tasks(status: str = None) - List all tasks or filter by status (pending/completed)
3. update_task(task_id: str, title: str = None, description: str = None, status: str = None) - Update a task
4. complete_task(task_id: str) - Mark a task as completed
5. delete_task(task_id: str) - Delete a task

The user's ID is: {user_id}
The user's email is: {user.email}

When you need to use a tool, respond with a tool call in this format:
TOOL:<tool_name>:<json_parameters>

For example:
TOOL:add_task:{"title": "Buy groceries", "description": "Go to the store"}

After executing a tool, report the result to the user in a friendly way.

Always be concise and helpful. If the user asks to show tasks, use the list_tasks tool."""}
            ]

            # Add recent tasks as context
            tasks = db.exec(select(Task).where(Task.user_id == user_id).limit(10)).all()
            if tasks:
                task_context = "\n\nRecent tasks:\n" + "\n".join([
                    f"- {t.title} (Status: {t.status}, ID: {t.id})"
                    for t in tasks
                ])
                messages[0]["content"] += task_context

            # Add user message
            messages.append({"role": "user", "content": user_message})

            # Call OpenAI API
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "add_task",
                            "description": "Add a new task to the user's todo list",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "The task title"},
                                    "description": {"type": "string", "description": "Optional description"}
                                },
                                "required": ["title"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "list_tasks",
                            "description": "List all tasks or filter by status",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "enum": ["pending", "completed", "all"], "description": "Filter by status"}
                                }
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "update_task",
                            "description": "Update an existing task",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "task_id": {"type": "string", "description": "The task ID"},
                                    "title": {"type": "string", "description": "New title"},
                                    "description": {"type": "string", "description": "New description"},
                                    "status": {"type": "string", "enum": ["pending", "completed"], "description": "New status"}
                                },
                                "required": ["task_id"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "complete_task",
                            "description": "Mark a task as completed",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "task_id": {"type": "string", "description": "The task ID"}
                                },
                                "required": ["task_id"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "delete_task",
                            "description": "Delete a task",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "task_id": {"type": "string", "description": "The task ID"}
                                },
                                "required": ["task_id"]
                            }
                        }
                    }
                ],
                tool_choice="auto"
            )

            assistant_message = response.choices[0].message
            tool_calls = assistant_message.tool_calls

            final_response = ""

            # Execute tool calls if any
            if tool_calls:
                tool_results = []
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    try:
                        # Execute the tool
                        if function_name == "add_task":
                            new_task = Task(
                                title=function_args.get("title", "Untitled"),
                                description=function_args.get("description", ""),
                                user_id=user_id,
                                status="pending"
                            )
                            db.add(new_task)
                            db.commit()
                            db.refresh(new_task)
                            result = f"✅ Added task: {new_task.title}"

                        elif function_name == "list_tasks":
                            status_filter = function_args.get("status")
                            statement = select(Task).where(Task.user_id == user_id)
                            if status_filter and status_filter != "all":
                                statement = statement.where(Task.status == status_filter)
                            tasks = db.exec(statement).all()

                            if tasks:
                                task_list = "\n".join([f"• {t.title} ({t.status})" for t in tasks])
                                result = f"📋 Your tasks:\n{task_list}"
                            else:
                                result = "📋 No tasks found"

                        elif function_name == "update_task":
                            task_id = function_args.get("task_id")
                            task = db.get(Task, task_id)
                            if task and task.user_id == user_id:
                                if "title" in function_args:
                                    task.title = function_args["title"]
                                if "description" in function_args:
                                    task.description = function_args["description"]
                                if "status" in function_args:
                                    task.status = function_args["status"]
                                db.commit()
                                result = f"✅ Updated task: {task.title}"
                            else:
                                result = "❌ Task not found"

                        elif function_name == "complete_task":
                            task_id = function_args.get("task_id")
                            task = db.get(Task, task_id)
                            if task and task.user_id == user_id:
                                task.status = "completed"
                                db.commit()
                                result = f"✅ Completed task: {task.title}"
                            else:
                                result = "❌ Task not found"

                        elif function_name == "delete_task":
                            task_id = function_args.get("task_id")
                            task = db.get(Task, task_id)
                            if task and task.user_id == user_id:
                                title = task.title
                                db.delete(task)
                                db.commit()
                                result = f"🗑️ Deleted task: {title}"
                            else:
                                result = "❌ Task not found"

                        else:
                            result = f"❓ Unknown tool: {function_name}"

                        tool_results.append(result)

                    except Exception as e:
                        tool_results.append(f"❌ Error executing {function_name}: {str(e)}")

                # Combine tool results for final response
                final_response = "\n\n".join(tool_results)

                # If there's also text content from the assistant, include it
                if assistant_message.content:
                    final_response = assistant_message.content + "\n\n" + final_response
            else:
                # No tool calls, just use the text response
                final_response = assistant_message.content or "I understand. How can I help you with your tasks?"

            # Generate message ID
            ai_message_id = str(uuid.uuid4())

            # Send thread.message.item.created event with the response
            message_created_event = {
                "id": ai_message_id,
                "thread_id": thread_id,
                "role": "assistant",
                "content": [{"type": "text", "text": final_response}],
                "created_at": datetime.utcnow().isoformat()
            }
            yield f"event: thread.message.item.created\ndata: {json.dumps(message_created_event)}\n\n"

            # Send thread.item.done event when complete
            item_done_event = {
                "item_id": ai_message_id
            }
            yield f"event: thread.item.done\ndata: {json.dumps(item_done_event)}\n\n"

        except Exception as e:
            # Send error event
            import traceback
            traceback.print_exc()
            error_data = json.dumps({"error": str(e)})
            yield f"event: error\ndata: {error_data}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
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

    # Get user from database
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    # Generate conversation ID
    conversation_id = request.conversation_id or str(uuid.uuid4())

    # Simple response (legacy)
    ai_response = f"I received: '{request.message}'. Please use the ChatKit widget for full AI features."

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
    """List user's conversations (placeholder for future use)"""
    return []


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Get messages for a conversation (placeholder for future use)"""
    return []
