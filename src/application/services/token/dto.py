from dataclasses import dataclass
from datetime import datetime

@dataclass(slots=True)
class GeneratedTokenDTO:
    jti: str
    token: str
    expires_at: datetime