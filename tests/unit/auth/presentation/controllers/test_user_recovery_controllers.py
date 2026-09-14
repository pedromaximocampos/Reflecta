import pytest

from src.modules.auth.presentation.controllers.recovery_controller import RecoveryController
from src.modules.auth.presentation.controllers.request_recovery_controller import (
    RequestRecoveryController,
)
from src.shared.presentation.http_types import HttpRequest


class RequestRecoveryUseCaseSpy:
    def __init__(self) -> None:
        self.emails = []

    async def execute(self, email: str) -> None:
        self.emails.append(email)


class RecoveryUseCaseSpy:
    def __init__(self) -> None:
        self.codes = []

    async def execute(self, raw_code: str) -> None:
        self.codes.append(raw_code)


@pytest.mark.asyncio
async def test_request_recovery_returns_generic_accepted_response() -> None:
    use_case = RequestRecoveryUseCaseSpy()
    controller = RequestRecoveryController(use_case)
    request = HttpRequest(
        method="POST",
        url="/auth/request-recovery",
        body={"email": "deleted@example.com"},
    )

    response = await controller.handle_request(request)

    assert use_case.emails == ["deleted@example.com"]
    assert response.status_code == 202
    assert "If a deleted account" in response.body["message"]


@pytest.mark.asyncio
async def test_recovery_passes_query_code_to_use_case() -> None:
    use_case = RecoveryUseCaseSpy()
    controller = RecoveryController(use_case)
    request = HttpRequest(
        method="POST",
        url="/auth/recovery?code=recovery-code",
        query_params={"code": "recovery-code"},
    )

    response = await controller.handle_request(request)

    assert use_case.codes == ["recovery-code"]
    assert response.status_code == 200
