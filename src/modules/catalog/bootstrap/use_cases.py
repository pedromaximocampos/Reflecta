from src.modules.catalog.application.use_cases.create_themes.create_themes_use_case import (
    CreateThemesUseCase,
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
