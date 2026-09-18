from src.modules.catalog.application.use_cases.create_themes.dto import (
    CreateThemesInputDTO,
    CreateThemesOutputDTO,
)
from src.modules.catalog.application.use_cases.create_themes.icreate_themes_use_case import (
    ICreateThemesUseCase,
)
from src.modules.catalog.domain.entities.theme import Theme
from src.modules.catalog.domain.exceptions.theme_exceptions import (
    EmptyThemeBatchError,
    InvalidThemeSlugError,
    ThemeAlreadyExistsError,
)
from src.modules.catalog.domain.ports.unit_of_work.icatalog_graph_unit_of_work import (
    ICatalogGraphUnitOfWork,
)
from src.modules.catalog.public.theme_id import ThemeId
from src.shared.domain.ports.system.iclock import IClock
from src.shared.domain.ports.system.islug_generator import ISlugGenerator
from src.shared.domain.ports.system.iulid_generator import IULIDGenerator


class CreateThemesUseCase(ICreateThemesUseCase):
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

    async def execute(
        self,
        themes_input: CreateThemesInputDTO,
    ) -> CreateThemesOutputDTO:
        themes = self._create_theme_entities(themes_input)

        async with self.__catalog_graph_uow as uow:
            await self._ensure_slugs_are_available(themes, uow)
            created_themes = await uow.theme_repository.create_many_themes(themes)
            output = CreateThemesOutputDTO.from_entities(created_themes)
            await uow.commit()

        return output

    def _create_theme_entities(
        self,
        themes_input: CreateThemesInputDTO,
    ) -> list[Theme]:
        if not themes_input.themes:
            raise EmptyThemeBatchError()

        created_at = self.__clock.now()
        themes: list[Theme] = []
        slugs: set[str] = set()

        for theme_data in themes_input.themes:
            slug = self._create_slug_for_theme(theme_data.label)
            if slug in slugs:
                raise ThemeAlreadyExistsError(slug)

            slugs.add(slug)
            themes.append(
                Theme(
                    id=ThemeId(self.__ulid_generator.generate_ulid()),
                    label=theme_data.label,
                    description=theme_data.description,
                    is_active=theme_data.is_active,
                    created_at=created_at,
                    slug=slug,
                )
            )

        return themes

    @staticmethod
    async def _ensure_slugs_are_available(
        themes: list[Theme],
        uow: ICatalogGraphUnitOfWork,
    ) -> None:
        for theme in themes:
            if await uow.theme_repository.get_theme_by_slug(theme.slug) is not None:
                raise ThemeAlreadyExistsError(theme.slug)

    def _create_slug_for_theme(self, label: str) -> str:
        slug = self.__slug_generator.generate_slug(label)
        if not slug:
            raise InvalidThemeSlugError()

        return slug
