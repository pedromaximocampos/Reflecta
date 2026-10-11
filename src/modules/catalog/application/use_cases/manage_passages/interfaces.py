from typing import Protocol

from src.modules.catalog.application.dto import PassageOutputDTO, PassagesOutputDTO
from src.modules.catalog.public.passage_id import PassageId

from .dto import (
    CreatePassageInputDTO,
    ListPassagesInputDTO,
    UpdatePassageInputDTO,
)


class ICreatePassageUseCase(Protocol):
    async def execute(self, data: CreatePassageInputDTO) -> PassageOutputDTO: ...


class IGetPassageUseCase(Protocol):
    async def execute(self, passage_id: PassageId) -> PassageOutputDTO: ...


class IListPassagesUseCase(Protocol):
    async def execute(self, filters: ListPassagesInputDTO) -> PassagesOutputDTO: ...


class IUpdatePassageUseCase(Protocol):
    async def execute(self, data: UpdatePassageInputDTO) -> PassageOutputDTO: ...


class IReviewPassageUseCase(Protocol):
    async def execute(
        self,
        passage_id: PassageId,
        *,
        approve: bool,
    ) -> PassageOutputDTO: ...


class ISetPassageAvailabilityUseCase(Protocol):
    async def execute(
        self,
        passage_id: PassageId,
        *,
        active: bool,
    ) -> PassageOutputDTO: ...


class IDeletePassageUseCase(Protocol):
    async def execute(self, passage_id: PassageId) -> None: ...
