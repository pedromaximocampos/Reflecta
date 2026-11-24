from datetime import date, datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.modules.auth.public.notification_recipient import UserNotificationRecipient
from src.modules.sharing.application.assign_professional_activities import (
    MAX_ACTIVITIES_PER_SHARE,
    AssignProfessionalActivities,
    AssignProfessionalActivitiesCommand,
    ProfessionalActivityInput,
)
from src.modules.sharing.domain import ActivityLimitReached, ShareUnavailable
from src.modules.sharing.domain.entities import ShareAccess
from src.modules.sharing.domain.value_objects import ActivityKind, ActivityStatus


NOW = datetime(2026, 11, 9, 15, tzinfo=timezone.utc)


class FakeUnitOfWork:
    def __init__(self, repository) -> None:
        self.activity_repository = repository
        self.outbox_repository = object()
        self.commit = AsyncMock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None


def setup_use_case(*, access=True, count=0):
    resolved_access = ShareAccess(
        id="share-id",
        user_id="user-id",
        analysis_id="analysis-id",
        expires_at=NOW,
    ) if access else None
    repository = SimpleNamespace(
        find_active_access_for_update=AsyncMock(return_value=resolved_access),
        count_for_share=AsyncMock(return_value=count),
        add_many=AsyncMock(side_effect=lambda activities: activities),
    )
    uow = FakeUnitOfWork(repository)
    journal = SimpleNamespace(ensure_available=AsyncMock())
    recipients = SimpleNamespace(get_active_recipient=AsyncMock(return_value=
        UserNotificationRecipient("user-id", "Pedro", "pedro@example.com")
    ))
    outbox = SimpleNamespace(persist_event=AsyncMock())
    identifiers = iter(["activity-id-1", "activity-id-2"])
    use_case = AssignProfessionalActivities(
        unit_of_work=uow,
        journal=journal,
        recipients=recipients,
        outbox_service=outbox,
        clock=SimpleNamespace(now=lambda: NOW),
        ulid_generator=SimpleNamespace(generate_ulid=lambda: next(identifiers)),
    )
    command = AssignProfessionalActivitiesCommand(
        token="a" * 43,
        activities=(
            ProfessionalActivityInput(
                kind=ActivityKind.ACTIVITY,
                title="Observar escolhas",
                description="Observe uma escolha durante a semana.",
            ),
            ProfessionalActivityInput(
                kind=ActivityKind.GUIDED_REFLECTION,
                title="Refletir sobre escolhas",
                description="Escreva sobre uma escolha possível.",
                due_date=date(2026, 11, 15),
            ),
        ),
    )
    return use_case, command, uow, repository, journal, recipients, outbox


@pytest.mark.asyncio
async def test_assigns_activity_and_email_event_in_same_unit_of_work():
    use_case, command, uow, repository, journal, recipients, outbox = setup_use_case()

    activities = await use_case.execute(command)

    assert [activity.id for activity in activities] == [
        "activity-id-1",
        "activity-id-2",
    ]
    assert activities[1].kind is ActivityKind.GUIDED_REFLECTION
    assert all(activity.status is ActivityStatus.PENDING for activity in activities)
    repository.add_many.assert_awaited_once_with(activities)
    journal.ensure_available.assert_awaited_once_with("analysis-id", "user-id")
    recipients.get_active_recipient.assert_awaited_once_with("user-id")
    event, outbox_repository = outbox.persist_event.await_args.args
    assert event.__event_type__ == "emails.professional_activities.assigned"
    assert len(event.to_payload()["activities"]) == 2
    assert event.to_payload()["activities"][1]["description"] == (
        command.activities[1].description
    )
    assert outbox_repository is uow.outbox_repository
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_rejects_expired_or_revoked_access_without_side_effects():
    use_case, command, uow, repository, journal, recipients, outbox = setup_use_case(access=False)

    with pytest.raises(ShareUnavailable):
        await use_case.execute(command)

    repository.add_many.assert_not_awaited()
    journal.ensure_available.assert_not_awaited()
    recipients.get_active_recipient.assert_not_awaited()
    outbox.persist_event.assert_not_awaited()
    uow.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_limits_guidance_created_from_the_same_shared_access():
    use_case, command, uow, repository, _, _, outbox = setup_use_case(
        count=MAX_ACTIVITIES_PER_SHARE - 1,
    )

    with pytest.raises(ActivityLimitReached):
        await use_case.execute(command)

    repository.add_many.assert_not_awaited()
    outbox.persist_event.assert_not_awaited()
    uow.commit.assert_not_awaited()

