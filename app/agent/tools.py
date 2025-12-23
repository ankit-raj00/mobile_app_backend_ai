from langchain_core.tools import tool
from typing import List, Optional
from app.db import db
from app.models.task_model import Task
from datetime import datetime

@tool
async def create_task(
    title: str,
    subject: str = None,
    topic: str = None,
    tags: List[str] = [],
    priority: str = "medium",
    type: str = "study"
) -> str:
    """
    Create a new task in the database.
    Use this when the user explicitly wants to add a new todo item or study goal.
    """
    new_task = Task(
        title=title,
        subject=subject,
        topic=topic,
        tags=tags,
        priority=priority,
        type=type,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    result = await db.tasks.insert_one(new_task.dict(by_alias=True))
    return f"Task created successfully. ID: {result.inserted_id}"

@tool
async def query_tasks(
    tags: List[str] = None,
    status: str = None,
    query: str = None,
    limit: int = 5
) -> List[dict]:
    """
    Search for tasks in the database.
    Use this to retrieve tasks for display, explanation, or management.
    - tags: Filter by tags (e.g., ['GATE'])
    - status: Filter by status (e.g., 'pending')
    - query: Text search on title/topic (simple regex match for now)
    """
    filter_query = {}
    if tags:
        filter_query["tags"] = {"$in": tags}
    if status:
        filter_query["status"] = status
    if query:
        filter_query["$or"] = [
            {"title": {"$regex": query, "$options": "i"}},
            {"topic": {"$regex": query, "$options": "i"}}
        ]

    cursor = db.tasks.find(filter_query).limit(limit)
    tasks = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string for LLM consumption
    for task in tasks:
        task["_id"] = str(task["_id"])
        
    return tasks

@tool
async def update_task(
    task_id: str,
    status: str = None,
    priority: str = None,
    add_tags: List[str] = None
) -> str:
    """
    Update an existing task's status, priority, or tags.
    """
    from bson import ObjectId
    try:
        oid = ObjectId(task_id)
    except:
        return "Invalid Task ID format."

    update_fields = {"updated_at": datetime.utcnow()}
    if status:
        update_fields["status"] = status
    if priority:
        update_fields["priority"] = priority
    
    operation = {"$set": update_fields}
    if add_tags:
        operation["$addToSet"] = {"tags": {"$each": add_tags}}

    result = await db.tasks.update_one({"_id": oid}, operation)
    
    if result.modified_count > 0:
        return f"Task {task_id} updated successfully."
    return "Task not found or no changes made."
