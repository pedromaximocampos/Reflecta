from src.modules.catalog.application.use_cases.create_work.dto import (
    CreateWorkInputDTO,
    CreateWorkOutputDTO,
)
from src.modules.catalog.domain.entities.author import Author
from src.modules.catalog.domain.entities.work import Work
from src.modules.catalog.domain.exceptions.work_exceptions import (
    InvalidAuthorNameError,
    InvalidWorkSlugError,
    WorkAlreadyExistsError,
)
from src.modules.catalog.domain.ports.unit_of_work.icatalog_graph_unit_of_work import (
    ICatalogGraphUnitOfWork,
)
from src.modules.catalog.domain.value_objects.catalog_status import CatalogStatus
from src.modules.catalog.public.author_id import AuthorId
from src.modules.catalog.public.work_id import WorkId
from src.shared.domain.ports.system.iclock import IClock
from src.shared.domain.ports.system.islug_generator import ISlugGenerator
from src.shared.domain.ports.system.iulid_generator import IULIDGenerator


class CreateWorkUseCase:
    def __init__(
        self,
        catalog_graph_uow: ICatalogGraphUnitOfWork,
        ulid_generator: IULIDGenerator,
        clock: IClock,
        slug_generator: ISlugGenerator,
    ) -> None:
        self.__catalog_graph_uow = catalog_graph_uow
        self.__ulid_generator = ulid_generator
        self.__clock = clock
        self.__slug_generator = slug_generator

    async def execute(self, work_input: CreateWorkInputDTO) -> CreateWorkOutputDTO:
        work, author = self._create_entities(work_input)
        async with self.__catalog_graph_uow as uow:
            if await uow.work_repository.get_work_by_slug(work.slug) is not None:
                raise WorkAlreadyExistsError(work.slug)
            created_work, stored_author = await uow.work_repository.create_work(work, author)
            output = CreateWorkOutputDTO.from_entities(created_work, stored_author)
            await uow.commit()
        return output

    def _create_entities(self, work_input: CreateWorkInputDTO) -> tuple[Work, Author]:
        work_slug = self.__slug_generator.generate_slug(work_input.title)
        if not work_slug:
            raise InvalidWorkSlugError()
        normalized_author_name = self.__slug_generator.generate_slug(work_input.author.name)
        if not normalized_author_name:
            raise InvalidAuthorNameError()
        created_at = self.__clock.now()
        author = Author(
            id=AuthorId(self.__ulid_generator.generate_ulid()),
            name=work_input.author.name,
            normalized_name=normalized_author_name,
            description=work_input.author.description,
            created_at=created_at,
        )
        work = Work(
            id=WorkId(self.__ulid_generator.generate_ulid()),
            slug=work_slug,
            title=work_input.title,
            synopsis=work_input.synopsis,
            work_type=work_input.work_type,
            language=work_input.language,
            status=CatalogStatus.INACTIVE,
            created_at=created_at,
        )
        return work, author
