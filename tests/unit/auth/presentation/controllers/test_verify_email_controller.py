from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.modules.auth.presentation.controllers.verify_email_controller import VerifyEmailController
from src.shared.presentation.http_types import HttpRequest


@pytest.mark.asyncio
@pytest.mark.parametrize("success,status", [(True, 200), (False, 410)])
async def test_confirmation_distinguishes_verified_email_from_expired_code(success, status):
    use_case = AsyncMock()
    use_case.execute.return_value = SimpleNamespace(success=success, message="Verification result")
    controller = VerifyEmailController(use_case)
    request = HttpRequest(method="POST", url="http://test/auth/verify-email", query_params={"code": "test-code"})
    response = await controller.handle_request(request)
    assert response.status_code == status
    assert response.body == {"success": success, "message": "Verification result"}
    use_case.execute.assert_awaited_once_with("test-code")
