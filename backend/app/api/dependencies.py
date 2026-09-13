import uuid


class CurrentUser:
    def __init__(
        self,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> None:
        self.user_id = user_id
        self.organization_id = organization_id


def get_current_user() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        organization_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
    )