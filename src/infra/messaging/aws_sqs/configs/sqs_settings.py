from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SQSSettings:
    aws_region: str
    queue_url: str
    service: str = "sqs"
    aws_profile: Optional[str] = None
