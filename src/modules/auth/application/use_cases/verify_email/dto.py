from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class VerifyEmailOutputDTO:
    success: bool
    message: str