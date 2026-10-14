from dataclasses import dataclass
from enum import Enum


class InboxClaimOutcome(str, Enum):
    CLAIMED = "claimed"
    ALREADY_PROCESSED = "already_processed"
    BUSY = "busy"


@dataclass(frozen=True, slots=True)
class InboxClaim:
    outcome: InboxClaimOutcome
    attempt: int
