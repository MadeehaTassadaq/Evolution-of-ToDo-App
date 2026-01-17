from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from ..database import get_session
from ..models.task import Task
from ..middleware.auth import get_current_user
from uuid import UUID
import asyncio
import json

router = APIRouter()

@router.get("/")
def get_tasks(session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    # Get the user's ID from the authenticated user
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated properly")

    # Filter tasks by the authenticated user's ID
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    return tasks

@router.post("/")
def create_task(task: Task, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    # Set the user_id from the current authenticated user
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated properly")

    # Create a new task with the authenticated user's ID
    task.user_id = user_id
    session.add(task)
    session.commit()
    session.refresh(task)

    # Broadcast the new task to connected clients
    import asyncio
    asyncio.create_task(broadcast_task_update(
        str(user_id),
        {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        },
        "create"
    ))

    return task

@router.get("/{task_id}")
def get_task(task_id: UUID, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated properly")

    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify ownership
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied: You don't own this task")

    return task

@router.put("/{task_id}")
def update_task(task_id: UUID, task_update: Task, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated properly")

    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify ownership
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied: You don't own this task")

    # Update task fields, excluding the user_id to prevent user impersonation
    task_data = task_update.model_dump(exclude_unset=True)
    # Ensure user_id cannot be changed during update
    if "user_id" in task_data:
        del task_data["user_id"]

    for key, value in task_data.items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)

    # Broadcast the updated task to connected clients
    import asyncio
    asyncio.create_task(broadcast_task_update(
        str(user_id),
        {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        },
        "update"
    ))

    return task

@router.delete("/{task_id}")
def delete_task(task_id: UUID, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated properly")

    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify ownership
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied: You don't own this task")

    # Store task info for broadcasting before deletion
    task_info = {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None
    }

    session.delete(task)
    session.commit()

    # Broadcast the deleted task to connected clients
    import asyncio
    asyncio.create_task(broadcast_task_update(
        str(user_id),
        task_info,
        "delete"
    ))

    return {"ok": True}


# WebSocket for real-time task updates
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List

# Global variable to store connected WebSocket clients
connected_clients: Dict[str, List[WebSocket]] = {}


async def broadcast_task_update(user_id: str, task_data: dict, action: str):
    """
    Broadcast task updates to all connected clients for a specific user.

    Args:
        user_id: The ID of the user whose tasks changed
        task_data: The task data that changed
        action: The type of action ("create", "update", "delete", "complete")
    """
    if str(user_id) in connected_clients:
        message = {
            "action": action,
            "task": task_data,
            "timestamp": asyncio.get_event_loop().time()
        }

        disconnected_clients = []
        for websocket in connected_clients[str(user_id)]:
            try:
                await websocket.send_json(message)
            except WebSocketDisconnect:
                disconnected_clients.append(websocket)

        # Remove disconnected clients
        for websocket in disconnected_clients:
            if websocket in connected_clients[str(user_id)]:
                connected_clients[str(user_id)].remove(websocket)


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time task updates.

    Args:
        websocket: WebSocket connection
        user_id: User ID to subscribe to task updates
    """
    await websocket.accept()

    # Add user to connected clients
    if user_id not in connected_clients:
        connected_clients[user_id] = []

    connected_clients[user_id].append(websocket)

    try:
        while True:
            # Keep the connection alive
            data = await websocket.receive_text()
            # Optionally handle client messages here
    except WebSocketDisconnect:
        # Remove user from connected clients when disconnected
        if user_id in connected_clients and websocket in connected_clients[user_id]:
            connected_clients[user_id].remove(websocket)

@router.patch("/{task_id}/complete")
def complete_task(task_id: UUID, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated properly")

    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify ownership
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied: You don't own this task")

    # Toggle between pending and completed
    task.status = "pending" if task.status == "completed" else "completed"

    session.add(task)
    session.commit()
    session.refresh(task)

    # Broadcast the updated task to connected clients
    import asyncio
    asyncio.create_task(broadcast_task_update(
        str(user_id),
        {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        },
        "complete"
    ))

    return task
