import uuid
from datetime import datetime, timedelta, timezone

from app.api.dependencies import CurrentUser, get_current_user
from app.main import app


def test_task_lifecycle(client):
    # Create
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Integration test task",
            "notes": "Testing the full lifecycle",
            "priority": "medium",
        },
    )

    assert response.status_code == 201

    task = response.json()
    task_id = task["id"]

    assert task["status"] == "open"

    # List
    response = client.get("/api/v1/tasks")

    assert response.status_code == 200

    items = response.json()["items"]

    assert any(item["id"] == task_id for item in items)

    # Get
    response = client.get(f"/api/v1/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["id"] == task_id

    # Patch
    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={
            "priority": "high",
        },
    )

    assert response.status_code == 200
    assert response.json()["priority"] == "high"

    # Complete
    response = client.post(f"/api/v1/tasks/{task_id}/complete")

    assert response.status_code == 200

    completed_task = response.json()

    assert completed_task["status"] == "done"
    assert completed_task["completed_at"] is not None

    completed_at = completed_task["completed_at"]

    # Complete again - must be idempotent
    response = client.post(f"/api/v1/tasks/{task_id}/complete")

    assert response.status_code == 200
    assert response.json()["completed_at"] == completed_at

    # Reopen
    response = client.post(f"/api/v1/tasks/{task_id}/reopen")

    assert response.status_code == 200

    reopened_task = response.json()

    assert reopened_task["status"] == "open"
    assert reopened_task["completed_at"] is None

    # Reopen again - must be a no-op
    updated_at = reopened_task["updated_at"]

    response = client.post(f"/api/v1/tasks/{task_id}/reopen")

    assert response.status_code == 200

    reopened_again = response.json()

    assert reopened_again["status"] == "open"
    assert reopened_again["completed_at"] is None
    assert reopened_again["updated_at"] == updated_at

    # Delete
    response = client.delete(f"/api/v1/tasks/{task_id}")

    assert response.status_code == 204

    # Confirm hard delete
    response = client.get(f"/api/v1/tasks/{task_id}")

    assert response.status_code == 404


def test_task_from_another_organization_returns_404(client):
    organization_a = uuid.uuid4()
    organization_b = uuid.uuid4()

    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(
            user_id=uuid.uuid4(),
            organization_id=organization_a,
        )
    )

    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Organization A task",
        },
    )

    assert response.status_code == 201

    task_id = response.json()["id"]

    app.dependency_overrides[get_current_user] = (
        lambda: CurrentUser(
            user_id=uuid.uuid4(),
            organization_id=organization_b,
        )
    )

    try:
        # GET
        response = client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 404

        # PATCH
        response = client.patch(
            f"/api/v1/tasks/{task_id}",
            json={"title": "Hacked task"},
        )
        assert response.status_code == 404

        # COMPLETE
        response = client.post(
            f"/api/v1/tasks/{task_id}/complete"
        )
        assert response.status_code == 404

        # REOPEN
        response = client.post(
            f"/api/v1/tasks/{task_id}/reopen"
        )
        assert response.status_code == 404

        # DELETE
        response = client.delete(
            f"/api/v1/tasks/{task_id}"
        )
        assert response.status_code == 404

        # LIST
        response = client.get("/api/v1/tasks")
        assert response.status_code == 200

        listed_ids = [
            item["id"]
            for item in response.json()["items"]
        ]

        assert task_id not in listed_ids

    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_cursor_pagination_returns_each_item_once(client):
    task_ids = []

    # Create 5 tasks
    for number in range(5):
        response = client.post(
            "/api/v1/tasks",
            json={
                "title": f"Pagination task {number}",
            },
        )

        assert response.status_code == 201

        task_ids.append(response.json()["id"])

    # Get first page
    response = client.get(
        "/api/v1/tasks",
        params={"limit": 2},
    )

    assert response.status_code == 200

    first_page = response.json()

    first_page_ids = [
        item["id"]
        for item in first_page["items"]
    ]

    next_cursor = first_page["next_cursor"]

    assert len(first_page_ids) == 2
    assert next_cursor is not None

    # Get second page
    response = client.get(
        "/api/v1/tasks",
        params={
            "limit": 2,
            "cursor": next_cursor,
        },
    )

    assert response.status_code == 200

    second_page = response.json()

    second_page_ids = [
        item["id"]
        for item in second_page["items"]
    ]

    assert len(second_page_ids) == 2

    # No item should appear on both pages
    assert set(first_page_ids).isdisjoint(
        second_page_ids
    )

    # All four returned items should be unique
    all_ids = first_page_ids + second_page_ids

    assert len(all_ids) == len(set(all_ids))


def test_status_filter(client):
    open_response = client.post(
        "/api/v1/tasks",
        json={"title": "Open task"},
    )

    assert open_response.status_code == 201

    open_task_id = open_response.json()["id"]

    done_response = client.post(
        "/api/v1/tasks",
        json={"title": "Done task"},
    )

    assert done_response.status_code == 201

    done_task_id = done_response.json()["id"]

    response = client.post(
        f"/api/v1/tasks/{done_task_id}/complete"
    )

    assert response.status_code == 200

    # Open filter
    response = client.get(
        "/api/v1/tasks",
        params={"status": "open"},
    )

    assert response.status_code == 200

    open_ids = {
        item["id"]
        for item in response.json()["items"]
    }

    assert open_task_id in open_ids
    assert done_task_id not in open_ids

    # Done filter
    response = client.get(
        "/api/v1/tasks",
        params={"status": "done"},
    )

    assert response.status_code == 200

    done_ids = {
        item["id"]
        for item in response.json()["items"]
    }

    assert done_task_id in done_ids
    assert open_task_id not in done_ids


def test_assignee_user_id_filter(client):
    assignee_a = str(uuid.uuid4())
    assignee_b = str(uuid.uuid4())

    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Assigned to A",
            "assignee_user_id": assignee_a,
        },
    )

    assert response.status_code == 201

    task_a_id = response.json()["id"]

    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Assigned to B",
            "assignee_user_id": assignee_b,
        },
    )

    assert response.status_code == 201

    task_b_id = response.json()["id"]

    response = client.get(
        "/api/v1/tasks",
        params={"assignee_user_id": assignee_a},
    )

    assert response.status_code == 200

    ids = {
        item["id"]
        for item in response.json()["items"]
    }

    assert task_a_id in ids
    assert task_b_id not in ids


def test_overdue_filter(client):
    past_due = (
        datetime.now(timezone.utc) - timedelta(hours=1)
    ).isoformat()

    future_due = (
        datetime.now(timezone.utc) + timedelta(hours=1)
    ).isoformat()

    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Overdue task",
            "due_at": past_due,
        },
    )

    assert response.status_code == 201

    overdue_task_id = response.json()["id"]

    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Future task",
            "due_at": future_due,
        },
    )

    assert response.status_code == 201

    future_task_id = response.json()["id"]

    response = client.get(
        "/api/v1/tasks",
        params={"overdue": True},
    )

    assert response.status_code == 200

    ids = {
        item["id"]
        for item in response.json()["items"]
    }

    assert overdue_task_id in ids
    assert future_task_id not in ids


def test_invalid_status_returns_422(client):
    response = client.get(
        "/api/v1/tasks",
        params={"status": "banana"},
    )

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["code"] == "validation_error"


def test_invalid_priority_returns_422(client):
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Invalid priority",
            "priority": "urgent",
        },
    )

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["code"] == "validation_error"


def test_priority_too_long_returns_422(client):
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Invalid priority",
            "priority": "extremehigh",
        },
    )

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["code"] == "validation_error"


def test_whitespace_title_returns_422(client):
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "   ",
        },
    )

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["code"] == "validation_error"


def test_notes_over_2000_characters_returns_422(client):
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Long notes",
            "notes": "a" * 2001,
        },
    )

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["code"] == "validation_error"


def test_patch_notes_over_2000_characters_returns_422(client):
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Patch notes test",
        },
    )

    assert response.status_code == 201

    task_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={
            "notes": "a" * 2001,
        },
    )

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["code"] == "validation_error"


def test_patch_null_title_returns_422(client):
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Original title",
        },
    )

    assert response.status_code == 201

    task_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={
            "title": None,
        },
    )

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["code"] == "validation_error"


def test_patch_null_priority_returns_422(client):
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Original title",
        },
    )

    assert response.status_code == 201

    task_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={
            "priority": None,
        },
    )

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["code"] == "validation_error"


def test_invalid_cursor_returns_422(client):
    response = client.get(
        "/api/v1/tasks",
        params={"cursor": "not-a-valid-cursor"},
    )

    assert response.status_code == 422

    body = response.json()

    assert body["error"]["code"] == "validation_error"


def test_unknown_route_returns_resource_not_found(client):
    response = client.get("/api/v1/does-not-exist")

    assert response.status_code == 404

    body = response.json()

    assert body["error"]["code"] == "not_found"
    assert body["error"]["message"] == "Resource not found"