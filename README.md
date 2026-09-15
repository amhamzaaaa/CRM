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
│   │   ├── dependencies.py
│   │   └── errors.py
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
├── .env.example
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
    v
Service
    |
    v
Repository
    |
    v
SQLAlchemy
    |
    v
PostgreSQL
```

- `api/routes`: HTTP request and response handling and route definitions
- `api/dependencies.py`: Request dependencies and current-user context
- `api/errors.py`: Standardized API error responses
- `schemas`: Pydantic request and response validation and API data models
- `services`: Business and application logic
- `repositories`: Database queries
- `models`: SQLAlchemy database models
- `db`: Database engine and session setup
- `core`: Application configuration
- `alembic`: Database migrations
- `tests`: Unit tests and PostgreSQL integration tests

## Setup

From the repository root, change to the backend directory:

```powershell
cd backend
```

Create and activate a virtual environment, then install the project dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a local environment file from the safe example:

```powershell
Copy-Item .env.example .env
```

The `.env` file is ignored by Git and should contain local secrets. The committed `.env.example` file contains safe placeholder values.

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

The task API uses `customer_id` as the customer reference field. The previous `lead_id` naming was changed to `customer_id` so the API contract, Pydantic schemas, SQLAlchemy model, service layer, and database schema consistently use the same field name.

### List Filters

`GET /api/v1/tasks` supports the following query parameters:

- `status`
- `assignee_user_id`
- `overdue`
- `cursor`
- `limit`

Pagination uses cursor-based keyset pagination and does not use `OFFSET` pagination. The default limit is 25 items, and the maximum limit is 100 items per request.

## Database

PostgreSQL runs through Docker Compose. From the `backend/` directory, start the database with:

```powershell
docker compose up -d
```

PostgreSQL is exposed locally on port `5433`. Use the following connection setting with a local password:

```dotenv
DATABASE_URL=postgresql+psycopg://crm_user:your_password@localhost:5433/crm
```

Keep local secrets in `.env` and out of version control. `.env` is ignored by Git, while `.env.example` is safe to commit and uses placeholder values.

## Database Migrations

Alembic manages database schema migrations. From the `backend/` directory, apply migrations with:

```powershell
alembic upgrade head
```

Check the current migration:

```powershell
alembic current
```

Create a new migration for a schema change:

```powershell
alembic revision --autogenerate -m "describe your change"
```

Review generated migrations before applying them. Schema changes should be made through new Alembic migrations, and migrations already applied to shared environments should not be modified.

## Running the API

From the `backend/` directory, start FastAPI with:

```powershell
uvicorn app.main:app --reload
```

The API is available at:

| Resource | URL |
| --- | --- |
| API | http://127.0.0.1:8000 |
| Swagger documentation | http://127.0.0.1:8000/docs |
| Health endpoint | http://127.0.0.1:8000/health |

The `/health` endpoint checks the PostgreSQL connection.

## Testing

Integration tests use the real PostgreSQL database rather than SQLite or mocked database behavior.

Run the test suite from the `backend/` directory:

```powershell
python -m pytest -v
```

The tests cover:

- Task lifecycle
- Cross-organization isolation
- Cursor pagination
- Status filtering
- Assignee filtering
- Overdue filtering
- Overdue calculation
- Open tasks with future due dates
- Open tasks without due dates
- Completed tasks with past due dates
- Idempotent task completion
- Idempotent task reopening
- Input validation
- Invalid cursors
- Standardized error responses
- Unknown routes

Current result: **20 passed**.

There are currently 2 dependency deprecation warnings from the FastAPI/Starlette testing stack. They do not cause test failures.

## Linting

Run Ruff from the `backend/` directory:

```powershell
ruff check .
```

Current result: **All checks passed**.

## Type Checking

Run mypy from the `backend/` directory:

```powershell
mypy app
```

Current result: **Success: no issues found**.

## Authentication and Organization Scoping

Authentication is currently represented by a stub dependency so the Follow-up Tasks feature can be tested without implementing the full production authentication system.

- The organization ID comes from the current-user context.
- The organization ID is not accepted from the request body, query parameters, or other client input.
- All task database queries are scoped by organization.
- A task belonging to another organization returns `404 Not Found` rather than `403 Forbidden`.
- The current-user dependency is a development stub.
- The stub should be replaced by the application's production authentication mechanism when authentication is implemented.

## Error Responses

API errors use the following standardized structure:

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

- Validation failures use the `validation_error` code.
- Invalid cursors return HTTP `422`.
- Request IDs are returned through the `X-Request-ID` response header.
- Request IDs are also included in standardized error responses.
- Unknown routes use the standardized `404` error response.

## Development Notes

- Make database schema changes through new Alembic migrations.
- Do not modify migrations that have already been applied to shared environments.
- Keep business rules in the service layer.
- Keep database queries in repositories.
- Keep route handlers thin.
- Use PostgreSQL for integration tests.
- Keep secrets in `.env` and out of version control.
- Keep `.env.example` safe to commit and use placeholders instead of real credentials.

## Deliberate Scope and Omissions

The Follow-up Tasks implementation does not include:

- Recurring tasks
- Reminders
- Notifications
- Calendar synchronization
- Bulk task operations
- Full production authentication and authorization

These features are outside the required core scope of the Follow-up Tasks assignment.
