from abc import ABC, abstractmethod
from dto import SignupInputDTO, SignupOutputDTO


class ISignUpUseCase(ABC):

    @abstractmethod
    async def execute(self, signup_input: SignupInputDTO) -> SignupOutputDTO:
        ...