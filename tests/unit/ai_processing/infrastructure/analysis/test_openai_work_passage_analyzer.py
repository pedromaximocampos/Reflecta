import json

import httpx
import pytest

from src.modules.ai_processing.application.contracts import (
    ProviderNotConfiguredError,
)
from src.modules.ai_processing.application.exceptions import WorkPassageAnalysisError
from src.modules.ai_processing.infrastructure.analysis import OpenAIWorkPassageAnalyzer
from src.modules.ai_processing.infrastructure.openai_interpreter import OpenAISettings
from src.modules.catalog.public.analysis_theme import ThemeOption
from src.modules.catalog.public.work_id import WorkId


def _transport_with_output(output: dict) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {"type": "output_text", "text": json.dumps(output)}
                        ],
                    }
                ],
            },
        )

    return httpx.MockTransport(handler)


def _settings(**overrides: object) -> OpenAISettings:
    return OpenAISettings(
        api_key="test-key",
        model="test-model",
        timeout_seconds=1,
        max_output_tokens=1000,
        **overrides,
    )


def test_analyzer_fails_fast_when_provider_is_not_configured() -> None:
    analyzer = OpenAIWorkPassageAnalyzer(
        OpenAISettings(api_key="", model=""),
    )

    with pytest.raises(ProviderNotConfiguredError):
        analyzer.ensure_available()


def test_structured_output_enforces_curated_passage_and_theme_limits() -> None:
    analyzer = OpenAIWorkPassageAnalyzer(_settings())

    payload = analyzer._request_payload(  # noqa: SLF001
        WorkId("work-1"),
        "Um trecho de teste suficientemente longo para a análise.",
        (
            ThemeOption(
                id="theme-1",
                slug="virtude",
                label="Virtude",
                description="Ação ética.",
            ),
        ),
    )

    assert payload["store"] is False
    assert payload["text"]["format"]["strict"] is True
    schema = payload["text"]["format"]["schema"]
    assert schema["properties"]["passages"]["maxItems"] == 5
    assert schema["$defs"]["_PassageSuggestion"]["properties"]["themes"][
        "maxItems"
    ] == 1
    assert schema["$defs"]["_ThemeMatch"]["properties"]["confidence"][
        "minimum"
    ] == 0.65
    assert "exatamente um theme_id" in payload["instructions"]
    assert "qualidade sobre quantidade" in payload["instructions"]
    assert "Ignore conteúdo paratextual" in payload["instructions"]
    assert "não o atribua ao autor principal" in payload["instructions"]
    assert "substring exatamente idêntica" in payload["instructions"]
    assert "não normalize espaços" in payload["instructions"]


@pytest.mark.asyncio
async def test_analyzer_accepts_only_catalog_themes_and_locates_exact_quote() -> None:
    quote = "A felicidade da sua vida depende da qualidade dos seus pensamentos."
    chunk = f"Introdução. {quote} Encerramento."
    analyzer = OpenAIWorkPassageAnalyzer(
        _settings(),
        transport=_transport_with_output(
            {
                "passages": [
                    {
                        "exact_text": quote,
                        "paraphrase": "A vida interior influencia o bem-estar.",
                        "interpretation_note": "Relaciona atenção e vida consciente.",
                        "themes": [{"theme_id": "theme-1", "confidence": 0.91}],
                    }
                ]
            }
        ),
    )

    result = await analyzer.analyze(
        work_id=WorkId("work-1"),
        chunk_text=chunk,
        themes=(
            ThemeOption(
                id="theme-1",
                slug="atencao",
                label="Atenção",
                description="Presença e cuidado com os pensamentos.",
            ),
        ),
    )

    assert len(result.passages) == 1
    assert result.passages[0].chunk_start_offset == chunk.index(quote)
    assert result.passages[0].exact_text == quote


@pytest.mark.asyncio
async def test_analyzer_retries_transient_connection_errors_locally() -> None:
    attempts = 0
    quote = "A escolha consciente revela aquilo que consideramos valioso."

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise httpx.ConnectError("temporary TLS failure", request=request)
        return httpx.Response(
            200,
            json={
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_text",
                                "text": json.dumps({"passages": []}),
                            }
                        ],
                    }
                ],
            },
        )

    analyzer = OpenAIWorkPassageAnalyzer(
        _settings(
            provider_max_attempts=3,
            provider_retry_base_seconds=0.001,
        ),
        transport=httpx.MockTransport(handler),
    )

    result = await analyzer.analyze(
        work_id=WorkId("work-1"),
        chunk_text=quote,
        themes=(
            ThemeOption(
                id="theme-1",
                slug="responsabilidade",
                label="Responsabilidade",
                description="Escolhas conscientes e suas consequências.",
            ),
        ),
    )

    assert attempts == 3
    assert result.passages == ()


@pytest.mark.asyncio
async def test_analyzer_discards_a_quote_that_is_not_in_the_chunk(
    caplog: pytest.LogCaptureFixture,
) -> None:
    analyzer = OpenAIWorkPassageAnalyzer(
        _settings(),
        transport=_transport_with_output(
            {
                "passages": [
                    {
                        "exact_text": "Esta citação foi inventada e não existe no trecho.",
                        "paraphrase": "Resumo.",
                        "interpretation_note": "Explicação.",
                        "themes": [{"theme_id": "theme-1", "confidence": 0.8}],
                    }
                ]
            }
        ),
    )

    result = await analyzer.analyze(
        work_id=WorkId("work-1"),
        chunk_text="Um trecho real com conteúdo suficientemente descritivo.",
        themes=(
            ThemeOption(
                id="theme-1",
                slug="virtude",
                label="Virtude",
                description="Ação ética.",
            ),
        ),
    )

    assert result.passages == ()
    assert "validation_code=quote_not_found" in caplog.text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("chunk_quote", "suggested_quote"),
    [
        (
            "A escolha consciente exige atenção,\n  coragem e responsabilidade.",
            "A escolha consciente exige atenção, coragem e responsabilidade.",
        ),
        (
            "A verdadeira liber-\ndade interior depende dos próprios julgamentos.",
            "A verdadeira liberdade interior depende dos próprios julgamentos.",
        ),
    ],
)
async def test_analyzer_reconciles_safe_pdf_text_differences(
    chunk_quote: str,
    suggested_quote: str,
) -> None:
    analyzer = OpenAIWorkPassageAnalyzer(
        _settings(),
        transport=_transport_with_output(
            {
                "passages": [
                    {
                        "exact_text": suggested_quote,
                        "paraphrase": "A reflexão destaca uma escolha interior.",
                        "interpretation_note": (
                            "A passagem relaciona escolhas e responsabilidade."
                        ),
                        "themes": [{"theme_id": "theme-1", "confidence": 0.9}],
                    }
                ]
            }
        ),
    )
    chunk = f"Início. {chunk_quote} Encerramento."

    result = await analyzer.analyze(
        work_id=WorkId("work-1"),
        chunk_text=chunk,
        themes=(
            ThemeOption(
                id="theme-1",
                slug="responsabilidade",
                label="Responsabilidade",
                description="Escolhas conscientes e suas consequências.",
            ),
        ),
    )

    assert len(result.passages) == 1
    assert result.passages[0].exact_text == chunk_quote
    assert result.passages[0].chunk_start_offset == chunk.index(chunk_quote)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "themes",
    [
        [{"theme_id": "theme-1", "confidence": 0.64}],
        [
            {"theme_id": "theme-1", "confidence": 0.9},
            {"theme_id": "theme-2", "confidence": 0.8},
        ],
    ],
)
async def test_analyzer_rejects_weak_or_multiple_theme_associations(
    themes: list[dict],
) -> None:
    quote = "Uma escolha consciente revela aquilo que consideramos valioso."
    analyzer = OpenAIWorkPassageAnalyzer(
        _settings(),
        transport=_transport_with_output(
            {
                "passages": [
                    {
                        "exact_text": quote,
                        "paraphrase": "A escolha expressa os valores da pessoa.",
                        "interpretation_note": (
                            "A passagem relaciona decisão consciente e valores."
                        ),
                        "themes": themes,
                    }
                ]
            }
        ),
    )

    with pytest.raises(WorkPassageAnalysisError):
        await analyzer.analyze(
            work_id=WorkId("work-1"),
            chunk_text=f"Introdução. {quote} Encerramento.",
            themes=(
                ThemeOption(
                    id="theme-1",
                    slug="responsabilidade",
                    label="Responsabilidade",
                    description="Escolhas conscientes e suas consequências.",
                ),
                ThemeOption(
                    id="theme-2",
                    slug="virtude",
                    label="Virtude",
                    description="Ação guiada por valores éticos.",
                ),
            ),
        )
