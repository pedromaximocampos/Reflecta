from src.modules.catalog.application.use_cases.manage_passages import (
    CreatePassageInputDTO,
    ICreatePassageUseCase,
    IDeletePassageUseCase,
    IGetPassageUseCase,
    IListPassagesUseCase,
    IReviewPassageUseCase,
    ISetPassageAvailabilityUseCase,
    IUpdatePassageUseCase,
    ListPassagesInputDTO,
    PassageThemeInputDTO,
    UpdatePassageInputDTO,
)
from src.modules.catalog.domain.value_objects import CatalogStatus
from src.modules.catalog.public.passage_id import PassageId
from src.modules.catalog.public.theme_id import ThemeId
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class CreatePassageController(IControllerInterface):
    def __init__(self, use_case: ICreatePassageUseCase) -> None:
        self._use_case = use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        body = dict(request.body or {})
        result = await self._use_case.execute(
            CreatePassageInputDTO(
                work_id=WorkId(body["work_id"]),
                locator=body["locator"],
                short_text=body["short_text"],
                paraphrase=body["paraphrase"],
                interpretation_note=body["interpretation_note"],
                priority=body.get("priority", 0),
                themes=_theme_inputs(body["themes"]),
                start_page=body.get("start_page"),
                end_page=body.get("end_page"),
            )
        )
        return HttpResponse(status_code=201, body=result.to_dict())


class GetPassageController(IControllerInterface):
    def __init__(self, use_case: IGetPassageUseCase) -> None:
        self._use_case = use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        result = await self._use_case.execute(_passage_id(request))
        return HttpResponse(status_code=200, body=result.to_dict())


class ListPassagesController(IControllerInterface):
    def __init__(self, use_case: IListPassagesUseCase) -> None:
        self._use_case = use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        status = request.query_params.get("status")
        work_id = request.query_params.get("work_id")
        ingestion_id = request.query_params.get("ingestion_id")
        result = await self._use_case.execute(
            ListPassagesInputDTO(
                status=CatalogStatus(status) if status else None,
                work_id=WorkId(work_id) if work_id else None,
                ingestion_id=(
                    WorkIngestionId(ingestion_id) if ingestion_id else None
                ),
            )
        )
        return HttpResponse(status_code=200, body=result.to_dict())


class UpdatePassageController(IControllerInterface):
    def __init__(self, use_case: IUpdatePassageUseCase) -> None:
        self._use_case = use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        body = dict(request.body or {})
        result = await self._use_case.execute(
            UpdatePassageInputDTO(
                passage_id=_passage_id(request),
                locator=body.get("locator"),
                short_text=body.get("short_text"),
                paraphrase=body.get("paraphrase"),
                interpretation_note=body.get("interpretation_note"),
                priority=body.get("priority"),
                themes=(
                    _theme_inputs(body["themes"])
                    if "themes" in body
                    else None
                ),
                start_page=body.get("start_page"),
                end_page=body.get("end_page"),
                update_page_range="start_page" in body,
            )
        )
        return HttpResponse(status_code=200, body=result.to_dict())


class ReviewPassageController(IControllerInterface):
    def __init__(self, use_case: IReviewPassageUseCase, *, approve: bool) -> None:
        self._use_case = use_case
        self._approve = approve

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        result = await self._use_case.execute(
            _passage_id(request),
            approve=self._approve,
        )
        return HttpResponse(status_code=200, body=result.to_dict())


class SetPassageAvailabilityController(IControllerInterface):
    def __init__(
        self,
        use_case: ISetPassageAvailabilityUseCase,
        *,
        active: bool,
    ) -> None:
        self._use_case = use_case
        self._active = active

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        result = await self._use_case.execute(
            _passage_id(request),
            active=self._active,
        )
        return HttpResponse(status_code=200, body=result.to_dict())


class DeletePassageController(IControllerInterface):
    def __init__(self, use_case: IDeletePassageUseCase) -> None:
        self._use_case = use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        await self._use_case.execute(_passage_id(request))
        return HttpResponse(status_code=204)


def _passage_id(request: HttpRequest) -> PassageId:
    return PassageId(str(request.path_params["passage_id"]))


def _theme_inputs(items: list[dict]) -> tuple[PassageThemeInputDTO, ...]:
    return tuple(
        PassageThemeInputDTO(
            theme_id=ThemeId(item["theme_id"]),
            confidence=item["confidence"],
        )
        for item in items
    )
