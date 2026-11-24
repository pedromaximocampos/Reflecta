from functools import lru_cache

from src.modules.auth.public.notification_provider import (
    get_user_notification_recipient_provider,
)
from src.modules.internal_events.bootstrap.services import get_outbox_service
from src.modules.journal.public.sharing_provider import get_journal_sharing_facade
from src.modules.sharing.application import (
    AssignProfessionalActivities,
    CompleteProfessionalActivity,
    ListProfessionalActivities,
)
from src.modules.sharing.infrastructure.persistence.postgresql.share_gateway import (
    ContextShareGateway,
)
from src.modules.sharing.infrastructure.persistence.postgresql.unit_of_work import (
    SharingUnitOfWork,
)
from src.shared.config.settings import get_settings
from src.shared.infrastructure.system.providers import get_clock, get_ulid_generator
from src.shared.infrastructure.persistence.postgresql.provider import (
    individuum_mvp_provider,
)


@lru_cache
def get_share_gateway() -> ContextShareGateway:
    return ContextShareGateway(
        individuum_mvp_provider,
        journal=get_journal_sharing_facade(),
        token_secret=get_settings().JWT_SECRET,
    )


def get_assign_professional_activities() -> AssignProfessionalActivities:
    clock = get_clock()
    return AssignProfessionalActivities(
        unit_of_work=SharingUnitOfWork(individuum_mvp_provider, clock),
        journal=get_journal_sharing_facade(),
        recipients=get_user_notification_recipient_provider(),
        outbox_service=get_outbox_service(),
        clock=clock,
        ulid_generator=get_ulid_generator(),
    )


def get_list_professional_activities() -> ListProfessionalActivities:
    return ListProfessionalActivities(
        unit_of_work=SharingUnitOfWork(individuum_mvp_provider, get_clock()),
    )


def get_complete_professional_activity() -> CompleteProfessionalActivity:
    clock = get_clock()
    return CompleteProfessionalActivity(
        unit_of_work=SharingUnitOfWork(individuum_mvp_provider, clock),
        clock=clock,
    )
