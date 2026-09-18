from src.modules.catalog.bootstrap.use_cases import (
    get_all_themes_use_case,
    get_create_themes_use_case,
    get_delete_theme_by_id_use_case,
    get_theme_by_id_use_case,
    get_update_theme_use_case,
)
from src.modules.catalog.presentation.controllers.create_themes_controller import (
    CreateThemesController,
)
from src.modules.catalog.presentation.controllers.delete_themes_controller import (
    DeleteThemeByIdController,
)
from src.modules.catalog.presentation.controllers.get_themes_controller import (
    GetAllThemesController,
    GetThemeByIdController,
)
from src.modules.catalog.presentation.controllers.update_theme_controller import (
    UpdateThemeController,
)


def get_create_themes_controller() -> CreateThemesController:
    return CreateThemesController(
        create_themes_use_case=get_create_themes_use_case(),
    )


def get_theme_by_id_controller() -> GetThemeByIdController:
    return GetThemeByIdController(
        get_theme_by_id_use_case=get_theme_by_id_use_case(),
    )


def get_all_themes_controller() -> GetAllThemesController:
    return GetAllThemesController(
        get_all_themes_use_case=get_all_themes_use_case(),
    )


def get_update_theme_controller() -> UpdateThemeController:
    return UpdateThemeController(update_theme_use_case=get_update_theme_use_case())


def get_delete_theme_by_id_controller() -> DeleteThemeByIdController:
    return DeleteThemeByIdController(
        delete_theme_by_id_use_case=get_delete_theme_by_id_use_case(),
    )
