# CRM Backend

Backend for a CRM application's Follow-up Tasks feature, built with FastAPI and PostgreSQL.

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- pytest
- Ruff
- mypy
- Docker Compose

## Project Structure

```text
backend/
├── alembic/
│   ├── versions/
│   └── env.py
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   └── tasks.py
│   │   └── dependencies.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── database.py
│   │   └── session.py
│   ├── models/
│   │   └── task.py
│   ├── repositories/
│   │   └── task_repository.py
│   ├── schemas/
│   │   └── task.py
│   ├── services/
│   │   └── task_service.py
│   └── main.py
├── tests/
│   ├── integration/
│   │   └── test_tasks.py
│   ├── unit/
│   │   └── test_task_service.py
│   └── conftest.py
├── .env
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── requirements.txt
```

## Architecture

The backend follows a layered architecture:

```text
HTTP Route
    |
Service
    |
Repository
    |
SQLAlchemy
    |
PostgreSQL
```

- `api/routes`: HTTP request and response handling and route definitions
- `schemas`: Pydantic request and response validation and API data models
- `services`: Business and application logic
- `repositories`: Database queries
- `models`: SQLAlchemy database models
- `db`: Database engine and session setup
- `alembic`: Database migrations
- `tests`: Unit tests and PostgreSQL integration tests

## Follow-up Tasks

The API base path is `/api/v1/tasks`.

### Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/v1/tasks` | Create a task |
| `GET` | `/api/v1/tasks` | List tasks |
| `GET` | `/api/v1/tasks/{task_id}` | Get a task |
| `PATCH` | `/api/v1/tasks/{task_id}` | Update a task |
| `POST` | `/api/v1/tasks/{task_id}/complete` | Complete a task |
| `POST` | `/api/v1/tasks/{task_id}/reopen` | Reopen a task |
| `DELETE` | `/api/v1/tasks/{task_id}` | Delete a task |

### Task Fields

- `title`
- `notes`
- `status`: `open` or `done`
- `priority`: `low`, `medium`, or `high`
- `due_at`
- `assignee_user_id`
- `customer_id`
- `completed_at`
- `is_overdue`
- `created_at`
- `updated_at`

`is_overdue` is calculated by the server and is not stored as a database field. It is `true` only when the task is open, has a due date, and that due date is in the past.

### List Filters

`GET /api/v1/tasks` supports the following query parameters:

- `status`
- `assignee_user_id`
- `overdue`
- `cursor`
- `limit`

Pagination uses cursor-based keyset pagination rather than `OFFSET` pagination. The default limit is 25 items, and the maximum limit is 100 items per request.

## Database

PostgreSQL runs through Docker Compose. From the `backend/` directory, start the database with:

```powershell
docker compose up -d
```

PostgreSQL is exposed locally on port `5433`. The application uses the following database connection setting:

```dotenv
DATABASE_URL=postgresql+psycopg://crm_user:crm_password@localhost:5433/crm
```

Keep real credentials and other secrets out of version control.

## Database Migrations

Alembic manages database schema migrations. After starting PostgreSQL, apply the migrations from the `backend/` directory:

```powershell
alembic upgrade head
```

## Running the API

From the `backend/` directory, start FastAPI with:

```powershell
uvicorn app.main:app --reload
```

The API is available at:

- API: http://127.0.0.1:8000
- Swagger documentation: http://127.0.0.1:8000/docs
- Health endpoint: http://127.0.0.1:8000/health

## Running Tests

Integration tests use the real PostgreSQL database rather than SQLite or mocked database behavior.

Run the test suite from `backend/` with:

```powershell
python -m pytest -v
```

The tests cover:

- Task lifecycle
- Cross-organization isolation
- Cursor pagination
- Overdue calculation
- Open tasks with future due dates
- Open tasks without due dates
- Completed tasks with past due dates
- Idempotent task completion

Current result: **7 passed**.

## Linting

Run Ruff from `backend/`:

```powershell
ruff check .
```

Current result: **All checks passed**.

## Type Checking

Run mypy from `backend/`:

```powershell
mypy app
```

Current result: **Success: no issues found**.

## Authentication and Organization Scoping

Authentication is represented by a stub dependency so the Follow-up Tasks feature can be exercised without implementing the full production authentication system.

- The organization ID comes from the authenticated user context.
- The organization ID is not accepted from the request body, query parameters, or other client input.
- All task database queries are scoped by organization.
- A task belonging to another organization returns `404 Not Found` rather than `403 Forbidden`.

## Error Responses

API errors use the following structure:

```json
{
  "error": {
    "code": "not_found",
    "message": "Task not found",
    "details": null,
    "request_id": "..."
  }
}
```

Validation failures use the `validation_error` code. Invalid cursors return HTTP `422` with a validation error response.

## Development Notes

- Make database schema changes through new Alembic migrations.
- Keep business rules in the service layer.
- Keep database queries in repositories.
- Keep route handlers thin.
- Use PostgreSQL for integration tests.

## Deliberate Scope and Omissions

The Follow-up Tasks implementation does not include:

- Recurring tasks
- Reminders
- Notifications
- Calendar synchronization
- Bulk task operations
- Full production authentication and authorization

These features are outside the required core scope of the Follow-up Tasks assignment.
