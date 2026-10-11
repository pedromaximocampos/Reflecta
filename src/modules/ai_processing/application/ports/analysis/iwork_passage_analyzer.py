from typing import Protocol

from src.modules.ai_processing.application.dto import WorkChunkAnalysisDTO
from src.modules.catalog.public.analysis_theme import ThemeOption
from src.modules.catalog.public.work_id import WorkId


class IWorkPassageAnalyzer(Protocol):
    def ensure_available(self) -> None: ...

    async def analyze(
        self,
        *,
        work_id: WorkId,
        chunk_text: str,
        themes: tuple[ThemeOption, ...],
    ) -> WorkChunkAnalysisDTO: ...
