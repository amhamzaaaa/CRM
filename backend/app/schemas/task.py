import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TaskCreateIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    notes: str | None = Field(default=None, max_length=2000)
    priority: str = "medium"
    due_at: datetime | None = None
    assignee_user_id: uuid.UUID | None = None
    customer_id: uuid.UUID | None = None


class TaskUpdateIn(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    notes: str | None = None
    priority: str | None = None
    due_at: datetime | None = None
    assignee_user_id: uuid.UUID | None = None
    customer_id: uuid.UUID | None = None


class TaskOut(BaseModel):
    id: uuid.UUID
    title: str
    notes: str | None
    status: str
    priority: str
    due_at: datetime | None
    assignee_user_id: uuid.UUID | None
    customer_id: uuid.UUID | None
    completed_at: datetime | None
    is_overdue: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class TaskListOut(BaseModel):
    items: list[TaskOut]
    next_cursor: str | None