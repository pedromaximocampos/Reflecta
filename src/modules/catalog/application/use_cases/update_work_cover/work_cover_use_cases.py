import logging

from src.modules.catalog.application.dto import WorkOutputDTO
from src.modules.catalog.application.ports.media import IWorkCoverProcessor
from src.modules.catalog.application.ports.storage import IWorkCoverStorage
from src.modules.catalog.application.use_cases.update_work_cover.dto import (
    RemoveWorkCoverInputDTO,
    ReplaceWorkCoverInputDTO,
)
from src.modules.catalog.application.use_cases.update_work_cover.iwork_cover_use_cases import (
    IRemoveWorkCoverUseCase,
    IReplaceWorkCoverUseCase,
)
from src.modules.catalog.domain.exceptions.work_exceptions import WorkNotFoundError
from src.modules.catalog.domain.ports.repositories.iwork_repository import (
    WorkCatalogRecord,
)
from src.modules.catalog.domain.ports.unit_of_work import ICatalogGraphUnitOfWork
from src.modules.catalog.public.work_id import WorkId
from src.shared.domain.ports.system.iclock import IClock
from src.shared.domain.ports.system.iulid_generator import IULIDGenerator


_LOGGER = logging.getLogger(__name__)


class ReplaceWorkCoverUseCase(IReplaceWorkCoverUseCase):
    def __init__(
        self,
        catalog_graph_uow: ICatalogGraphUnitOfWork,
        cover_processor: IWorkCoverProcessor,
        cover_storage: IWorkCoverStorage,
        ulid_generator: IULIDGenerator,
        clock: IClock,
    ) -> None:
        self.__catalog_graph_uow = catalog_graph_uow
        self.__cover_processor = cover_processor
        self.__cover_storage = cover_storage
        self.__ulid_generator = ulid_generator
        self.__clock = clock

    async def execute(
        self,
        work_input: ReplaceWorkCoverInputDTO,
    ) -> WorkOutputDTO:
        await self._ensure_work_exists(work_input.work_id)
        processed = await self.__cover_processor.process(
            content=work_input.content,
            declared_content_type=work_input.content_type,
            declared_size_bytes=work_input.size_bytes,
        )
        object_key = (
            f"works/{work_input.work_id.value}/cover/"
            f"{self.__ulid_generator.generate_ulid()}.{processed.extension}"
        )
        stored = await self.__cover_storage.upload(
            object_key=object_key,
            content=processed.content,
            content_type=processed.content_type,
            size_bytes=processed.size_bytes,
        )

        database_committed = False
        try:
            cover_url = await self.__cover_storage.create_read_url(
                object_key=stored.object_key
            )
            async with self.__catalog_graph_uow as uow:
                current = await uow.work_repository.get_work_with_author_by_id(
                    work_input.work_id
                )
                if current is None:
                    raise WorkNotFoundError(work_input.work_id.value)
                previous_object_key = current.work.cover_object_key
                current.work.replace_cover(stored.object_key, self.__clock.now())
                updated_work = await uow.work_repository.update_work(current.work)
                output = WorkOutputDTO.from_catalog_record(
                    self._with_updated_work(current, updated_work),
                    cover_image_url=cover_url,
                )
                await uow.commit()
                database_committed = True
        except Exception:
            if not database_committed:
                await self._delete_safely(stored.object_key, compensation=True)
            raise

        if previous_object_key and previous_object_key != stored.object_key:
            await self._delete_safely(previous_object_key)
        return output

    async def _ensure_work_exists(self, work_id: WorkId) -> None:
        async with self.__catalog_graph_uow as uow:
            if await uow.work_repository.get_work_by_id(work_id) is None:
                raise WorkNotFoundError(work_id.value)

    async def _delete_safely(
        self,
        object_key: str,
        *,
        compensation: bool = False,
    ) -> None:
        try:
            await self.__cover_storage.delete(object_key=object_key)
        except Exception:
            _LOGGER.exception(
                "Failed to delete work cover object: object_key=%s compensation=%s",
                object_key,
                compensation,
            )

    @staticmethod
    def _with_updated_work(
        current: WorkCatalogRecord,
        updated_work,
    ) -> WorkCatalogRecord:
        return WorkCatalogRecord(
            work=updated_work,
            author=current.author,
            passage_count=current.passage_count,
            active_passage_count=current.active_passage_count,
            inactive_passage_count=current.inactive_passage_count,
        )


class RemoveWorkCoverUseCase(IRemoveWorkCoverUseCase):
    def __init__(
        self,
        catalog_graph_uow: ICatalogGraphUnitOfWork,
        cover_storage: IWorkCoverStorage,
        clock: IClock,
    ) -> None:
        self.__catalog_graph_uow = catalog_graph_uow
        self.__cover_storage = cover_storage
        self.__clock = clock

    async def execute(
        self,
        work_input: RemoveWorkCoverInputDTO,
    ) -> WorkOutputDTO:
        async with self.__catalog_graph_uow as uow:
            current = await uow.work_repository.get_work_with_author_by_id(
                work_input.work_id
            )
            if current is None:
                raise WorkNotFoundError(work_input.work_id.value)
            previous_object_key = current.work.cover_object_key
            current.work.remove_cover(self.__clock.now())
            updated_work = await uow.work_repository.update_work(current.work)
            output = WorkOutputDTO.from_catalog_record(
                ReplaceWorkCoverUseCase._with_updated_work(current, updated_work)
            )
            await uow.commit()

        if previous_object_key:
            try:
                await self.__cover_storage.delete(object_key=previous_object_key)
            except Exception:
                _LOGGER.exception(
                    "Failed to delete removed work cover object: object_key=%s",
                    previous_object_key,
                )
        return output
