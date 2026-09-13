import uuid

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
    response = client.get(
        f"/api/v1/tasks/{task_id}"
    )

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
    response = client.post(
        f"/api/v1/tasks/{task_id}/complete"
    )

    assert response.status_code == 200

    completed_task = response.json()

    assert completed_task["status"] == "done"
    assert completed_task["completed_at"] is not None

    completed_at = completed_task["completed_at"]

    # Complete again - must be idempotent
    response = client.post(
        f"/api/v1/tasks/{task_id}/complete"
    )

    assert response.status_code == 200
    assert response.json()["completed_at"] == completed_at

    # Reopen
    response = client.post(
        f"/api/v1/tasks/{task_id}/reopen"
    )

    assert response.status_code == 200

    reopened_task = response.json()

    assert reopened_task["status"] == "open"
    assert reopened_task["completed_at"] is None

    # Delete
    response = client.delete(
        f"/api/v1/tasks/{task_id}"
    )

    assert response.status_code == 204

    # Confirm hard delete
    response = client.get(
        f"/api/v1/tasks/{task_id}"
    )

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

    try:
        # Organization A creates the task
        response = client.post(
            "/api/v1/tasks",
            json={
                "title": "Organization A task",
            },
        )

        assert response.status_code == 201

        task_id = response.json()["id"]

        # Switch to Organization B
        app.dependency_overrides[get_current_user] = (
            lambda: CurrentUser(
                user_id=uuid.uuid4(),
                organization_id=organization_b,
            )
        )

        # Organization B must receive 404
        response = client.get(
            f"/api/v1/tasks/{task_id}"
        )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()


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

    # Get second page using cursor
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