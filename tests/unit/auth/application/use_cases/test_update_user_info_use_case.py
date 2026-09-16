from datetime import date, datetime, timezone

import pytest

from src.modules.auth.application.use_cases.update_user_info.dto import UpdateUserInfoInput
from src.modules.auth.application.use_cases.update_user_info.update_user_info_use_case_impl import (
    UpdateUserInfoUseCaseImpl,
)
from src.modules.auth.domain.exceptions.user_custom_exceptions import UserNotFoundError
from src.modules.auth.public.user_id import UserId
from tests.support.builders.user_builder import UserBuilder
from tests.support.doubles.clock_fake import ClockFake


class UsersRepositoryFake:
    def __init__(self, user) -> None:
        self.user = user
        self.updated_user = None
        self.updated_fields = None

    async def find_by_id(self, user_id):
        if self.user is not None and self.user.id == user_id and not self.user.is_deleted:
            return self.user
        return None

    async def update_user_info(self, user, fields_to_update):
        self.updated_user = user
        self.updated_fields = fields_to_update


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

    async def rollback(self):
        return None


def make_use_case(uow) -> UpdateUserInfoUseCaseImpl:
    return UpdateUserInfoUseCaseImpl(
        auth_unit_of_work=uow,
        system_clock=ClockFake(
            now=datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
        ),
    )


@pytest.mark.asyncio
async def test_updates_a_subset_without_overwriting_other_user_fields() -> None:
    user = UserBuilder().build()
    original_surname = user.surname
    original_date_of_birth = user.date_of_birth
    uow = UnitOfWorkFake(user)

    output = await make_use_case(uow).execute(
        UpdateUserInfoInput(
            user_id=user.id,
            name="Maria",
            avatar_url="https://cdn.example.com/avatar.png",
        )
    )

    assert output.name == "Maria"
    assert output.avatar_url == "https://cdn.example.com/avatar.png"
    assert output.surname == original_surname
    assert output.date_of_birth == original_date_of_birth
    assert uow.users_repository.updated_user is user
    assert uow.users_repository.updated_fields == frozenset({"name", "avatar_url"})
    assert uow.commits == 1


@pytest.mark.asyncio
async def test_does_not_update_a_different_or_deleted_user() -> None:
    uow = UnitOfWorkFake(None)

    with pytest.raises(UserNotFoundError):
        await make_use_case(uow).execute(
            UpdateUserInfoInput(
                user_id=UserId("01MISSINGUSER0000000000000"),
                date_of_birth=date(2001, 1, 1),
            )
        )

    assert uow.users_repository.updated_user is None
    assert uow.users_repository.updated_fields is None
    assert uow.commits == 0
