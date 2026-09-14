import base64
import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreateIn, TaskOut, TaskUpdateIn

repository = TaskRepository()


def is_overdue(task: Task) -> bool:
    if task.status != "open":
        return False

    if task.due_at is None:
        return False

    return task.due_at < datetime.now(timezone.utc)


def encode_cursor(task: Task) -> str:
    cursor_data = {
        "created_at": task.created_at.isoformat(),
        "id": str(task.id),
    }

    cursor_json = json.dumps(cursor_data)

    return base64.urlsafe_b64encode(
        cursor_json.encode()
    ).decode()


def decode_cursor(cursor: str) -> tuple[datetime, uuid.UUID]:
    try:
        cursor_json = base64.urlsafe_b64decode(
            cursor.encode()
        ).decode()

        cursor_data = json.loads(cursor_json)

        created_at = datetime.fromisoformat(
            cursor_data["created_at"]
        )

        task_id = uuid.UUID(cursor_data["id"])

        return created_at, task_id

    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        raise ValueError("Invalid cursor")


def to_task_out(task: Task) -> TaskOut:
    return TaskOut(
        id=task.id,
        title=task.title,
        notes=task.notes,
        status=task.status,
        priority=task.priority,
        due_at=task.due_at,
        assignee_user_id=task.assignee_user_id,
        customer_id=task.customer_id,
        completed_at=task.completed_at,
        is_overdue=is_overdue(task),
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def create_task(
    db: Session,
    organization_id: uuid.UUID,
    data: TaskCreateIn,
) -> TaskOut:
    task = Task(
        organization_id=organization_id,
        title=data.title,
        notes=data.notes,
        priority=data.priority,
        due_at=data.due_at,
        assignee_user_id=data.assignee_user_id,
        customer_id=data.customer_id,
        status="open",
    )

    task = repository.create(db, task)

    return to_task_out(task)


def get_task(
    db: Session,
    organization_id: uuid.UUID,
    task_id: uuid.UUID,
) -> TaskOut | None:
    task = repository.get_by_id(
        db=db,
        task_id=task_id,
        organization_id=organization_id,
    )

    if task is None:
        return None

    return to_task_out(task)


def list_tasks(
    db: Session,
    organization_id: uuid.UUID,
    status: str | None = None,
    assignee_user_id: uuid.UUID | None = None,
    overdue: bool = False,
    cursor: str | None = None,
    limit: int = 25,
) -> tuple[list[TaskOut], str | None]:
    cursor_created_at = None
    cursor_id = None

    if cursor is not None:
        cursor_created_at, cursor_id = decode_cursor(cursor)

    tasks = repository.list_tasks(
        db=db,
        organization_id=organization_id,
        status=status,
        assignee_user_id=assignee_user_id,
        overdue=overdue,
        cursor_created_at=cursor_created_at,
        cursor_id=cursor_id,
        limit=limit + 1,
    )

    has_next_page = len(tasks) > limit

    if has_next_page:
        tasks = tasks[:limit]

    items = [
        to_task_out(task)
        for task in tasks
    ]

    if not has_next_page:
        return items, None

    next_cursor = encode_cursor(tasks[-1])

    return items, next_cursor


def update_task(
    db: Session,
    organization_id: uuid.UUID,
    task_id: uuid.UUID,
    data: TaskUpdateIn,
) -> TaskOut | None:
    task = repository.get_by_id(
        db=db,
        task_id=task_id,
        organization_id=organization_id,
    )

    if task is None:
        return None

    updates = data.model_dump(exclude_unset=True)

    if "title" in updates:
        task.title = updates["title"]

    if "notes" in updates:
        task.notes = updates["notes"]

    if "priority" in updates:
        task.priority = updates["priority"]

    if "due_at" in updates:
        task.due_at = updates["due_at"]

    if "assignee_user_id" in updates:
        task.assignee_user_id = updates["assignee_user_id"]

    if "customer_id" in updates:
        task.customer_id = updates["customer_id"]

    task.updated_at = datetime.now(timezone.utc)

    task = repository.update(db, task)

    return to_task_out(task)


def delete_task(
    db: Session,
    organization_id: uuid.UUID,
    task_id: uuid.UUID,
) -> bool:
    task = repository.get_by_id(
        db=db,
        task_id=task_id,
        organization_id=organization_id,
    )

    if task is None:
        return False

    repository.delete(db, task)

    return True


def complete_task(
    db: Session,
    organization_id: uuid.UUID,
    task_id: uuid.UUID,
) -> TaskOut | None:
    task = repository.get_by_id(
        db=db,
        task_id=task_id,
        organization_id=organization_id,
    )

    if task is None:
        return None

    if task.status == "open":
        task.status = "done"
        task.completed_at = datetime.now(timezone.utc)
        task.updated_at = datetime.now(timezone.utc)

        task = repository.update(db, task)

    return to_task_out(task)


def reopen_task(
    db: Session,
    organization_id: uuid.UUID,
    task_id: uuid.UUID,
) -> TaskOut | None:
    task = repository.get_by_id(
        db=db,
        task_id=task_id,
        organization_id=organization_id,
    )

    if task is None:
        return None

    task.status = "open"
    task.completed_at = None
    task.updated_at = datetime.now(timezone.utc)

    task = repository.update(db, task)

    return to_task_out(task)