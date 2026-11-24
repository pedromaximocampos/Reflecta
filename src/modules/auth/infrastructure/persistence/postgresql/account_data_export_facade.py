from sqlalchemy import select

from src.modules.auth.application.exceptions import UserAvatarStorageError
from src.modules.auth.application.ports.storage import IUserAvatarStorage
from src.modules.auth.infrastructure.persistence.postgresql.models.users_model import (
    UserModel,
)
from src.modules.auth.public.data_export import (
    AccountDataExport,
    AccountDataExportUnavailable,
    ExportedAvatar,
    IAccountDataExportFacade,
)


class PostgresAccountDataExportFacade(IAccountDataExportFacade):
    def __init__(self, db, avatar_storage: IUserAvatarStorage) -> None:
        self._db = db
        self._avatar_storage = avatar_storage

    async def export_account(self, user_id: str) -> AccountDataExport:
        async with self._db.session() as session:
            user = await session.scalar(
                select(UserModel).where(
                    UserModel.id == user_id,
                    UserModel.deleted_at.is_(None),
                )
            )
        if user is None:
            raise AccountDataExportUnavailable()

        profile = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "name": user.name,
            "surname": user.surname,
            "date_of_birth": user.date_of_birth.isoformat(),
            "created_at": user.created_at.isoformat(),
            "role": user.role.value,
            "is_email_verified": user.is_email_verified,
            "email_verified_at": (
                user.email_verified_at.isoformat() if user.email_verified_at else None
            ),
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "account_status": "active",
        }

        avatar = None
        warnings: list[str] = []
        if user.avatar_object_key:
            try:
                downloaded = await self._avatar_storage.download(
                    object_key=user.avatar_object_key
                )
                avatar = ExportedAvatar(
                    filename="foto-perfil.webp",
                    content_type=downloaded.content_type,
                    content=downloaded.content,
                )
            except (UserAvatarStorageError, ValueError):
                warnings.append(
                    "A foto de perfil não pôde ser incluída nesta exportação."
                )

        return AccountDataExport(
            profile=profile,
            avatar=avatar,
            warnings=tuple(warnings),
        )
