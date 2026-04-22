import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    username: str

    def create_update_dict(self) -> dict:
        # Exclude username — it's stored on UserProfile, not the User table.
        d = super().create_update_dict()
        d.pop("username", None)
        return d


class UserUpdate(schemas.BaseUserUpdate):
    pass
