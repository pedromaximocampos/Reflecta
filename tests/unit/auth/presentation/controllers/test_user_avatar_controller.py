from datetime import date
from io import BytesIO

import pytest

from src.modules.auth.application.use_cases.update_user_info.dto import (
    UpdateUserInfoOutput,
)
from src.modules.auth.presentation.controllers.user_avatar_controller import (
    GetUserProfileController,
    RemoveUserAvatarController,
    ReplaceUserAvatarController,
)
from src.modules.auth.presentation.validators.user_avatar import (
    UserAvatarUploadValidator,
)
from src.modules.auth.public.user_id import UserId
from src.shared.presentation.http_types import HttpRequest


class UseCaseSpy:
    def __init__(self) -> None:
        self.argument = None

    async def execute(self, argument):
        self.argument = argument
        user_id = argument if isinstance(argument, UserId) else argument.user_id
        return UpdateUserInfoOutput(
            user_id=user_id,
            name="Maria",
            surname="Silva",
            date_of_birth=date(2000, 1, 1),
            avatar_url="https://signed.example/avatar.webp",
        )


@pytest.mark.asyncio
async def test_avatar_controllers_use_authenticated_identity() -> None:
    user_id = "01TESTUSER0000000000000000"
    replace_spy = UseCaseSpy()
    replace = await ReplaceUserAvatarController(replace_spy).handle_request(
        HttpRequest(
            method="PUT",
            url="/auth/user-info/avatar",
            body={
                "content": BytesIO(b"image"),
                "content_type": "image/png",
                "size_bytes": 5,
            },
            authenticated_user_id=user_id,
        )
    )
    remove_spy = UseCaseSpy()
    remove = await RemoveUserAvatarController(remove_spy).handle_request(
        HttpRequest(
            method="DELETE",
            url="/auth/user-info/avatar",
            authenticated_user_id=user_id,
        )
    )
    get_spy = UseCaseSpy()
    profile = await GetUserProfileController(get_spy).handle_request(
        HttpRequest(
            method="GET",
            url="/auth/user-info",
            authenticated_user_id=user_id,
        )
    )

    assert replace_spy.argument.user_id == UserId(user_id)
    assert remove_spy.argument.user_id == UserId(user_id)
    assert get_spy.argument == UserId(user_id)
    assert replace.status_code == remove.status_code == profile.status_code == 200


def test_avatar_validator_accepts_only_expected_metadata() -> None:
    valid = UserAvatarUploadValidator(
        filename="profile.png",
        content_type="image/png",
        size_bytes=1024,
    )

    assert valid.filename == "profile.png"
    with pytest.raises(ValueError):
        UserAvatarUploadValidator(
            filename="profile.svg",
            content_type="image/svg+xml",
            size_bytes=1024,
        )
