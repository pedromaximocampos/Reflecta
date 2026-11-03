from dataclasses import replace
from unittest.mock import Mock, AsyncMock
import pytest
from src.modules.auth.public import UserRole
from src.modules.operations.presentation.routes import default_analysis_settings
from tests.unit.operations.test_reprocess_routes import client_for, FAILURE_ID
from tests.unit.operations.test_failure_routes import BASE, HEADERS
from tests.unit.ai_processing.test_analysis_gateway import setup_gateway, NOW
from tests.unit.ai_processing.test_worker import setup
from src.modules.ai_processing.worker import process_one

SETTINGS = {"model": "gpt-6-luna", "timeout_seconds": 60.0,
            "max_output_tokens": 12000, "reasoning_effort": "low"}


def test_admin_can_read_non_secret_defaults_and_override_single_request():
    client, gateway = client_for()
    response = client.get(BASE + '/analysis-settings', headers=HEADERS)
    assert response.status_code == 200
    assert set(response.json()) == set(SETTINGS)
    result = client.post(BASE + f'/journal/{FAILURE_ID}/reprocess', headers=HEADERS, json=SETTINGS)
    assert result.status_code == 202
    assert gateway.admin_reprocess.call_args.kwargs['processing_settings'] == SETTINGS
    assert default_analysis_settings().model_dump() == response.json()


@pytest.mark.parametrize('change', [
    {'api_key': 'not-allowed'}, {'base_url': 'https://example.invalid'},
    {'timeout_seconds': 0}, {'timeout_seconds': 601},
    {'max_output_tokens': 128001}, {'max_output_tokens': True},
    {'reasoning_effort': 'unknown'}, {'model': 'bad/model'},
])
def test_invalid_or_secret_settings_do_not_enqueue(change):
    client, gateway = client_for()
    response = client.post(BASE + f'/journal/{FAILURE_ID}/reprocess', headers=HEADERS, json=SETTINGS | change)
    assert response.status_code == 422
    gateway.admin_reprocess.assert_not_awaited()


def test_user_cannot_read_defaults_or_override_admin_request():
    client, gateway = client_for(UserRole.USER)
    assert client.get(BASE + '/analysis-settings', headers=HEADERS).status_code == 403
    assert client.post(BASE + f'/journal/{FAILURE_ID}/reprocess', headers=HEADERS, json=SETTINGS).status_code == 403
    gateway.admin_reprocess.assert_not_awaited()


@pytest.mark.asyncio
async def test_admin_settings_are_durable_audited_and_pending_repeat_does_not_replace_them():
    gateway, session, entry = setup_gateway()
    entry.status = 'analysis_failed'
    entry.user_reprocess_count = 3
    session.scalar.return_value = 'failure'
    await gateway.admin_reprocess('failure', 'admin', now=NOW, processing_settings=SETTINGS)
    assert entry.processing_settings == SETTINGS
    assert session.add.call_args.args[0].processing_settings == SETTINGS
    assert entry.user_reprocess_count == 3
    await gateway.admin_reprocess('failure', 'admin', now=NOW, processing_settings=SETTINGS | {'timeout_seconds': 120.0})
    assert entry.processing_settings == SETTINGS
    session.add.assert_called_once()


@pytest.mark.asyncio
async def test_worker_uses_custom_case_for_request_then_returns_to_default_case():
    gateway, default, snapshot = setup()
    from types import SimpleNamespace
    custom = SimpleNamespace(execute=AsyncMock(return_value='analysis'))
    factory = Mock(return_value=custom)
    gateway.next_pending.return_value = replace(snapshot, processing_settings=SETTINGS)
    await process_one(gateway, default, case_factory=factory)
    factory.assert_called_once_with(processing_settings=SETTINGS)
    custom.execute.assert_awaited_once_with('entry', 'owner')
    default.execute.assert_not_awaited()
    gateway.next_pending.return_value = snapshot
    await process_one(gateway, default, case_factory=factory)
    default.execute.assert_awaited_once_with('entry', 'owner')
    assert factory.call_count == 1


def test_factory_sets_both_providers_and_application_timeout_without_mutating_defaults(monkeypatch):
    from types import SimpleNamespace
    from src.modules.ai_processing.bootstrap import use_cases
    from src.modules.ai_processing.infrastructure.openai_interpreter import OpenAISettings
    monkeypatch.setattr(use_cases, 'get_contextual_passage_catalog', lambda: SimpleNamespace())
    before = OpenAISettings().model_dump(exclude={'api_key'})
    case = use_cases.get_interpret_entry(processing_settings=SETTINGS)
    assert case.timeout_seconds == 60
    assert case.interpreter is case.passage_selector
    assert case.interpreter.settings.max_output_tokens == 12000
    assert case.interpreter.settings.model == 'gpt-6-luna'
    assert OpenAISettings().model_dump(exclude={'api_key'}) == before
