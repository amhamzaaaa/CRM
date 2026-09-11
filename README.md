# CRM Backend

This project is the backend for the CRM application. It uses FastAPI for the HTTP API and is intended to connect to PostgreSQL as database features are added.

## Folder organization

### `app/`

The main FastAPI application package. Application code that belongs to the backend lives here.

Put API, schema, model, service, and database code in their matching subfolders. Do not put frontend files, deployment scripts, or future infrastructure code here unless a dedicated folder is added for it.

The subfolders separate HTTP handling, data shapes, database models, business logic, and database setup while keeping them part of one application.

### `app/api/`

The API layer handles HTTP requests and responses.

Put API-level organization and route wiring here. Do not put business rules, database models, or frontend code here; those belong in `services/`, `models/`, or the frontend project.

The route files in `routes/` are exposed through this layer and call services when application work is needed.

### `app/api/routes/`

This folder contains the actual FastAPI endpoint files, such as future `users.py`, `leads.py`, or `auth.py` modules.

Put request handling, status codes, and route declarations here. Do not put database queries or large business rules here; delegate those to `db/` and `services/`.

Routes receive HTTP input, use schemas for its shape, call services, and return API responses.

### `app/schemas/`

This folder contains Pydantic schemas that define and validate data entering and leaving the API.

Put request and response data models here. Do not put database table models or business workflows here; use `models/` and `services/` for those concerns.

Routes use schemas to keep API data contracts clear and consistent.

### `app/models/`

This folder contains database models representing PostgreSQL tables.

Put persistence model definitions here. Do not put API request and response schemas or business operations here; those belong in `schemas/` and `services/`.

Database setup in `db/` will use these models when database features are implemented.

### `app/services/`

This folder contains application business logic, such as creating, assigning, updating, or processing leads.

Put reusable workflows and rules here. Do not put HTTP route declarations or direct frontend code here; routes belong in `api/routes/`.

Routes call services so business behavior stays separate from request handling and database setup.

### `app/db/`

This folder contains PostgreSQL database setup, including the engine, sessions, connection settings, and related configuration.

Put database connection and persistence setup here. Do not put API endpoints or general business logic here; those belong in `api/` and `services/`.

Models describe database data, while this folder provides the database connection they will use.

### `tests/`

This folder contains automated tests for the backend.

Put tests for routes, schemas, services, and database behavior here. Do not put application implementation code here; implementation belongs under `app/`.

Tests exercise the application layers and help verify behavior as each feature is added.

## Run the application

1. Create and activate a virtual environment.
2. Install dependencies:

   ```text
   pip install -r requirements.txt
   ```

3. Start the development server from this directory:

   ```text
   uvicorn app.main:app --reload
   ```

The API will be available at `http://127.0.0.1:8000`. FastAPI's interactive documentation is at `/docs`.

The `.env` file is reserved for local environment values such as the PostgreSQL URL. Do not put real secrets in source control.

Folders for migrations/Alembic, repositories, integrations, workers, and other infrastructure will be added later when the application actually needs them.
