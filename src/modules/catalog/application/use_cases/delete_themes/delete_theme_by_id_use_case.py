from src.modules.catalog.application.use_cases.delete_themes.idelete_theme_by_id_use_case import (
    IDeleteThemeByIdUseCase,
)
from src.modules.catalog.domain.exceptions.theme_exceptions import ThemeNotFoundError
from src.modules.catalog.domain.ports.unit_of_work.icatalog_graph_unit_of_work import (
    ICatalogGraphUnitOfWork,
)
from src.modules.catalog.public.theme_id import ThemeId


class DeleteThemeByIdUseCase(IDeleteThemeByIdUseCase):
    def __init__(self, catalog_graph_uow: ICatalogGraphUnitOfWork) -> None:
        self.__catalog_graph_uow = catalog_graph_uow

    async def execute(self, theme_id: ThemeId) -> None:
        async with self.__catalog_graph_uow as uow:
            theme = await uow.theme_repository.get_theme_by_id(theme_id)
            if theme is None:
                raise ThemeNotFoundError(theme_id.value)

            await uow.theme_repository.delete_theme(theme_id)
            await uow.commit()
