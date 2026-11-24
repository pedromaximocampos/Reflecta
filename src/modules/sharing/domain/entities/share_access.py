from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ShareAccess:
    id: str
    user_id: str
    analysis_id: str
    expires_at: datetime

