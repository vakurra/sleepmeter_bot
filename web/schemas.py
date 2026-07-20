from pydantic import BaseModel


class UpdateProfileRequest(BaseModel):
    utc_offset: int | None = None
    reminder_time: str | None = None
    notifications_enabled: bool | None = None