from dataclasses import dataclass



@dataclass(frozen=True)
class SNSSettings:
    aws_region: str
    sns_arn: str
    service: str = "sns"
    aws_profile: str | None = None