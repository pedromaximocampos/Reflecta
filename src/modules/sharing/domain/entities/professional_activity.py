from dataclasses import dataclass, replace
from datetime import date, datetime

from src.modules.sharing.domain.value_objects import ActivityKind, ActivityStatus


@dataclass(frozen=True, slots=True)
class ProfessionalActivity:
    id: str
    share_id: str
    user_id: str
    kind: ActivityKind
    title: str
    description: str
    status: ActivityStatus
    created_at: datetime
    due_date: date | None = None
    completed_at: datetime | None = None

    def complete(self, completed_at: datetime) -> "ProfessionalActivity":
        if self.status is ActivityStatus.COMPLETED:
            return self
        return replace(
            self,
            status=ActivityStatus.COMPLETED,
            completed_at=completed_at,
        )

