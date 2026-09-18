from src.modules.catalog.application.dto.theme import ThemesOutputDTO
from src.modules.catalog.application.use_cases.get_themes.iget_all_themes_use_case import (
    IGetAllThemesUseCase,
)
from src.modules.catalog.domain.ports.unit_of_work.icatalog_graph_unit_of_work import (
    ICatalogGraphUnitOfWork,
)


class GetAllThemesUseCase(IGetAllThemesUseCase):
    def __init__(self, catalog_graph_uow: ICatalogGraphUnitOfWork) -> None:
        self.__catalog_graph_uow = catalog_graph_uow

    async def execute(self) -> ThemesOutputDTO:
        async with self.__catalog_graph_uow as uow:
            themes = await uow.theme_repository.list_themes()
            return ThemesOutputDTO.from_entities(themes)
