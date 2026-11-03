import logging

from src.modules.auth.application.ports.media import IUserAvatarProcessor
from src.modules.auth.application.ports.storage import IUserAvatarStorage
from src.modules.auth.application.services.user_avatar_url_resolver import (
    resolve_user_avatar_url,
)
from src.modules.auth.application.use_cases.update_user_avatar.dto import (
    RemoveUserAvatarInputDTO,
    ReplaceUserAvatarInputDTO,
)
from src.modules.auth.application.use_cases.update_user_info.dto import (
    UpdateUserInfoOutput,
)
from src.modules.auth.domain.entities.user import User
from src.modules.auth.domain.exceptions.user_custom_exceptions import UserNotFoundError
from src.modules.auth.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from src.shared.domain.ports.system.iulid_generator import IULIDGenerator


_LOGGER = logging.getLogger(__name__)


def _profile_output(user: User, avatar_url: str | None) -> UpdateUserInfoOutput:
    return UpdateUserInfoOutput(
        user_id=user.id,
        name=user.name,
        surname=user.surname,
        date_of_birth=user.date_of_birth,
        avatar_url=avatar_url,
    )


class ReplaceUserAvatarUseCase:
    def __init__(
        self,
        auth_unit_of_work: IAuthUnitOfWork,
        avatar_processor: IUserAvatarProcessor,
        avatar_storage: IUserAvatarStorage,
        ulid_generator: IULIDGenerator,
    ) -> None:
        self.__uow = auth_unit_of_work
        self.__avatar_processor = avatar_processor
        self.__avatar_storage = avatar_storage
        self.__ulid_generator = ulid_generator

    async def execute(
        self,
        avatar_input: ReplaceUserAvatarInputDTO,
    ) -> UpdateUserInfoOutput:
        await self.__ensure_user_exists(avatar_input.user_id)
        processed = await self.__avatar_processor.process(
            content=avatar_input.content,
            declared_content_type=avatar_input.content_type,
            declared_size_bytes=avatar_input.size_bytes,
        )
        object_key = (
            f"users/{avatar_input.user_id.value}/avatar/"
            f"{self.__ulid_generator.generate_ulid()}.{processed.extension}"
        )
        stored = await self.__avatar_storage.upload(
            object_key=object_key,
            content=processed.content,
            content_type=processed.content_type,
            size_bytes=processed.size_bytes,
        )

        database_committed = False
        try:
            avatar_url = await self.__avatar_storage.create_read_url(
                object_key=stored.object_key
            )
            async with self.__uow as uow:
                user = await uow.users_repository.find_by_id(avatar_input.user_id)
                if user is None:
                    raise UserNotFoundError()
                previous_object_key = user.avatar_object_key
                user.replace_avatar(stored.object_key)
                await uow.users_repository.update_user_avatar(user)
                await uow.commit()
                database_committed = True
        except Exception:
            if not database_committed:
                await self.__delete_safely(stored.object_key, compensation=True)
            raise

        if previous_object_key and previous_object_key != stored.object_key:
            await self.__delete_safely(previous_object_key)
        return _profile_output(user, avatar_url)

    async def __ensure_user_exists(self, user_id) -> None:
        async with self.__uow as uow:
            if await uow.users_repository.find_by_id(user_id) is None:
                raise UserNotFoundError()

    async def __delete_safely(
        self,
        object_key: str,
        *,
        compensation: bool = False,
    ) -> None:
        try:
            await self.__avatar_storage.delete(object_key=object_key)
        except Exception:
            _LOGGER.exception(
                "Failed to delete user avatar object: object_key=%s compensation=%s",
                object_key,
                compensation,
            )


class RemoveUserAvatarUseCase:
    def __init__(
        self,
        auth_unit_of_work: IAuthUnitOfWork,
        avatar_storage: IUserAvatarStorage,
    ) -> None:
        self.__uow = auth_unit_of_work
        self.__avatar_storage = avatar_storage

    async def execute(
        self,
        avatar_input: RemoveUserAvatarInputDTO,
    ) -> UpdateUserInfoOutput:
        async with self.__uow as uow:
            user = await uow.users_repository.find_by_id(avatar_input.user_id)
            if user is None:
                raise UserNotFoundError()
            previous_object_key = user.avatar_object_key
            user.remove_avatar()
            await uow.users_repository.update_user_avatar(user)
            await uow.commit()

        if previous_object_key:
            try:
                await self.__avatar_storage.delete(object_key=previous_object_key)
            except Exception:
                _LOGGER.exception(
                    "Failed to delete removed user avatar object: object_key=%s",
                    previous_object_key,
                )
        avatar_url = await resolve_user_avatar_url(user, self.__avatar_storage)
        return _profile_output(user, avatar_url)
