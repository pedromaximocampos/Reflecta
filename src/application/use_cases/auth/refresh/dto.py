from dataclasses import dataclass
from src.domain.entities.user import User


@dataclass(slots=True)
class RefreshResultDTO:
    access_token: str
    refresh_token: str
    user: User