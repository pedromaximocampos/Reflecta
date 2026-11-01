from src.modules.auth.application.ports.storage import IUserAvatarStorage
from src.modules.auth.infrastructure.storage.aws.s3.client import (
    make_user_avatar_s3_client,
)
from src.modules.auth.infrastructure.storage.aws.s3.settings import (
    UserAvatarS3Settings,
)
from src.modules.auth.infrastructure.storage.aws.s3.user_avatar_storage import (
    S3UserAvatarStorage,
)
from src.shared.config.settings import get_settings


def get_user_avatar_storage() -> IUserAvatarStorage:
    application_settings = get_settings()
    bucket_name = (
        application_settings.AWS_S3_MEDIA_BUCKET
        or application_settings.AWS_S3_WORKS_BUCKET
    )
    s3_settings = UserAvatarS3Settings(
        aws_region=application_settings.AWS_S3_REGION,
        bucket_name=bucket_name,
        aws_profile=application_settings.AWS_PROFILE,
    )
    return S3UserAvatarStorage(
        client=make_user_avatar_s3_client(s3_settings),
        settings=s3_settings,
        read_url_ttl_seconds=(
            application_settings.AWS_S3_USER_AVATAR_READ_URL_TTL_SECONDS
        ),
    )
