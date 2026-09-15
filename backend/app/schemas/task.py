import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

Priority = Literal["low", "medium", "high"]
Status = Literal["open", "done"]

Title = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=200,
    ),
]


class TaskCreateIn(BaseModel):
    title: Title
    notes: str | None = Field(
        default=None,
        max_length=2000,
    )
    priority: Priority = "medium"
    due_at: datetime | None = None
    assignee_user_id: uuid.UUID | None = None
    customer_id: uuid.UUID | None = None


class TaskUpdateIn(BaseModel):
    title: Title | None = None
    notes: str | None = Field(
        default=None,
        max_length=2000,
    )
    priority: Priority | None = None
    due_at: datetime | None = None
    assignee_user_id: uuid.UUID | None = None
    customer_id: uuid.UUID | None = None


class TaskOut(BaseModel):
    id: uuid.UUID
    title: str
    notes: str | None
    status: Status
    priority: Priority
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