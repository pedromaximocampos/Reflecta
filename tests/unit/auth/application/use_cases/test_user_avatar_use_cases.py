from io import BytesIO

import pytest

from src.modules.auth.application.dto import (
    ProcessedUserAvatarDTO,
    StoredUserAvatarDTO,
)
from src.modules.auth.application.use_cases.get_user_profile import (
    GetUserProfileUseCase,
)
from src.modules.auth.application.use_cases.update_user_avatar import (
    RemoveUserAvatarInputDTO,
    RemoveUserAvatarUseCase,
    ReplaceUserAvatarInputDTO,
    ReplaceUserAvatarUseCase,
)
from tests.support.builders.user_builder import UserBuilder


class UsersRepositoryFake:
    def __init__(self, user) -> None:
        self.user = user
        self.updated = 0

    async def find_by_id(self, user_id):
        if self.user is not None and self.user.id == user_id:
            return self.user
        return None

    async def update_user_avatar(self, user):
        self.user = user
        self.updated += 1


class UnitOfWorkFake:
    def __init__(self, user) -> None:
        self.users_repository = UsersRepositoryFake(user)
        self.commits = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def commit(self):
        self.commits += 1


class ProcessorFake:
    async def process(self, **kwargs):
        return ProcessedUserAvatarDTO(
            content=BytesIO(b"normalized"),
            content_type="image/webp",
            size_bytes=10,
            extension="webp",
        )


class StorageFake:
    def __init__(self) -> None:
        self.uploaded = None
        self.deleted = []

    async def upload(self, **kwargs):
        self.uploaded = kwargs
        return StoredUserAvatarDTO(
            object_key=kwargs["object_key"],
            content_type=kwargs["content_type"],
            size_bytes=kwargs["size_bytes"],
        )

    async def delete(self, *, object_key):
        self.deleted.append(object_key)

    async def create_read_url(self, *, object_key):
        return f"https://signed.example.test/{object_key}"


class ULIDGeneratorFake:
    def generate_ulid(self):
        return "01AVATAR000000000000000000"


@pytest.mark.asyncio
async def test_replace_avatar_commits_new_key_and_removes_previous_object() -> None:
    previous_key = "users/user-id/avatar/previous.webp"
    user = UserBuilder().with_avatar_object_key(previous_key).build()
    uow = UnitOfWorkFake(user)
    storage = StorageFake()
    use_case = ReplaceUserAvatarUseCase(
        auth_unit_of_work=uow,
        avatar_processor=ProcessorFake(),
        avatar_storage=storage,
        ulid_generator=ULIDGeneratorFake(),
    )

    output = await use_case.execute(
        ReplaceUserAvatarInputDTO(
            user_id=user.id,
            content=BytesIO(b"source"),
            content_type="image/png",
            size_bytes=6,
        )
    )

    assert user.avatar_object_key == (
        f"users/{user.id.value}/avatar/01AVATAR000000000000000000.webp"
    )
    assert output.avatar_url.endswith(user.avatar_object_key)
    assert storage.deleted == [previous_key]
    assert uow.users_repository.updated == 1
    assert uow.commits == 1


@pytest.mark.asyncio
async def test_remove_avatar_clears_reference_and_deletes_object() -> None:
    key = "users/user-id/avatar/avatar.webp"
    user = UserBuilder().with_avatar_object_key(key).build()
    uow = UnitOfWorkFake(user)
    storage = StorageFake()

    output = await RemoveUserAvatarUseCase(uow, storage).execute(
        RemoveUserAvatarInputDTO(user_id=user.id)
    )

    assert user.avatar_object_key is None
    assert output.avatar_url is None
    assert storage.deleted == [key]
    assert uow.commits == 1


@pytest.mark.asyncio
async def test_get_profile_returns_fresh_signed_avatar_url() -> None:
    key = "users/user-id/avatar/avatar.webp"
    user = UserBuilder().with_avatar_object_key(key).build()

    output = await GetUserProfileUseCase(
        UnitOfWorkFake(user),
        StorageFake(),
    ).execute(user.id)

    assert output.avatar_url == f"https://signed.example.test/{key}"
