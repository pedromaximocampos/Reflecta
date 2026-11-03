import boto3
from mypy_boto3_s3 import S3Client

from .settings import UserAvatarS3Settings


def make_user_avatar_s3_client(settings: UserAvatarS3Settings) -> S3Client:
    if settings.aws_profile:
        session = boto3.Session(
            profile_name=settings.aws_profile,
            region_name=settings.aws_region,
        )
        return session.client("s3")
    return boto3.client("s3", region_name=settings.aws_region)
