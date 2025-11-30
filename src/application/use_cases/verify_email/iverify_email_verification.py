from typing import Protocol
from .dto import VerifyEmailOutputDTO

class IVerifyEmailVerification(Protocol):


    async def execute(self, raw_code: str) -> VerifyEmailOutputDTO:
        ...