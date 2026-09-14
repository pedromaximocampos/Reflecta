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
        {"avatar_url": "   "},
    ],
)
def test_update_info_rejects_invalid_changes(changes) -> None:
    user = UserBuilder().build()

    with pytest.raises(InvalidUserInfoError):
        user.update_info(today=date(2026, 9, 14), **changes)
