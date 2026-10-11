import hashlib

from src.modules.catalog.application.dto import PassageOutputDTO, PassagesOutputDTO
from src.modules.catalog.domain.entities.passage import Passage, PassageThemeRelevance
from src.modules.catalog.domain.exceptions import (
    EmptyPassageUpdateError,
    InactivePassageThemeError,
    InvalidPassageThemesError,
    PassageNotFoundError,
    ThemeNotFoundError,
)
from src.modules.catalog.domain.exceptions.work_exceptions import WorkNotFoundError
from src.modules.catalog.domain.ports.unit_of_work import (
    ICatalogGraphUnitOfWork,
    ICatalogSQLUnitOfWork,
)
from src.modules.catalog.domain.value_objects import CatalogStatus, WorkIngestionStatus
from src.modules.catalog.public.passage_id import PassageId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId
from src.shared.domain.ports.system.iclock import IClock
from src.shared.domain.ports.system.iulid_generator import IULIDGenerator

from .dto import (
    CreatePassageInputDTO,
    ListPassagesInputDTO,
    PassageThemeInputDTO,
    UpdatePassageInputDTO,
)


class CreatePassageUseCase:
    def __init__(
        self,
        graph_uow: ICatalogGraphUnitOfWork,
        ids: IULIDGenerator,
        clock: IClock,
    ) -> None:
        self._graph_uow = graph_uow
        self._ids = ids
        self._clock = clock

    async def execute(self, data: CreatePassageInputDTO) -> PassageOutputDTO:
        passage_id = PassageId(self._ids.generate_ulid())
        async with self._graph_uow as uow:
            if await uow.work_repository.get_work_by_id(data.work_id) is None:
                raise WorkNotFoundError(data.work_id.value)
            themes = await _validated_themes(uow, data.themes)
            passage = Passage(
                id=passage_id,
                work_id=data.work_id,
                source_key=hashlib.sha256(
                    f"admin|{passage_id.value}".encode("utf-8")
                ).hexdigest(),
                source="admin",
                locator=data.locator,
                short_text=data.short_text,
                paraphrase=data.paraphrase,
                interpretation_note=data.interpretation_note,
                status=CatalogStatus.APPROVED,
                priority=data.priority,
                themes=themes,
                start_page=data.start_page,
                end_page=data.end_page,
                created_at=self._clock.now(),
            )
            created = await uow.passage_repository.create(passage)
            output = await _passage_output(uow, created)
            await uow.commit()
        return output


class GetPassageUseCase:
    def __init__(self, graph_uow: ICatalogGraphUnitOfWork) -> None:
        self._graph_uow = graph_uow

    async def execute(self, passage_id: PassageId) -> PassageOutputDTO:
        async with self._graph_uow as uow:
            passage = await uow.passage_repository.get_by_id(passage_id)
            if passage is None:
                raise PassageNotFoundError(passage_id.value)
            return await _passage_output(uow, passage)


class ListPassagesUseCase:
    def __init__(self, graph_uow: ICatalogGraphUnitOfWork) -> None:
        self._graph_uow = graph_uow

    async def execute(self, filters: ListPassagesInputDTO) -> PassagesOutputDTO:
        async with self._graph_uow as uow:
            passages = await uow.passage_repository.list_passages(
                status=filters.status,
                work_id=filters.work_id,
                ingestion_id=filters.ingestion_id,
            )
            return await _passages_output(uow, passages)


class UpdatePassageUseCase:
    def __init__(self, graph_uow: ICatalogGraphUnitOfWork, clock: IClock) -> None:
        self._graph_uow = graph_uow
        self._clock = clock

    async def execute(self, data: UpdatePassageInputDTO) -> PassageOutputDTO:
        if data.is_empty():
            raise EmptyPassageUpdateError()
        async with self._graph_uow as uow:
            passage = await uow.passage_repository.get_by_id(data.passage_id)
            if passage is None:
                raise PassageNotFoundError(data.passage_id.value)
            themes = (
                await _validated_themes(uow, data.themes)
                if data.themes is not None
                else None
            )
            passage.update(
                now=self._clock.now(),
                locator=data.locator,
                short_text=data.short_text,
                paraphrase=data.paraphrase,
                interpretation_note=data.interpretation_note,
                priority=data.priority,
                themes=themes,
                start_page=data.start_page,
                end_page=data.end_page,
                update_page_range=data.update_page_range,
            )
            updated = await uow.passage_repository.update(passage)
            output = await _passage_output(uow, updated)
            await uow.commit()
        return output


class ReviewPassageUseCase:
    def __init__(
        self,
        graph_uow: ICatalogGraphUnitOfWork,
        sql_uow: ICatalogSQLUnitOfWork,
        clock: IClock,
    ) -> None:
        self._graph_uow = graph_uow
        self._sql_uow = sql_uow
        self._clock = clock

    async def execute(
        self,
        passage_id: PassageId,
        *,
        approve: bool,
    ) -> PassageOutputDTO:
        ingestion_id = None
        pending = 0
        async with self._graph_uow as uow:
            passage = await uow.passage_repository.get_by_id(passage_id)
            if passage is None:
                raise PassageNotFoundError(passage_id.value)
            if approve:
                await _ensure_active_passage_themes(uow, passage)
                passage.approve(now=self._clock.now())
            else:
                passage.reject(now=self._clock.now())
            updated = await uow.passage_repository.update(passage)
            ingestion_id = updated.ingestion_id
            if ingestion_id is not None:
                pending = await uow.passage_repository.count_pending_by_ingestion(
                    ingestion_id
                )
            output = await _passage_output(uow, updated)
            await uow.commit()
        if ingestion_id is not None and pending == 0:
            await _complete_ingestion(
                self._sql_uow,
                ingestion_id,
                self._clock,
            )
        return output


class SetPassageAvailabilityUseCase:
    def __init__(self, graph_uow: ICatalogGraphUnitOfWork, clock: IClock) -> None:
        self._graph_uow = graph_uow
        self._clock = clock

    async def execute(
        self,
        passage_id: PassageId,
        *,
        active: bool,
    ) -> PassageOutputDTO:
        async with self._graph_uow as uow:
            passage = await uow.passage_repository.get_by_id(passage_id)
            if passage is None:
                raise PassageNotFoundError(passage_id.value)
            if active:
                await _ensure_active_passage_themes(uow, passage)
                passage.activate(now=self._clock.now())
            else:
                passage.deactivate(now=self._clock.now())
            updated = await uow.passage_repository.update(passage)
            output = await _passage_output(uow, updated)
            await uow.commit()
        return output


class DeletePassageUseCase:
    def __init__(
        self,
        graph_uow: ICatalogGraphUnitOfWork,
        sql_uow: ICatalogSQLUnitOfWork,
        clock: IClock,
    ) -> None:
        self._graph_uow = graph_uow
        self._sql_uow = sql_uow
        self._clock = clock

    async def execute(self, passage_id: PassageId) -> None:
        ingestion_id = None
        pending = 0
        async with self._graph_uow as uow:
            passage = await uow.passage_repository.get_by_id(passage_id)
            if passage is None:
                raise PassageNotFoundError(passage_id.value)
            passage.retire(now=self._clock.now())
            updated = await uow.passage_repository.update(passage)
            ingestion_id = updated.ingestion_id
            if ingestion_id is not None:
                pending = await uow.passage_repository.count_pending_by_ingestion(
                    ingestion_id
                )
            await uow.commit()
        if ingestion_id is not None and pending == 0:
            await _complete_ingestion(
                self._sql_uow,
                ingestion_id,
                self._clock,
            )


async def _validated_themes(
    uow: ICatalogGraphUnitOfWork,
    themes: tuple[PassageThemeInputDTO, ...],
) -> tuple[PassageThemeRelevance, ...]:
    theme_ids = tuple(item.theme_id.value for item in themes)
    if not theme_ids or len(theme_ids) != len(set(theme_ids)):
        raise InvalidPassageThemesError()
    validated: list[PassageThemeRelevance] = []
    for item in themes:
        theme = await uow.theme_repository.get_theme_by_id(item.theme_id)
        if theme is None:
            raise ThemeNotFoundError(item.theme_id.value)
        if not theme.is_active:
            raise InactivePassageThemeError(item.theme_id.value)
        validated.append(PassageThemeRelevance(item.theme_id, item.confidence))
    return tuple(validated)


async def _passage_output(
    uow: ICatalogGraphUnitOfWork,
    passage: Passage,
) -> PassageOutputDTO:
    labels = await _theme_labels(uow)
    return PassageOutputDTO.from_entity(passage, labels)


async def _passages_output(
    uow: ICatalogGraphUnitOfWork,
    passages: list[Passage],
) -> PassagesOutputDTO:
    labels = await _theme_labels(uow)
    return PassagesOutputDTO.from_entities(passages, labels)


async def _theme_labels(uow: ICatalogGraphUnitOfWork) -> dict[str, str]:
    themes = await uow.theme_repository.list_themes()
    return {theme.id.value: theme.label for theme in themes}


async def _ensure_active_passage_themes(
    uow: ICatalogGraphUnitOfWork,
    passage: Passage,
) -> None:
    await _validated_themes(
        uow,
        tuple(
            PassageThemeInputDTO(theme.theme_id, theme.confidence)
            for theme in passage.themes
        ),
    )


async def _complete_ingestion(
    sql_uow: ICatalogSQLUnitOfWork,
    ingestion_id: WorkIngestionId,
    clock: IClock,
) -> None:
    async with sql_uow as uow:
        ingestion = await uow.work_ingestion_repository.find_by_id(ingestion_id)
        if ingestion is None:
            raise LookupError(
                f"Work ingestion '{ingestion_id.value}' was not found."
            )
        if ingestion.status is WorkIngestionStatus.COMPLETED:
            return
        ingestion.mark_completed(now=clock.now())
        await uow.work_ingestion_repository.update(ingestion)
        await uow.commit()
