"""add task list indexes

Revision ID: 5e4e914aa3b4
Revises: 3a7dcbf283c9
Create Date: 2026-09-13
"""

from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision = "5e4e914aa3b4"
down_revision = "3a7dcbf283c9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_tasks_org_created_at_id",
        "tasks",
        ["organization_id", "created_at", "id"],
    )

    op.create_index(
        "ix_tasks_org_status_created_at_id",
        "tasks",
        ["organization_id", "status", "created_at", "id"],
    )

    op.create_index(
        "ix_tasks_org_assignee_created_at_id",
        "tasks",
        ["organization_id", "assignee_user_id", "created_at", "id"],
    )

    op.create_index(
        "ix_tasks_org_due_at_open",
        "tasks",
        ["organization_id", "due_at"],
        postgresql_where=text("status = 'open'"),
    )


def downgrade() -> None:
    op.drop_index("ix_tasks_org_due_at_open", table_name="tasks")
    op.drop_index(
        "ix_tasks_org_assignee_created_at_id",
        table_name="tasks",
    )
    op.drop_index(
        "ix_tasks_org_status_created_at_id",
        table_name="tasks",
    )
    op.drop_index(
        "ix_tasks_org_created_at_id",
        table_name="tasks",
    )