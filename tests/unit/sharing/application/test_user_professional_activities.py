from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.modules.sharing.application import (
    CompleteProfessionalActivity,
    ListProfessionalActivities,
    ListProfessionalActivitiesQuery,
)
from src.modules.sharing.domain import ProfessionalActivityNotFound
from src.modules.sharing.domain.entities import ProfessionalActivity
from src.modules.sharing.domain.value_objects import ActivityKind, ActivityStatus


NOW = datetime(2026, 11, 9, 18, tzinfo=timezone.utc)


def activity(status: ActivityStatus = ActivityStatus.PENDING):
    return ProfessionalActivity(
        id="activity-id",
        share_id="share-id",
        user_id="user-id",
        kind=ActivityKind.GUIDED_REFLECTION,
        title="Observar escolhas",
        description="Escreva sobre uma escolha possível.",
        status=status,
        created_at=NOW,
        completed_at=NOW if status is ActivityStatus.COMPLETED else None,
    )


class FakeUnitOfWork:
    def __init__(self, repository) -> None:
        self.activity_repository = repository
        self.commit = AsyncMock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None


@pytest.mark.asyncio
async def test_lists_only_the_authenticated_users_activities():
    expected = (activity(),)
    repository = SimpleNamespace(
        list_for_user=AsyncMock(return_value=expected),
        count_for_user=AsyncMock(return_value=1),
    )
    use_case = ListProfessionalActivities(FakeUnitOfWork(repository))
    query = ListProfessionalActivitiesQuery(
        user_id="user-id",
        status=ActivityStatus.PENDING,
        limit=8,
        offset=0,
    )

    page = await use_case.execute(query)

    assert page.activities == expected
    assert page.total == 1
    repository.list_for_user.assert_awaited_once_with(
        "user-id",
        ActivityStatus.PENDING,
        8,
        0,
    )
    repository.count_for_user.assert_awaited_once_with(
        "user-id",
        ActivityStatus.PENDING,
    )


@pytest.mark.asyncio
async def test_completes_pending_activity_and_commits_once():
    pending = activity()
    repository = SimpleNamespace(
        find_for_user_for_update=AsyncMock(return_value=pending),
        save=AsyncMock(side_effect=lambda value: value),
    )
    uow = FakeUnitOfWork(repository)
    use_case = CompleteProfessionalActivity(
        uow,
        SimpleNamespace(now=lambda: NOW),
    )

    completed = await use_case.execute("activity-id", "user-id")

    assert completed.status is ActivityStatus.COMPLETED
    assert completed.completed_at == NOW
    repository.find_for_user_for_update.assert_awaited_once_with(
        "activity-id",
        "user-id",
    )
    repository.save.assert_awaited_once_with(completed)
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_completion_is_idempotent_and_owner_scoped():
    completed = activity(ActivityStatus.COMPLETED)
    repository = SimpleNamespace(
        find_for_user_for_update=AsyncMock(return_value=completed),
        save=AsyncMock(),
    )
    uow = FakeUnitOfWork(repository)
    use_case = CompleteProfessionalActivity(
        uow,
        SimpleNamespace(now=lambda: NOW),
    )

    assert await use_case.execute("activity-id", "user-id") is completed
    repository.save.assert_not_awaited()
    uow.commit.assert_not_awaited()

    repository.find_for_user_for_update.return_value = None
    with pytest.raises(ProfessionalActivityNotFound):
        await use_case.execute("activity-id", "other-user")
