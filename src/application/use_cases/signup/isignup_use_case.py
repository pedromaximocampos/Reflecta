from typing import Protocol
from .dto import SignupInputDTO, SignupOutputDTO


class ISignUpUseCase(Protocol):

    async def execute(self, signup_input: SignupInputDTO) -> SignupOutputDTO:
        ...