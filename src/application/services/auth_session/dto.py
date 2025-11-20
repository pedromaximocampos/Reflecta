from dataclasses import dataclass
from datetime import datetime

@dataclass(slots=True)
class AuthSessionResultDTO:
    session_id: str
    access_token: str
    refresh_token: str

