from datetime import date, datetime, timezone

from src.modules.auth.domain.entities.user import AuthCredentials, User
from src.modules.auth.domain.value_objects.password_hash import PasswordHash
from src.modules.auth.domain.value_objects.user_role import UserRole
from src.modules.auth.public.email import Email
from src.modules.auth.public.password_algorithm import PasswordAlgorithm
from src.modules.auth.public.user_id import UserId


def make_user(**overrides) -> User:
    now = datetime(2026, 9, 14, tzinfo=timezone.utc)
    user_id = UserId("01TESTUSER0000000000000000")
    values = {
        "id": user_id,
        "email": Email("user@example.com"),
        "username": "test-user",
        "name": "Test",
        "surname": "User",
        "date_of_birth": date(2000, 1, 1),
        "created_at": now,
        "auth_credentials": AuthCredentials(
            user_id=user_id,
            password=PasswordHash(
                hash="test-hash",
                algorithm=PasswordAlgorithm.ARGON2ID,
                version=1,
            ),
            created_at=now,
        ),
        "is_email_verified": True,
    }
    values.update(overrides)
    return User(**values)


def test_new_user_has_user_role_and_is_active_by_default() -> None:
    user = make_user()

    assert user.role is UserRole.USER
    assert user.is_admin is False
    assert user.is_deleted is False


def test_admin_and_soft_deleted_states_are_derived_from_domain_fields() -> None:
    deleted_at = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    user = make_user(role=UserRole.ADMIN, deleted_at=deleted_at)

    assert user.is_admin is True
    assert user.is_deleted is True
    assert user.deleted_at == deleted_at
