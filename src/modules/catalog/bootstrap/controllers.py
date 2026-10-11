from src.modules.catalog.bootstrap.use_cases import (
    get_all_themes_use_case,
    get_create_themes_use_case,
    get_create_work_use_case,
    get_request_work_ingestion_use_case,
    get_delete_theme_by_id_use_case,
    get_theme_by_id_use_case,
    get_update_theme_use_case,
    get_create_passage_use_case,
    get_delete_passage_use_case,
    get_list_passages_use_case,
    get_passage_use_case,
    get_review_passage_use_case,
    get_set_passage_availability_use_case,
    get_update_passage_use_case,
)
from src.modules.catalog.presentation.controllers.passage_controller import (
    CreatePassageController,
    DeletePassageController,
    GetPassageController,
    ListPassagesController,
    ReviewPassageController,
    SetPassageAvailabilityController,
    UpdatePassageController,
)
from src.modules.catalog.presentation.controllers.create_themes_controller import (
    CreateThemesController,
)
from src.modules.catalog.presentation.controllers.create_work_controller import CreateWorkController
from src.modules.catalog.presentation.controllers.request_work_ingestion_controller import (
    RequestWorkIngestionController,
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


def get_create_work_controller() -> CreateWorkController:
    return CreateWorkController(create_work_use_case=get_create_work_use_case())


def get_request_work_ingestion_controller() -> RequestWorkIngestionController:
    return RequestWorkIngestionController(
        request_work_ingestion_use_case=get_request_work_ingestion_use_case(),
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


def get_create_passage_controller() -> CreatePassageController:
    return CreatePassageController(get_create_passage_use_case())


def get_passage_controller() -> GetPassageController:
    return GetPassageController(get_passage_use_case())


def get_list_passages_controller() -> ListPassagesController:
    return ListPassagesController(get_list_passages_use_case())


def get_update_passage_controller() -> UpdatePassageController:
    return UpdatePassageController(get_update_passage_use_case())


def get_approve_passage_controller() -> ReviewPassageController:
    return ReviewPassageController(get_review_passage_use_case(), approve=True)


def get_reject_passage_controller() -> ReviewPassageController:
    return ReviewPassageController(get_review_passage_use_case(), approve=False)


def get_activate_passage_controller() -> SetPassageAvailabilityController:
    return SetPassageAvailabilityController(
        get_set_passage_availability_use_case(),
        active=True,
    )


def get_deactivate_passage_controller() -> SetPassageAvailabilityController:
    return SetPassageAvailabilityController(
        get_set_passage_availability_use_case(),
        active=False,
    )


def get_delete_passage_controller() -> DeletePassageController:
    return DeletePassageController(get_delete_passage_use_case())
