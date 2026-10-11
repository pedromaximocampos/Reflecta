import asyncio

from pydantic import ValidationError

from src.modules.ai_processing.application.contracts import (
    ITextInterpreter, IThemeCatalog, Interpretation, InterpretationRequest,
    InterpretationFailedError, InvalidInterpretationError, ProviderNotConfiguredError,
    InvalidJournalInputError,
)
from src.modules.journal.public.analysis import IJournalAnalysisGateway
from src.shared.domain.ports.system.iclock import IClock
from src.shared.domain.ports.system.iulid_generator import IULIDGenerator


class InterpretEntry:
    def __init__(
        self, journal: IJournalAnalysisGateway, catalog: IThemeCatalog,
        interpreter: ITextInterpreter, clock: IClock, ids: IULIDGenerator,
        *, timeout_seconds: float = 30,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("Timeout must be positive.")
        self.journal, self.catalog, self.interpreter = journal, catalog, interpreter
        self.clock, self.ids, self.timeout_seconds = clock, ids, timeout_seconds

    async def execute(self, entry_id: str, user_id: str) -> str:
        # A trusted caller supplies the owner; never take it from the AI response.
        snapshot = await self.journal.read(entry_id, user_id)
        self.interpreter.ensure_available()
        themes = await self.catalog.active_themes()
        try:
            request = InterpretationRequest(
                content_text=snapshot.content_text, context_tags=snapshot.context_tags,
                themes=themes,
            )
        except ValidationError:
            raise InvalidJournalInputError("Invalid journal input.") from None
        try:
            async with asyncio.timeout(self.timeout_seconds):
                raw = await self.interpreter.interpret(request)
        except ProviderNotConfiguredError:
            raise
        except Exception:
            raise InterpretationFailedError("Text interpretation failed.") from None
        try:
            result = Interpretation.model_validate(raw)
        except ValidationError:
            raise InvalidInterpretationError("Invalid interpretation response.") from None

        allowed = {theme.id: theme for theme in themes}
        selected = [theme.theme_id for theme in result.themes]
        if len(selected) != len(set(selected)) or not set(selected) <= allowed.keys():
            raise InvalidInterpretationError("Invalid theme selection.")
        # Recheck eligibility after the external call. Neo4j/PostgreSQL are not
        # a distributed transaction; retain the catalog snapshot for traceability.
        current = {theme.id: theme for theme in await self.catalog.active_themes()}
        if any(current.get(theme_id) != allowed[theme_id] for theme_id in selected):
            raise InvalidInterpretationError("Selected catalog themes changed.")

        metadata = {
            "schema_version": 1,
            "sentiments": result.sentiments,
            "tone": result.tone,
            "themes": [
                {**allowed[match.theme_id].model_dump(), "confidence": match.confidence,
                 "source": "ai", "confirmed_by_user": False}
                for match in result.themes
            ],
        }
        analysis_id = self.ids.generate_ulid()
        await self.journal.save(
            snapshot, analysis_id=analysis_id, summary=result.summary,
            main_message=result.main_message, metadata=metadata, now=self.clock.now(),
        )
        return analysis_id
