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
from src.modules.catalog.domain.ports.system.itheme_color_generator import (
    IThemeColorGenerator,
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
        color_generator: IThemeColorGenerator,
    ) -> None:
        self.__catalog_graph_uow = catalog_graph_uow
        self.__ulid_generator = ulid_generator
        self.__clock = clock
        self.__slug_generator = slug_generator
        self.__color_generator = color_generator

    async def execute(
        self,
        themes_input: CreateThemesInputDTO,
    ) -> CreateThemesOutputDTO:
        slugs = self._create_theme_slugs(themes_input)

        async with self.__catalog_graph_uow as uow:
            await self._ensure_slugs_are_available(slugs, uow)
            used_colors = await uow.theme_repository.list_theme_colors()
            themes = self._create_theme_entities(themes_input, slugs, used_colors)
            created_themes = await uow.theme_repository.create_many_themes(themes)
            output = CreateThemesOutputDTO.from_entities(created_themes)
            await uow.commit()

        return output

    def _create_theme_slugs(
        self,
        themes_input: CreateThemesInputDTO,
    ) -> list[str]:
        if not themes_input.themes:
            raise EmptyThemeBatchError()

        ordered_slugs: list[str] = []
        slugs: set[str] = set()

        for theme_data in themes_input.themes:
            slug = self._create_slug_for_theme(theme_data.label)
            if slug in slugs:
                raise ThemeAlreadyExistsError(slug)

            slugs.add(slug)
            ordered_slugs.append(slug)

        return ordered_slugs

    def _create_theme_entities(
        self,
        themes_input: CreateThemesInputDTO,
        slugs: list[str],
        used_colors: set[str],
    ) -> list[Theme]:
        created_at = self.__clock.now()
        themes: list[Theme] = []
        reserved_colors = set(used_colors)

        for theme_data, slug in zip(themes_input.themes, slugs, strict=True):
            color = self.__color_generator.generate(reserved_colors)
            reserved_colors.add(color)
            themes.append(
                Theme(
                    id=ThemeId(self.__ulid_generator.generate_ulid()),
                    label=theme_data.label,
                    description=theme_data.description,
                    is_active=theme_data.is_active,
                    created_at=created_at,
                    slug=slug,
                    color=color,
                )
            )

        return themes

    @staticmethod
    async def _ensure_slugs_are_available(
        slugs: list[str],
        uow: ICatalogGraphUnitOfWork,
    ) -> None:
        for slug in slugs:
            if await uow.theme_repository.get_theme_by_slug(slug) is not None:
                raise ThemeAlreadyExistsError(slug)

    def _create_slug_for_theme(self, label: str) -> str:
        slug = self.__slug_generator.generate_slug(label)
        if not slug:
            raise InvalidThemeSlugError()

        return slug
