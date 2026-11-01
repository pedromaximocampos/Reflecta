from src.modules.auth.application.use_cases.update_user_info.dto import (
    UpdateUserInfoInput,
    UpdateUserInfoOutput,
)
from src.modules.auth.application.use_cases.update_user_info.iupdate_user_info_use_case import (
    IUpdateUserInfoUseCase,
)
from src.modules.auth.domain.exceptions.user_custom_exceptions import UserNotFoundError
from src.modules.auth.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from src.modules.auth.application.ports.storage import IUserAvatarStorage
from src.modules.auth.application.services.user_avatar_url_resolver import (
    resolve_user_avatar_url,
)
from src.shared.domain.ports.system.iclock import IClock


class UpdateUserInfoUseCaseImpl(IUpdateUserInfoUseCase):
    def __init__(
        self,
        auth_unit_of_work: IAuthUnitOfWork,
        system_clock: IClock,
        avatar_storage: IUserAvatarStorage,
    ) -> None:
        self.__uow = auth_unit_of_work
        self.__clock = system_clock
        self.__avatar_storage = avatar_storage

    async def execute(self, dto: UpdateUserInfoInput) -> UpdateUserInfoOutput:
        async with self.__uow as uow:
            user = await uow.users_repository.find_by_id(dto.user_id)
            if user is None:
                raise UserNotFoundError()

            user.update_info(
                today=self.__clock.now().date(),
                name=dto.name,
                surname=dto.surname,
                date_of_birth=dto.date_of_birth,
            )
            fields_to_update = frozenset(
                field_name
                for field_name, value in (
                    ("name", dto.name),
                    ("surname", dto.surname),
                    ("date_of_birth", dto.date_of_birth),
                )
                if value is not None
            )
            await uow.users_repository.update_user_info(user, fields_to_update)
            await uow.commit()

            avatar_url = await resolve_user_avatar_url(user, self.__avatar_storage)

            return UpdateUserInfoOutput(
                user_id=user.id,
                name=user.name,
                surname=user.surname,
                date_of_birth=user.date_of_birth,
                avatar_url=avatar_url,
            )
