from src.modules.catalog.application.dto import WorkOutputDTO
from src.modules.catalog.application.ports.storage import IWorkCoverStorage
from src.modules.catalog.application.use_cases.get_works.iget_work_by_id_use_case import (
    IGetWorkByIdUseCase,
)
from src.modules.catalog.domain.exceptions.work_exceptions import WorkNotFoundError
from src.modules.catalog.domain.ports.unit_of_work import ICatalogGraphUnitOfWork
from src.modules.catalog.public.work_id import WorkId


class GetWorkByIdUseCase(IGetWorkByIdUseCase):
    def __init__(
        self,
        catalog_graph_uow: ICatalogGraphUnitOfWork,
        cover_storage: IWorkCoverStorage,
    ) -> None:
        self.__catalog_graph_uow = catalog_graph_uow
        self.__cover_storage = cover_storage

    async def execute(self, work_id: WorkId) -> WorkOutputDTO:
        async with self.__catalog_graph_uow as uow:
            result = await uow.work_repository.get_work_with_author_by_id(work_id)
            if result is None:
                raise WorkNotFoundError(work_id.value)
            cover_url = result.work.cover_image_url
            if result.work.cover_object_key:
                cover_url = await self.__cover_storage.create_read_url(
                    object_key=result.work.cover_object_key
                )
            return WorkOutputDTO.from_catalog_record(
                result,
                cover_image_url=cover_url,
            )
