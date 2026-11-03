import asyncio

from src.modules.catalog.application.dto import WorkOutputDTO, WorksOutputDTO
from src.modules.catalog.application.ports.storage import IWorkCoverStorage
from src.modules.catalog.application.use_cases.get_works.iget_all_works_use_case import (
    IGetAllWorksUseCase,
)
from src.modules.catalog.domain.ports.unit_of_work import ICatalogGraphUnitOfWork


class GetAllWorksUseCase(IGetAllWorksUseCase):
    def __init__(
        self,
        catalog_graph_uow: ICatalogGraphUnitOfWork,
        cover_storage: IWorkCoverStorage,
    ) -> None:
        self.__catalog_graph_uow = catalog_graph_uow
        self.__cover_storage = cover_storage

    async def execute(self) -> WorksOutputDTO:
        async with self.__catalog_graph_uow as uow:
            works_with_authors = await uow.work_repository.list_works()
        cover_urls = await asyncio.gather(
            *(self._resolve_cover_url(record.work) for record in works_with_authors)
        )
        return WorksOutputDTO(
            tuple(
                WorkOutputDTO.from_catalog_record(
                    record,
                    cover_image_url=cover_url,
                )
                for record, cover_url in zip(
                    works_with_authors,
                    cover_urls,
                    strict=True,
                )
            )
        )

    async def _resolve_cover_url(self, work) -> str | None:
        if work.cover_object_key:
            return await self.__cover_storage.create_read_url(
                object_key=work.cover_object_key
            )
        return work.cover_image_url
