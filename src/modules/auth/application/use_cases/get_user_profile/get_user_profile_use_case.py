from src.modules.auth.application.ports.storage import IUserAvatarStorage
from src.modules.auth.application.services.user_avatar_url_resolver import (
    resolve_user_avatar_url,
)
from src.modules.auth.application.use_cases.update_user_info.dto import (
    UpdateUserInfoOutput,
)
from src.modules.auth.domain.exceptions.user_custom_exceptions import UserNotFoundError
from src.modules.auth.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from src.modules.auth.public.user_id import UserId


class GetUserProfileUseCase:
    def __init__(
        self,
        auth_unit_of_work: IAuthUnitOfWork,
        avatar_storage: IUserAvatarStorage,
    ) -> None:
        self.__uow = auth_unit_of_work
        self.__avatar_storage = avatar_storage

    async def execute(self, user_id: UserId) -> UpdateUserInfoOutput:
        async with self.__uow as uow:
            user = await uow.users_repository.find_by_id(user_id)
            if user is None:
                raise UserNotFoundError()

        avatar_url = await resolve_user_avatar_url(user, self.__avatar_storage)
        return UpdateUserInfoOutput(
            user_id=user.id,
            name=user.name,
            surname=user.surname,
            date_of_birth=user.date_of_birth,
            avatar_url=avatar_url,
        )
