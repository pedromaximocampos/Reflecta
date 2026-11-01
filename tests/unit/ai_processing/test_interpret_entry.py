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
from src.modules.ai_processing.application.failure_reasons import FailureReason
from src.modules.ai_processing.infrastructure.unconfigured_interpreter import UnconfiguredInterpreter
from src.modules.catalog.public.analysis_catalog import AnalysisThemeCatalog
from src.modules.catalog.public.contextual_passage import ContextualPassageCandidate
from src.modules.journal.public.analysis import EntrySnapshot

NOW = datetime(2026, 9, 30, tzinfo=timezone.utc)
THEME = ThemeOption(id="theme-1", slug="trabalho", label="Trabalho", description="Vida profissional")


def contextual_candidate(
    *,
    passage_id="passage-1",
    matched_theme_id="theme-1",
):
    return ContextualPassageCandidate(
        passage_id=passage_id,
        matched_theme_id=matched_theme_id,
        matched_theme_confidence=0.95,
        short_text="A passagem canônica da obra.",
        paraphrase="Uma paráfrase da passagem.",
        interpretation_note="Uma nota editorial sobre seu sentido.",
        locator="p. 10",
        priority=1,
        work_id="work-1",
        work_title="Obra",
        author_name="Autoria",
        start_page=10,
        end_page=10,
    )


def setup_case(raw=None):
    journal = SimpleNamespace(
        read=AsyncMock(return_value=EntrySnapshot("entry", "owner", "Meu dia no trabalho.", None, None, "draft")),
        save=AsyncMock(),
    )
    catalog = SimpleNamespace(active_themes=AsyncMock(return_value=(THEME,)))
    passage_catalog = SimpleNamespace(
        find_active_by_themes=AsyncMock(return_value=()),
    )
    passage_selector = SimpleNamespace(
        ensure_available=Mock(),
        select_contextual_passages=AsyncMock(return_value={"associations": []}),
    )
    interpreter = SimpleNamespace(ensure_available=Mock(), interpret=AsyncMock(return_value=raw or {
        "summary": "Dia de trabalho", "main_message": "Reflexão sobre o trabalho",
        "themes": [{"theme_id": "theme-1", "confidence": 0.8}],
        "sentiments": ["preocupação"], "tone": "reflexivo",
        "sentences": [{"sentence_text": "Meu dia no trabalho.",
                       "themes": [{"theme_id": "theme-1", "confidence": 0.85}]}],
    }))
    case = InterpretEntry(journal, catalog, interpreter, Mock(now=Mock(return_value=NOW)),
                         Mock(generate_ulid=Mock(return_value="analysis-id")),
                         passage_catalog=passage_catalog,
                         passage_selector=passage_selector)
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
    case.passage_catalog.find_active_by_themes.assert_awaited_once_with(
        ("theme-1",),
    )


@pytest.mark.asyncio
async def test_contextual_candidates_use_only_themes_present_in_sentences():
    case, _, catalog, provider = setup_case()
    unused = THEME.model_copy(update={
        "id": "theme-2",
        "slug": "unused",
        "label": "Unused",
    })
    catalog.active_themes.return_value = (THEME, unused)
    provider.interpret.return_value["themes"] = [
        {"theme_id": "theme-2", "confidence": 0.95},
        {"theme_id": "theme-1", "confidence": 0.85},
    ]

    await case.execute("entry", "owner")

    case.passage_catalog.find_active_by_themes.assert_awaited_once_with(
        ("theme-1",),
    )


@pytest.mark.asyncio
async def test_contextual_catalog_failure_does_not_persist_partial_analysis():
    case, journal, _, _ = setup_case()
    case.passage_catalog.find_active_by_themes.side_effect = RuntimeError(
        "private connection details",
    )

    with pytest.raises(InterpretationFailedError) as error:
        await case.execute("entry", "owner")

    assert error.value.reason == FailureReason.CATALOG
    assert str(error.value) == "Text interpretation failed."
    journal.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_contextual_selector_receives_only_trusted_ids_and_candidates():
    case, journal, _, _ = setup_case()
    candidate = contextual_candidate()
    case.passage_catalog.find_active_by_themes.return_value = (candidate,)
    case.passage_selector.select_contextual_passages.return_value = {
        "associations": [{
            "sentence_id": "analysis-id",
            "passage_id": "passage-1",
            "confidence": 0.92,
            "reason": "A passagem amplia a reflexão presente na frase.",
        }],
    }

    await case.execute("entry", "owner")

    case.passage_selector.ensure_available.assert_called_once_with()
    request = case.passage_selector.select_contextual_passages.call_args.args[0]
    assert request.sentences[0].sentence_id == "analysis-id"
    assert request.sentences[0].sentence_text == "Meu dia no trabalho."
    assert request.sentences[0].themes[0].theme_id == "theme-1"
    assert request.candidates == (candidate,)
    saved_passage = journal.save.call_args.kwargs["sentences"][0].passages[0]
    assert saved_passage.passage_id == "passage-1"
    assert saved_passage.confidence == 0.92
    assert saved_passage.reason == (
        "A passagem amplia a reflexão presente na frase."
    )
    assert saved_passage.payload_snapshot == {
        "schema_version": 1,
        "passage_id": "passage-1",
        "short_text": "A passagem canônica da obra.",
        "paraphrase": "Uma paráfrase da passagem.",
        "interpretation_note": "Uma nota editorial sobre seu sentido.",
        "locator": "p. 10",
        "priority": 1,
        "start_page": 10,
        "end_page": 10,
        "work": {"id": "work-1", "title": "Obra", "author_name": "Autoria"},
        "theme_matches": [{"theme_id": "theme-1", "confidence": 0.95}],
    }
    assert "Meu dia no trabalho" not in str(saved_passage.payload_snapshot)


@pytest.mark.asyncio
async def test_contextual_selector_is_skipped_without_candidates():
    case, _, _, _ = setup_case()

    await case.execute("entry", "owner")

    case.passage_selector.ensure_available.assert_not_called()
    case.passage_selector.select_contextual_passages.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("associations", [
    [{"sentence_id": "invented", "passage_id": "passage-1", "confidence": 0.9,
      "reason": "Relação inventada."}],
    [{"sentence_id": "analysis-id", "passage_id": "invented", "confidence": 0.9,
      "reason": "Relação inventada."}],
    [
        {"sentence_id": "analysis-id", "passage_id": "passage-1", "confidence": 0.9,
         "reason": "Primeira relação."},
        {"sentence_id": "analysis-id", "passage_id": "passage-2", "confidence": 0.88,
         "reason": "Segunda relação."},
    ],
    [{"sentence_id": "analysis-id", "passage_id": "passage-1", "confidence": 0.79,
      "reason": "Confiança insuficiente."}],
])
async def test_invalid_contextual_selection_never_persists(associations):
    case, journal, _, _ = setup_case()
    case.passage_catalog.find_active_by_themes.return_value = (
        contextual_candidate(),
        contextual_candidate(passage_id="passage-2"),
    )
    case.passage_selector.select_contextual_passages.return_value = {
        "associations": associations,
    }

    with pytest.raises(InvalidInterpretationError) as error:
        await case.execute("entry", "owner")

    assert error.value.reason == FailureReason.PASSAGES
    journal.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_contextual_selection_requires_a_shared_sentence_theme():
    case, journal, _, _ = setup_case()
    case.passage_catalog.find_active_by_themes.return_value = (
        contextual_candidate(matched_theme_id="theme-2"),
    )
    case.passage_selector.select_contextual_passages.return_value = {
        "associations": [{
            "sentence_id": "analysis-id",
            "passage_id": "passage-1",
            "confidence": 0.91,
            "reason": "Sem tema compartilhado.",
        }],
    }

    with pytest.raises(InvalidInterpretationError) as error:
        await case.execute("entry", "owner")

    assert error.value.reason == FailureReason.PASSAGES
    journal.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_contextual_selector_failure_does_not_persist_partial_analysis():
    case, journal, _, _ = setup_case()
    case.passage_catalog.find_active_by_themes.return_value = (
        contextual_candidate(),
    )
    case.passage_selector.select_contextual_passages.side_effect = (
        InterpretationFailedError(reason=FailureReason.RATE_LIMIT)
    )

    with pytest.raises(InterpretationFailedError) as error:
        await case.execute("entry", "owner")

    assert error.value.reason == FailureReason.RATE_LIMIT
    journal.save.assert_not_awaited()


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
@pytest.mark.parametrize("content", [" ", "x" * 20001])
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
    provider.interpret.return_value["sentences"][0]["themes"] = []
    await case.execute("entry", "owner")
    assert journal.save.call_args.kwargs["metadata"]["themes"] == []
    case.passage_catalog.find_active_by_themes.assert_not_awaited()


@pytest.mark.asyncio
async def test_catalog_adapter_only_returns_active_themes():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    uow.theme_repository.list_themes.return_value = [
        SimpleNamespace(id=SimpleNamespace(value="theme-1"), slug="trabalho",
                        label="Trabalho", description="Vida profissional", color=THEME.color, is_active=True),
        SimpleNamespace(is_active=False),
    ]
    assert await AnalysisThemeCatalog(uow).active_themes() == (THEME,)
    uow.theme_repository.create_many_themes.assert_not_awaited()
    uow.theme_repository.create_theme.assert_not_awaited()
    uow.theme_repository.update_theme.assert_not_awaited()


@pytest.mark.asyncio
async def test_sentences_preserve_unicode_offsets_order_and_individual_themes():
    case, journal, _, provider = setup_case()
    text = "  Estou cansado 😴.\n\nMas gostei do trabalho!  "
    journal.read.return_value = EntrySnapshot("entry", "owner", text, None, None, "draft")
    provider.interpret.return_value["sentences"] = [
        {"sentence_text": "Estou cansado 😴.", "themes": []},
        {"sentence_text": "Mas gostei do trabalho!", "themes": [{"theme_id": "theme-1", "confidence": 0.86}]},
    ]
    await case.execute("entry", "owner")
    sentences = journal.save.call_args.kwargs["sentences"]
    assert [sentence.sentence_index for sentence in sentences] == [0, 1]
    assert sentences[0].start_offset == 2
    for sentence in sentences:
        assert text[sentence.start_offset:sentence.end_offset] == sentence.sentence_text
    assert sentences[0].themes == ()
    assert sentences[1].themes[0] == {
        **THEME.model_dump(), "confidence": 0.86, "source": "ai", "confirmed_by_user": False,
    }
    assert journal.save.call_args.kwargs["metadata"]["schema_version"] == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("sentences", [
    [],
    [{"sentence_text": "Texto inventado.", "themes": []}],
    [{"sentence_text": "Meu dia", "themes": []}],
    [{"sentence_text": "no trabalho.", "themes": []}],
    [{"sentence_text": "Meu dia no trabalho.", "themes": []}] * 2,
    [{"sentence_text": "Meu dia no trabalho.", "themes": [{"theme_id": "unknown", "confidence": 0.8}]}],
    [{"sentence_text": "Meu dia no trabalho.", "themes": [{"theme_id": "theme-1", "confidence": 0.8}] * 2}],
    [{"sentence_text": "Meu dia no trabalho.", "themes": [{"theme_id": "theme-1", "confidence": -0.1}]}],
])
async def test_invalid_sentences_never_persist(sentences):
    case, journal, _, provider = setup_case()
    provider.interpret.return_value["sentences"] = sentences
    with pytest.raises(InvalidInterpretationError):
        await case.execute("entry", "owner")
    journal.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_sentence_theme_must_also_be_selected_in_overall_analysis():
    case, journal, _, provider = setup_case()
    provider.interpret.return_value["themes"] = []
    with pytest.raises(InvalidInterpretationError):
        await case.execute("entry", "owner")
    journal.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_repeated_identical_sentences_have_distinct_source_offsets():
    case, journal, _, provider = setup_case()
    journal.read.return_value = EntrySnapshot("entry", "owner", "Oi. Oi.", None, None, "draft")
    provider.interpret.return_value["sentences"] = [{"sentence_text": "Oi.", "themes": []}] * 2
    await case.execute("entry", "owner")
    assert [(s.start_offset, s.end_offset) for s in journal.save.call_args.kwargs["sentences"]] == [(0, 3), (4, 7)]


@pytest.mark.asyncio
@pytest.mark.parametrize("extra", [{"label": "Tema inventado"}, {"color": "#FF0000"}])
async def test_ai_cannot_create_or_modify_theme_properties(extra):
    case, journal, _, provider = setup_case()
    provider.interpret.return_value["themes"][0].update(extra)
    with pytest.raises(InvalidInterpretationError):
        await case.execute("entry", "owner")
    journal.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_analysis_and_sentences_use_catalog_color_without_ai_overrides():
    case, journal, catalog, provider = setup_case()
    colored = THEME.model_copy(update={"color": "#12ABEF"})
    catalog.active_themes.return_value = (colored,)
    await case.execute("entry", "owner")
    request = provider.interpret.call_args.args[0]
    assert request.themes[0].color == "#12ABEF"
    saved = journal.save.call_args.kwargs
    assert saved["metadata"]["themes"][0]["color"] == "#12ABEF"
    assert saved["sentences"][0].themes[0]["color"] == "#12ABEF"


@pytest.mark.asyncio
async def test_sentiments_are_deduplicated_without_inventing_emotions():
    case, journal, _, provider = setup_case()
    provider.interpret.return_value["sentiments"] = ["Tristeza", "tristeza", "Esperança"]
    await case.execute("entry", "owner")
    assert journal.save.call_args.kwargs["metadata"]["sentiments"] == ["tristeza", "esperança"]


@pytest.mark.asyncio
async def test_global_themes_exclude_unused_catalog_matches():
    case, journal, _, provider = setup_case()
    provider.interpret.return_value["sentences"][0]["themes"] = []
    await case.execute("entry", "owner")
    assert journal.save.call_args.kwargs["metadata"]["themes"] == []


@pytest.mark.asyncio
async def test_theme_confidence_below_reflective_threshold_never_persists():
    case, journal, _, provider = setup_case()
    provider.interpret.return_value["themes"][0]["confidence"] = 0.79
    with pytest.raises(InvalidInterpretationError):
        await case.execute("entry", "owner")
    journal.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_themes_are_persisted_in_descending_provider_confidence_order():
    case, journal, catalog, provider = setup_case()
    themes = tuple(
        THEME.model_copy(update={
            "id": f"theme-{index}",
            "slug": f"theme-{index}",
            "label": f"Theme {index}",
        })
        for index in range(1, 4)
    )
    catalog.active_themes.return_value = themes
    provider.interpret.return_value["themes"] = [
        {"theme_id": "theme-1", "confidence": 0.81},
        {"theme_id": "theme-3", "confidence": 0.97},
        {"theme_id": "theme-2", "confidence": 0.89},
    ]
    provider.interpret.return_value["sentences"][0]["themes"] = [
        {"theme_id": "theme-2", "confidence": 0.84},
        {"theme_id": "theme-3", "confidence": 0.95},
        {"theme_id": "theme-1", "confidence": 0.80},
    ]

    await case.execute("entry", "owner")

    saved = journal.save.call_args.kwargs
    assert [theme["id"] for theme in saved["metadata"]["themes"]] == [
        "theme-3", "theme-2", "theme-1",
    ]
    assert [theme["id"] for theme in saved["sentences"][0].themes] == [
        "theme-3", "theme-2", "theme-1",
    ]


@pytest.mark.asyncio
async def test_use_case_preserves_safe_provider_reason():
    from src.modules.ai_processing.application.failure_reasons import FailureReason
    case, journal, _, provider = setup_case()
    provider.interpret.side_effect = InterpretationFailedError(reason=FailureReason.RATE_LIMIT)
    with pytest.raises(InterpretationFailedError) as error:
        await case.execute("entry", "owner")
    assert error.value.reason == FailureReason.RATE_LIMIT
    journal.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_full_journal_limit_can_be_processed_as_one_sentence():
    content = "x" * 20000
    case, journal, _, provider = setup_case()
    journal.read.return_value = EntrySnapshot("entry", "owner", content, None, NOW, "pending_analysis")
    provider.interpret.return_value["sentences"] = [{"sentence_text": content, "themes": []}]
    assert await case.execute("entry", "owner") == "analysis-id"
    assert len(provider.interpret.call_args.args[0].content_text) == 20000
    journal.save.assert_awaited_once()
