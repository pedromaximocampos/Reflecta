from src.modules.catalog.application.use_cases.create_themes.create_themes_use_case import (
    CreateThemesUseCase,
)
from src.modules.catalog.application.use_cases.create_work.create_work_use_case import CreateWorkUseCase
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
from src.modules.catalog.application.use_cases.request_work_ingestion.request_work_ingestion_use_case import (
    RequestWorkIngestionUseCase,
)
from src.modules.catalog.application.use_cases.manage_passages import (
    CreatePassageUseCase,
    DeletePassageUseCase,
    GetPassageUseCase,
    ListPassagesUseCase,
    ReviewPassageUseCase,
    SetPassageAvailabilityUseCase,
    UpdatePassageUseCase,
)
from src.modules.catalog.bootstrap.storage import get_work_document_storage
from src.modules.catalog.bootstrap.unit_of_work import (
    get_graph_unit_of_work,
    get_sql_unit_of_work,
)
from src.modules.internal_events.bootstrap.services import get_outbox_service
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


def get_create_work_use_case() -> CreateWorkUseCase:
    return CreateWorkUseCase(
        catalog_graph_uow=get_graph_unit_of_work(),
        ulid_generator=get_ulid_generator(),
        clock=get_clock(),
        slug_generator=get_slug_generator(),
    )


def get_request_work_ingestion_use_case() -> RequestWorkIngestionUseCase:
    return RequestWorkIngestionUseCase(
        catalog_graph_uow=get_graph_unit_of_work(),
        catalog_sql_uow=get_sql_unit_of_work(),
        work_document_storage=get_work_document_storage(),
        outbox_service=get_outbox_service(),
        ulid_generator=get_ulid_generator(),
        clock=get_clock(),
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


def get_create_passage_use_case() -> CreatePassageUseCase:
    return CreatePassageUseCase(
        graph_uow=get_graph_unit_of_work(),
        ids=get_ulid_generator(),
        clock=get_clock(),
    )


def get_passage_use_case() -> GetPassageUseCase:
    return GetPassageUseCase(get_graph_unit_of_work())


def get_list_passages_use_case() -> ListPassagesUseCase:
    return ListPassagesUseCase(get_graph_unit_of_work())


def get_update_passage_use_case() -> UpdatePassageUseCase:
    return UpdatePassageUseCase(get_graph_unit_of_work(), get_clock())


def get_review_passage_use_case() -> ReviewPassageUseCase:
    return ReviewPassageUseCase(
        get_graph_unit_of_work(),
        get_sql_unit_of_work(),
        get_clock(),
    )


def get_set_passage_availability_use_case() -> SetPassageAvailabilityUseCase:
    return SetPassageAvailabilityUseCase(get_graph_unit_of_work(), get_clock())


def get_delete_passage_use_case() -> DeletePassageUseCase:
    return DeletePassageUseCase(
        get_graph_unit_of_work(),
        get_sql_unit_of_work(),
        get_clock(),
    )
