from src.modules.catalog.application.use_cases.create_themes.create_themes_use_case import (
    CreateThemesUseCase,
)
from src.modules.catalog.application.use_cases.delete_themes.delete_theme_by_id_use_case import (
    DeleteThemeByIdUseCase,
)
from src.modules.catalog.application.use_cases.get_themes.get_all_themes_use_case import (
    GetAllThemesUseCase,
)
from src.modules.catalog.application.use_cases.get_themes.get_theme_by_id_use_case import (
    GetThemeByIdUseCase,
)
from src.modules.catalog.application.use_cases.update_themes.update_theme_use_case import (
    UpdateThemeUseCase,
)
from src.modules.catalog.bootstrap.unit_of_work import get_graph_unit_of_work
from src.shared.infrastructure.system.providers import (
    get_clock,
    get_slug_generator,
    get_ulid_generator,
)


def get_create_themes_use_case() -> CreateThemesUseCase:
    return CreateThemesUseCase(
        catalog_graph_uow=get_graph_unit_of_work(),
        ulid_generator=get_ulid_generator(),
        clock=get_clock(),
        slug_generator=get_slug_generator(),
    )


def get_theme_by_id_use_case() -> GetThemeByIdUseCase:
    return GetThemeByIdUseCase(catalog_graph_uow=get_graph_unit_of_work())


def get_all_themes_use_case() -> GetAllThemesUseCase:
    return GetAllThemesUseCase(catalog_graph_uow=get_graph_unit_of_work())


def get_update_theme_use_case() -> UpdateThemeUseCase:
    return UpdateThemeUseCase(
        catalog_graph_uow=get_graph_unit_of_work(),
        clock=get_clock(),
    )


def get_delete_theme_by_id_use_case() -> DeleteThemeByIdUseCase:
    return DeleteThemeByIdUseCase(catalog_graph_uow=get_graph_unit_of_work())
