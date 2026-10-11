import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from src.modules.ai_processing.application.contracts import (
    InterpretationFailedError, InvalidInterpretationError, ProviderNotConfiguredError,
    ThemeOption,
    InvalidJournalInputError,
)
from src.modules.ai_processing.application.interpret_entry import InterpretEntry
from src.modules.ai_processing.infrastructure.unconfigured_interpreter import UnconfiguredInterpreter
from src.modules.catalog.public.analysis_catalog import AnalysisThemeCatalog
from src.modules.journal.public.analysis import EntrySnapshot

NOW = datetime(2026, 9, 30, tzinfo=timezone.utc)
THEME = ThemeOption(id="theme-1", slug="trabalho", label="Trabalho", description="Vida profissional")


def setup_case(raw=None):
    journal = SimpleNamespace(
        read=AsyncMock(return_value=EntrySnapshot("entry", "owner", "Meu dia no trabalho.", None, None, "draft")),
        save=AsyncMock(),
    )
    catalog = SimpleNamespace(active_themes=AsyncMock(return_value=(THEME,)))
    interpreter = SimpleNamespace(ensure_available=Mock(), interpret=AsyncMock(return_value=raw or {
        "summary": "Dia de trabalho", "main_message": "Reflexão sobre o trabalho",
        "themes": [{"theme_id": "theme-1", "confidence": 0.8}],
        "sentiments": ["preocupação"], "tone": "reflexivo",
    }))
    case = InterpretEntry(journal, catalog, interpreter, Mock(now=Mock(return_value=NOW)),
                         Mock(generate_ulid=Mock(return_value="analysis-id")))
    return case, journal, catalog, interpreter


@pytest.mark.asyncio
async def test_valid_analysis_is_scoped_and_persisted_with_catalog_identity():
    case, journal, _, provider = setup_case()
    assert await case.execute("entry", "owner") == "analysis-id"
    journal.read.assert_awaited_once_with("entry", "owner")
    request = provider.interpret.call_args.args[0]
    assert request.themes == (THEME,)
    assert request.content_text == "Meu dia no trabalho."
    values = journal.save.call_args.kwargs
    assert values["summary"] == "Dia de trabalho"
    assert values["metadata"]["themes"][0] == {
        **THEME.model_dump(), "confidence": 0.8, "source": "ai", "confirmed_by_user": False,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("change", [
    {"summary": "  "}, {"tone": 123}, {"extra": "not allowed"},
    {"themes": [{"theme_id": "invented", "confidence": 0.8}]},
    {"themes": [{"theme_id": "theme-1", "confidence": 1.1}]},
    {"themes": [{"theme_id": "theme-1", "confidence": float("nan")}]},
    {"themes": [{"theme_id": "theme-1", "confidence": 0.8}] * 2},
])
async def test_invalid_response_never_persists(change):
    case, journal, _, provider = setup_case()
    provider.interpret.return_value.update(change)
    with pytest.raises(InvalidInterpretationError):
        await case.execute("entry", "owner")
    journal.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_missing_provider_does_not_touch_catalog_or_persistence():
    case, journal, catalog, _ = setup_case()
    case.interpreter = UnconfiguredInterpreter()
    with pytest.raises(ProviderNotConfiguredError):
        await case.execute("entry", "owner")
    catalog.active_themes.assert_not_awaited()
    journal.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_provider_error_is_sanitized_and_preserves_existing_data():
    case, journal, _, provider = setup_case()
    provider.interpret.side_effect = RuntimeError("secret journal content and API key")
    with pytest.raises(InterpretationFailedError) as error:
        await case.execute("entry", "owner")
    assert str(error.value) == "Text interpretation failed."
    assert error.value.__suppress_context__
    journal.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_timeout_and_cancellation_do_not_persist():
    case, journal, _, provider = setup_case()
    async def slow(_):
        await asyncio.sleep(1)
    provider.interpret.side_effect = slow
    case.timeout_seconds = 0.001
    with pytest.raises(InterpretationFailedError):
        await case.execute("entry", "owner")
    provider.interpret.side_effect = asyncio.CancelledError
    with pytest.raises(asyncio.CancelledError):
        await case.execute("entry", "owner")
    journal.save.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("content", [" ", "x" * 10001])
async def test_invalid_input_never_calls_provider(content):
    case, journal, _, provider = setup_case()
    journal.read.return_value = EntrySnapshot("entry", "owner", content, None, None, "draft")
    with pytest.raises(InvalidJournalInputError):
        await case.execute("entry", "owner")
    provider.interpret.assert_not_awaited()
    journal.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_catalog_change_rejects_result():
    case, journal, catalog, _ = setup_case()
    catalog.active_themes.side_effect = [(THEME,), ()]
    with pytest.raises(InvalidInterpretationError):
        await case.execute("entry", "owner")
    journal.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_empty_catalog_allows_analysis_without_themes():
    case, journal, catalog, provider = setup_case()
    catalog.active_themes.return_value = ()
    provider.interpret.return_value["themes"] = []
    await case.execute("entry", "owner")
    assert journal.save.call_args.kwargs["metadata"]["themes"] == []


@pytest.mark.asyncio
async def test_catalog_adapter_only_returns_active_themes():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    uow.theme_repository.list_themes.return_value = [
        SimpleNamespace(id=SimpleNamespace(value="theme-1"), slug="trabalho",
                        label="Trabalho", description="Vida profissional", is_active=True),
        SimpleNamespace(is_active=False),
    ]
    assert await AnalysisThemeCatalog(uow).active_themes() == (THEME,)
