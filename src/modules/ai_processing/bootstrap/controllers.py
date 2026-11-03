from src.modules.ai_processing.bootstrap.use_cases import (
    get_list_work_ingestions_use_case,
)
from src.modules.ai_processing.presentation.controllers import (
    ListWorkIngestionsController,
)


def get_list_work_ingestions_controller() -> ListWorkIngestionsController:
    return ListWorkIngestionsController(get_list_work_ingestions_use_case())
