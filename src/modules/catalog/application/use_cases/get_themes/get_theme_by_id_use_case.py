from src.modules.catalog.application.dto.theme import ThemeOutputDTO
from src.modules.catalog.application.use_cases.get_themes.iget_theme_by_id_use_case import (
    IGetThemeByIdUseCase,
)
from src.modules.catalog.domain.exceptions.theme_exceptions import ThemeNotFoundError
from src.modules.catalog.domain.ports.unit_of_work.icatalog_graph_unit_of_work import (
    ICatalogGraphUnitOfWork,
)
from src.modules.catalog.public.theme_id import ThemeId


class GetThemeByIdUseCase(IGetThemeByIdUseCase):
    def __init__(self, catalog_graph_uow: ICatalogGraphUnitOfWork) -> None:
        self.__catalog_graph_uow = catalog_graph_uow

    async def execute(self, theme_id: ThemeId) -> ThemeOutputDTO:
        async with self.__catalog_graph_uow as uow:
            theme = await uow.theme_repository.get_theme_by_id(theme_id)
            if theme is None:
                raise ThemeNotFoundError(theme_id.value)

            return ThemeOutputDTO.from_entity(theme)
