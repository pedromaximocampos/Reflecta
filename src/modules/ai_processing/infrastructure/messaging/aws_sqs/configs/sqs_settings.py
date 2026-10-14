from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorkIngestionSQSSettings:
    aws_region: str
    queue_url: str
    aws_profile: str | None = None
    endpoint_url: str | None = None
    service: str = "sqs"
    wait_time_seconds: int = 20
    max_number_of_messages: int = 1
    visibility_timeout_seconds: int = 300
    heartbeat_interval_seconds: int = 120
    retry_base_seconds: int = 60
    retry_max_seconds: int = 900

    def __post_init__(self) -> None:
        if not self.aws_region.strip():
            raise ValueError("AWS SQS region must not be empty.")
        if not self.queue_url.strip():
            raise ValueError("Work ingestion SQS queue URL must not be empty.")
        if not 0 <= self.wait_time_seconds <= 20:
            raise ValueError("SQS wait time must be between 0 and 20 seconds.")
        if not 1 <= self.max_number_of_messages <= 10:
            raise ValueError("SQS batch size must be between 1 and 10.")
        if self.heartbeat_interval_seconds <= 0:
            raise ValueError("SQS heartbeat interval must be positive.")
        if self.visibility_timeout_seconds <= self.heartbeat_interval_seconds:
            raise ValueError(
                "SQS visibility timeout must be longer than the heartbeat interval."
            )
        if self.visibility_timeout_seconds > 43_200:
            raise ValueError("SQS visibility timeout cannot exceed 12 hours.")
        if self.retry_base_seconds <= 0:
            raise ValueError("SQS retry base delay must be positive.")
        if self.retry_max_seconds < self.retry_base_seconds:
            raise ValueError(
                "SQS retry maximum delay cannot be shorter than its base delay."
            )
