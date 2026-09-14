import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.task import TaskCreateIn, TaskListOut, TaskOut, TaskUpdateIn
from app.services.task_service import (
    complete_task,
    create_task,
    delete_task,
    get_task,
    list_tasks,
    reopen_task,
    update_task,
)

router = APIRouter(
    prefix="/api/v1/tasks",
    tags=["tasks"],
)


@router.post(
    "",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
)
def create_task_endpoint(
    data: TaskCreateIn,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> TaskOut:
    return create_task(
        db=db,
        organization_id=current_user.organization_id,
        data=data,
    )


@router.get(
    "",
    response_model=TaskListOut,
)
def list_tasks_endpoint(
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    assignee_user_id: uuid.UUID | None = None,
    overdue: bool = False,
    cursor: str | None = None,
    limit: int = Query(
        default=25,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> TaskListOut:
    try:
        items, next_cursor = list_tasks(
            db=db,
            organization_id=current_user.organization_id,
            status=status_filter,
            assignee_user_id=assignee_user_id,
            overdue=overdue,
            cursor=cursor,
            limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return TaskListOut(
        items=items,
        next_cursor=next_cursor,
    )


@router.get(
    "/{task_id}",
    response_model=TaskOut,
)
def get_task_endpoint(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> TaskOut:
    task = get_task(
        db=db,
        organization_id=current_user.organization_id,
        task_id=task_id,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.patch(
    "/{task_id}",
    response_model=TaskOut,
)
def update_task_endpoint(
    task_id: uuid.UUID,
    data: TaskUpdateIn,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> TaskOut:
    task = update_task(
        db=db,
        organization_id=current_user.organization_id,
        task_id=task_id,
        data=data,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.post(
    "/{task_id}/complete",
    response_model=TaskOut,
)
def complete_task_endpoint(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> TaskOut:
    task = complete_task(
        db=db,
        organization_id=current_user.organization_id,
        task_id=task_id,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.post(
    "/{task_id}/reopen",
    response_model=TaskOut,
)
def reopen_task_endpoint(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> TaskOut:
    task = reopen_task(
        db=db,
        organization_id=current_user.organization_id,
        task_id=task_id,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task_endpoint(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    deleted = delete_task(
        db=db,
        organization_id=current_user.organization_id,
        task_id=task_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )