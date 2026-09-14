from datetime import date

import pytest

from src.modules.auth.application.use_cases.update_user_info.dto import UpdateUserInfoOutput
from src.modules.auth.presentation.controllers.update_user_info_controller import (
    UpdateUserInfoController,
)
from src.modules.auth.presentation.validators.update_user_info import UpdateUserInfoValidator
from src.modules.auth.public.user_id import UserId
from src.shared.domain.errors.api_types import AuthError
from src.shared.presentation.http_types import HttpRequest


class UpdateUserInfoUseCaseSpy:
    def __init__(self) -> None:
        self.dto = None

    async def execute(self, dto):
        self.dto = dto
        return UpdateUserInfoOutput(
            user_id=dto.user_id,
            name=dto.name or "Existing",
            surname=dto.surname or "User",
            date_of_birth=dto.date_of_birth or date(2000, 1, 1),
            avatar_url=dto.avatar_url,
        )


@pytest.mark.asyncio
async def test_update_user_info_requires_authenticated_identity() -> None:
    controller = UpdateUserInfoController(UpdateUserInfoUseCaseSpy())

    with pytest.raises(AuthError):
        await controller.handle_request(
            HttpRequest(method="PATCH", url="/auth/user-info", body={"name": "Maria"})
        )


@pytest.mark.asyncio
async def test_update_user_info_uses_token_identity_and_only_sent_fields() -> None:
    use_case = UpdateUserInfoUseCaseSpy()
    controller = UpdateUserInfoController(use_case)
    body = UpdateUserInfoValidator(name="Maria")

    response = await controller.handle_request(
        HttpRequest(
            method="PATCH",
            url="/auth/user-info",
            body=body,
            authenticated_user_id="01TESTUSER0000000000000000",
        )
    )

    assert use_case.dto.user_id == UserId("01TESTUSER0000000000000000")
    assert use_case.dto.name == "Maria"
    assert use_case.dto.surname is None
    assert use_case.dto.date_of_birth is None
    assert use_case.dto.avatar_url is None
    assert response.status_code == 200


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"name": None},
        {"unknown": "value"},
        {"date_of_birth": "2026-09-14"},
        {"avatar_url": "not-a-url"},
    ],
)
def test_update_user_info_validator_rejects_invalid_partial_payload(payload) -> None:
    with pytest.raises(ValueError):
        UpdateUserInfoValidator(**payload)
