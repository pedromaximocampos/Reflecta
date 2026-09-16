from datetime import date, datetime, timezone

from src.modules.auth.domain.entities.user import AuthCredentials, User
from src.modules.auth.domain.value_objects.password_hash import PasswordHash
from src.modules.auth.domain.value_objects.user_role import UserRole
from src.modules.auth.infrastructure.persistence.postgresql.mappers.auth_credentials_mapper import (
    AuthCredentialsMapper,
)
from src.modules.auth.infrastructure.persistence.postgresql.mappers.user_mapper import UserMapper
from src.modules.auth.public.email import Email
from src.modules.auth.public.password_algorithm import PasswordAlgorithm
from src.modules.auth.public.user_id import UserId


def test_user_mapper_preserves_role_and_deleted_at() -> None:
    created_at = datetime(2026, 9, 14, tzinfo=timezone.utc)
    deleted_at = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
    user_id = UserId("01TESTUSER0000000000000000")
    user = User(
        id=user_id,
        email=Email("admin@example.com"),
        username="admin",
        name="Admin",
        surname="Reflecta",
        date_of_birth=date(1990, 1, 1),
        created_at=created_at,
        auth_credentials=AuthCredentials(
            user_id=user_id,
            password=PasswordHash(
                hash="test-hash",
                algorithm=PasswordAlgorithm.ARGON2ID,
                version=1,
            ),
            created_at=created_at,
        ),
        is_email_verified=True,
        role=UserRole.ADMIN,
        deleted_at=deleted_at,
    )
    mapper = UserMapper(AuthCredentialsMapper())

    model = mapper.to_model(user)
    mapped_user = mapper.to_entity(model)

    assert model.role is UserRole.ADMIN
    assert model.deleted_at == deleted_at
    assert mapped_user.role is UserRole.ADMIN
    assert mapped_user.deleted_at == deleted_at
