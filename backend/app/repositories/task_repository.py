import uuid
from datetime import datetime, timezone

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models.task import Task


class TaskRepository:

    def create(
        self,
        db: Session,
        task: Task,
    ) -> Task:
        db.add(task)
        db.commit()
        db.refresh(task)

        return task

    def get_by_id(
        self,
        db: Session,
        task_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Task | None:
        statement = select(Task).where(
            Task.id == task_id,
            Task.organization_id == organization_id,
        )

        return db.scalar(statement)

    def list_tasks(
        self,
        db: Session,
        organization_id: uuid.UUID,
        status: str | None = None,
        assignee_user_id: uuid.UUID | None = None,
        overdue: bool = False,
        cursor_created_at: datetime | None = None,
        cursor_id: uuid.UUID | None = None,
        limit: int = 25,
    ) -> list[Task]:
        conditions = [
            Task.organization_id == organization_id,
        ]

        if status is not None:
            conditions.append(Task.status == status)

        if assignee_user_id is not None:
            conditions.append(
                Task.assignee_user_id == assignee_user_id
            )

        if overdue:
            conditions.extend(
                [
                    Task.status == "open",
                    Task.due_at.is_not(None),
                    Task.due_at < datetime.now(timezone.utc),
                ]
            )

        if cursor_created_at is not None and cursor_id is not None:
            conditions.append(
                or_(
                    Task.created_at < cursor_created_at,
                    and_(
                        Task.created_at == cursor_created_at,
                        Task.id < cursor_id,
                    ),
                )
            )

        statement = (
            select(Task)
            .where(*conditions)
            .order_by(
                Task.created_at.desc(),
                Task.id.desc(),
            )
            .limit(limit)
        )

        return list(db.scalars(statement).all())

    def update(
        self,
        db: Session,
        task: Task,
    ) -> Task:
        db.commit()
        db.refresh(task)

        return task

    def delete(
        self,
        db: Session,
        task: Task,
    ) -> None:
        db.delete(task)
        db.commit()