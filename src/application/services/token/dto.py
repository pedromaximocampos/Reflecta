from dataclasses import dataclass
from datetime import datetime

from src.domain.value_objects.token_jti import TokenJti


@dataclass(slots=True)
class GeneratedTokenDTO:
    jti: TokenJti
    token: str
    expires_at: datetime