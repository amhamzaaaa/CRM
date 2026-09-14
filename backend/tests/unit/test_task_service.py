import uuid
from datetime import datetime, timedelta, timezone

from app.models.task import Task
from app.services.task_service import is_overdue


def make_task(
    status: str = "open",
    due_at: datetime | None = None,
) -> Task:
    return Task(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        title="Test task",
        status=status,
        priority="medium",
        due_at=due_at,
    )


def test_open_task_with_past_due_date_is_overdue():
    task = make_task(
        status="open",
        due_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )

    assert is_overdue(task) is True


def test_open_task_with_future_due_date_is_not_overdue():
    task = make_task(
        status="open",
        due_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    assert is_overdue(task) is False


def test_open_task_without_due_date_is_not_overdue():
    task = make_task(
        status="open",
        due_at=None,
    )

    assert is_overdue(task) is False


def test_done_task_with_past_due_date_is_not_overdue():
    task = make_task(
        status="done",
        due_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )

    assert is_overdue(task) is False