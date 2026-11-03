from src.modules.catalog.application.ports.media import IWorkCoverProcessor
from src.modules.catalog.infrastructure.media import PillowWorkCoverProcessor


def get_work_cover_processor() -> IWorkCoverProcessor:
    return PillowWorkCoverProcessor()
