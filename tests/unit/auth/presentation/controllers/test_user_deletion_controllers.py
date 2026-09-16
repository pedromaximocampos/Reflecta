import pytest

from src.modules.auth.presentation.controllers.delete_user_controller import DeleteUserController
from src.modules.auth.presentation.controllers.request_delete_controller import RequestDeleteController
from src.shared.domain.errors.api_types import AuthError
from src.shared.presentation.http_types import HttpRequest


class RequestDeleteUseCaseSpy:
    def __init__(self) -> None:
        self.user_ids = []

    async def execute(self, user_id) -> None:
        self.user_ids.append(user_id)


class DeleteUserUseCaseSpy:
    def __init__(self) -> None:
        self.codes = []

    async def execute(self, raw_code: str) -> None:
        self.codes.append(raw_code)


@pytest.mark.asyncio
async def test_request_delete_requires_authenticated_identity() -> None:
    controller = RequestDeleteController(RequestDeleteUseCaseSpy())
    request = HttpRequest(method="POST", url="/auth/request-delete")

    with pytest.raises(AuthError):
        await controller.handle_request(request)


@pytest.mark.asyncio
async def test_request_delete_uses_identity_injected_by_authentication_adapter() -> None:
    use_case = RequestDeleteUseCaseSpy()
    controller = RequestDeleteController(use_case)
    request = HttpRequest(
        method="POST",
        url="/auth/request-delete",
        authenticated_user_id="01TESTUSER0000000000000000",
    )

    response = await controller.handle_request(request)

    assert use_case.user_ids[0].value == "01TESTUSER0000000000000000"
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_delete_passes_query_code_to_use_case() -> None:
    use_case = DeleteUserUseCaseSpy()
    controller = DeleteUserController(use_case)
    request = HttpRequest(
        method="DELETE",
        url="/auth/delete?code=confirmation-code",
        query_params={"code": "confirmation-code"},
    )

    response = await controller.handle_request(request)

    assert use_case.codes == ["confirmation-code"]
    assert response.status_code == 200

