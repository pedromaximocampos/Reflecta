from src.modules.catalog.bootstrap.use_cases import get_create_themes_use_case
from src.modules.catalog.presentation.controllers.create_themes_controller import (
    CreateThemesController,
)


def get_create_themes_controller() -> CreateThemesController:
    return CreateThemesController(
        create_themes_use_case=get_create_themes_use_case(),
    )
