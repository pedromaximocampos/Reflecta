from src.modules.sharing.domain import ProfessionalActivityNotFound
from src.modules.sharing.domain.entities import ProfessionalActivity
from src.modules.sharing.domain.ports import ISharingUnitOfWork
from src.shared.domain.ports.system.iclock import IClock


class CompleteProfessionalActivity:
    def __init__(
        self,
        unit_of_work: ISharingUnitOfWork,
        clock: IClock,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._clock = clock

    async def execute(
        self,
        activity_id: str,
        user_id: str,
    ) -> ProfessionalActivity:
        async with self._unit_of_work as uow:
            activity = await uow.activity_repository.find_for_user_for_update(
                activity_id,
                user_id,
            )
            if activity is None:
                raise ProfessionalActivityNotFound()
            completed = activity.complete(self._clock.now())
            if completed is not activity:
                completed = await uow.activity_repository.save(completed)
                await uow.commit()
            return completed
