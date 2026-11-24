from dataclasses import dataclass
from datetime import date

from src.modules.auth.public.notification_recipient import (
    IUserNotificationRecipientProvider,
    UserNotificationRecipientUnavailable,
)
from src.modules.internal_events.public import IOutboxService
from src.modules.journal.public.context_share import (
    IJournalSharingFacade,
    JournalShareSourceUnavailable,
)
from src.modules.sharing.domain import ActivityLimitReached, ShareUnavailable
from src.modules.sharing.domain.entities import ProfessionalActivity
from src.modules.sharing.domain.events import (
    ProfessionalActivitiesAssigned,
    ProfessionalActivityAssignedItem,
)
from src.modules.sharing.domain.ports import ISharingUnitOfWork
from src.modules.sharing.domain.value_objects import ActivityKind, ActivityStatus
from src.shared.domain.ports.system.iclock import IClock
from src.shared.domain.ports.system.iulid_generator import IULIDGenerator


MAX_ACTIVITIES_PER_SHARE = 20


@dataclass(frozen=True, slots=True)
class ProfessionalActivityInput:
    kind: ActivityKind
    title: str
    description: str
    due_date: date | None = None


@dataclass(frozen=True, slots=True)
class AssignProfessionalActivitiesCommand:
    token: str
    activities: tuple[ProfessionalActivityInput, ...]


class AssignProfessionalActivities:
    def __init__(
        self,
        unit_of_work: ISharingUnitOfWork,
        journal: IJournalSharingFacade,
        recipients: IUserNotificationRecipientProvider,
        outbox_service: IOutboxService,
        clock: IClock,
        ulid_generator: IULIDGenerator,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._journal = journal
        self._recipients = recipients
        self._outbox_service = outbox_service
        self._clock = clock
        self._ulid_generator = ulid_generator

    async def execute(
        self,
        command: AssignProfessionalActivitiesCommand,
    ) -> tuple[ProfessionalActivity, ...]:
        if not command.activities or len(command.activities) > MAX_ACTIVITIES_PER_SHARE:
            raise ActivityLimitReached()

        now = self._clock.now()
        async with self._unit_of_work as uow:
            access = await uow.activity_repository.find_active_access_for_update(
                command.token,
                now,
            )
            if access is None:
                raise ShareUnavailable()

            try:
                await self._journal.ensure_available(
                    access.analysis_id,
                    access.user_id,
                )
                recipient = await self._recipients.get_active_recipient(access.user_id)
            except (
                JournalShareSourceUnavailable,
                UserNotificationRecipientUnavailable,
            ) as error:
                raise ShareUnavailable() from error

            existing = await uow.activity_repository.count_for_share(access.id)
            if existing + len(command.activities) > MAX_ACTIVITIES_PER_SHARE:
                raise ActivityLimitReached()

            activities = tuple(
                ProfessionalActivity(
                    id=self._ulid_generator.generate_ulid(),
                    share_id=access.id,
                    user_id=access.user_id,
                    kind=item.kind,
                    title=item.title,
                    description=item.description,
                    due_date=item.due_date,
                    status=ActivityStatus.PENDING,
                    created_at=now,
                )
                for item in command.activities
            )
            created = await uow.activity_repository.add_many(activities)
            event = ProfessionalActivitiesAssigned(
                activities=tuple(
                    ProfessionalActivityAssignedItem(
                        activity_id=item.id,
                        kind=item.kind,
                        title=item.title,
                        description=item.description,
                        due_date=item.due_date,
                    )
                    for item in created
                ),
                user_email=recipient.email,
                username=recipient.username,
                occurred_at=now,
            )
            await self._outbox_service.persist_event(event, uow.outbox_repository)
            await uow.commit()
            return created
