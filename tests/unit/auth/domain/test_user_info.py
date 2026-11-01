from datetime import date

import pytest

from src.modules.auth.domain.exceptions.user_custom_exceptions import InvalidUserInfoError
from tests.support.builders.user_builder import UserBuilder


def test_update_info_changes_only_values_that_were_provided() -> None:
    user = UserBuilder().build()
    original_date_of_birth = user.date_of_birth
    original_avatar_url = user.avatar_url

    user.update_info(
        today=date(2026, 9, 14),
        name="  Maria  ",
        surname="Silva",
    )

    assert user.name == "Maria"
    assert user.surname == "Silva"
    assert user.date_of_birth == original_date_of_birth
    assert user.avatar_url == original_avatar_url


@pytest.mark.parametrize(
    "changes",
    [
        {},
        {"name": "   "},
        {"surname": "   "},
        {"date_of_birth": date(2026, 9, 14)},
        {"date_of_birth": date(2026, 9, 15)},
    ],
)
def test_update_info_rejects_invalid_changes(changes) -> None:
    user = UserBuilder().build()

    with pytest.raises(InvalidUserInfoError):
        user.update_info(today=date(2026, 9, 14), **changes)


def test_replace_and_remove_avatar_manage_durable_reference() -> None:
    user = UserBuilder().with_avatar_url("https://legacy.example/avatar.png").build()

    user.replace_avatar("users/user-id/avatar/avatar.webp")

    assert user.avatar_object_key == "users/user-id/avatar/avatar.webp"
    assert user.avatar_url is None

    user.remove_avatar()

    assert user.avatar_object_key is None
    assert user.avatar_url is None


def test_replace_avatar_rejects_empty_object_key() -> None:
    user = UserBuilder().build()

    with pytest.raises(InvalidUserInfoError):
        user.replace_avatar("   ")
