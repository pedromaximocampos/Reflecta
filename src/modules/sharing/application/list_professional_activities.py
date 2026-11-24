from dataclasses import dataclass

from src.modules.sharing.domain.entities import ProfessionalActivity
from src.modules.sharing.domain.ports import ISharingUnitOfWork
from src.modules.sharing.domain.value_objects import ActivityStatus


@dataclass(frozen=True, slots=True)
class ListProfessionalActivitiesQuery:
    user_id: str
    status: ActivityStatus | None
    limit: int
    offset: int


@dataclass(frozen=True, slots=True)
class ProfessionalActivityPage:
    activities: tuple[ProfessionalActivity, ...]
    total: int
    limit: int
    offset: int


class ListProfessionalActivities:
    def __init__(self, unit_of_work: ISharingUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(
        self,
        query: ListProfessionalActivitiesQuery,
    ) -> ProfessionalActivityPage:
        async with self._unit_of_work as uow:
            activities = await uow.activity_repository.list_for_user(
                query.user_id,
                query.status,
                query.limit,
                query.offset,
            )
            total = await uow.activity_repository.count_for_user(
                query.user_id,
                query.status,
            )
        return ProfessionalActivityPage(
            activities=activities,
            total=total,
            limit=query.limit,
            offset=query.offset,
        )
