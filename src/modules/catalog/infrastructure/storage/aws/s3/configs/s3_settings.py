from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class S3Settings:
    aws_region: str
    bucket_name: str
    aws_profile: str | None = None
    endpoint_url: str | None = None
    key_prefix: str = "works/"
    service: str = "s3"

    def __post_init__(self) -> None:
        if not self.aws_region.strip():
            raise ValueError("AWS S3 region must not be empty.")
        if not self.bucket_name.strip():
            raise ValueError("AWS S3 works bucket must not be empty.")
        if not self.key_prefix or not self.key_prefix.endswith("/"):
            raise ValueError("AWS S3 key prefix must end with '/'.")
