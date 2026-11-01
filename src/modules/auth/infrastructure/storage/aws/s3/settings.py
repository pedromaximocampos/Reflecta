from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserAvatarS3Settings:
    aws_region: str
    bucket_name: str
    aws_profile: str | None = None
    key_prefix: str = "users/"
