from src.modules.catalog.application.dto.theme import ThemeOutputDTO
from src.modules.catalog.application.use_cases.update_themes.dto import (
    UpdateThemeInputDTO,
)
from src.modules.catalog.application.use_cases.update_themes.iupdate_theme_use_case import (
    IUpdateThemeUseCase,
)
from src.modules.catalog.domain.exceptions.theme_exceptions import (
    EmptyThemeUpdateError,
    ThemeNotFoundError,
)
from src.modules.catalog.domain.ports.unit_of_work.icatalog_graph_unit_of_work import (
    ICatalogGraphUnitOfWork,
)
from src.shared.domain.ports.system.iclock import IClock


class UpdateThemeUseCase(IUpdateThemeUseCase):
    def __init__(
        self,
        catalog_graph_uow: ICatalogGraphUnitOfWork,
        clock: IClock,
    ) -> None:
        self.__catalog_graph_uow = catalog_graph_uow
        self.__clock = clock

    async def execute(self, theme_input: UpdateThemeInputDTO) -> ThemeOutputDTO:
        if (
            theme_input.label is None
            and theme_input.description is None
            and theme_input.is_active is None
        ):
            raise EmptyThemeUpdateError()

        async with self.__catalog_graph_uow as uow:
            theme = await uow.theme_repository.get_theme_by_id(theme_input.theme_id)
            if theme is None:
                raise ThemeNotFoundError(theme_input.theme_id.value)

            updated_at = self.__clock.now()
            if theme_input.label is not None or theme_input.description is not None:
                theme.update(
                    label=theme_input.label,
                    description=theme_input.description,
                    updated_at=updated_at,
                )

            if theme_input.is_active is True:
                theme.activate(updated_at)
            elif theme_input.is_active is False:
                theme.deactivate(updated_at)

            updated_theme = await uow.theme_repository.update_theme(theme)
            output = ThemeOutputDTO.from_entity(updated_theme)
            await uow.commit()

        return output
