from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models.task import Task
from ..middleware.auth import get_current_user
from uuid import UUID

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
    task_data = task_update.dict(exclude_unset=True)
    # Ensure user_id cannot be changed during update
    if "user_id" in task_data:
        del task_data["user_id"]

    for key, value in task_data.items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)
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

    session.delete(task)
    session.commit()
    return {"ok": True}

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
    return task
