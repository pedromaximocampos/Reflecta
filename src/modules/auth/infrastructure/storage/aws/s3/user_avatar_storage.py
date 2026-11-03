import asyncio
import logging
from typing import Any, BinaryIO

from botocore.exceptions import BotoCoreError, ClientError
from mypy_boto3_s3 import S3Client

from src.modules.auth.application.dto import StoredUserAvatarDTO
from src.modules.auth.application.exceptions import UserAvatarStorageError
from src.modules.auth.application.ports.storage import IUserAvatarStorage

from .settings import UserAvatarS3Settings


_LOGGER = logging.getLogger(__name__)


class S3UserAvatarStorage(IUserAvatarStorage):
    def __init__(
        self,
        client: S3Client,
        settings: UserAvatarS3Settings,
        read_url_ttl_seconds: int,
    ) -> None:
        if read_url_ttl_seconds <= 0:
            raise ValueError("User avatar read URL TTL must be greater than zero.")
        self.__client = client
        self.__settings = settings
        self.__read_url_ttl_seconds = read_url_ttl_seconds

    async def upload(
        self,
        *,
        object_key: str,
        content: BinaryIO,
        content_type: str,
        size_bytes: int,
    ) -> StoredUserAvatarDTO:
        self.__validate_object_key(object_key)
        if content_type != "image/webp" or size_bytes <= 0:
            raise ValueError("Normalized user avatar metadata is invalid.")
        try:
            response = await asyncio.to_thread(
                self.__put_object,
                object_key,
                content,
                content_type,
                size_bytes,
            )
        except (BotoCoreError, ClientError) as error:
            self.__log_aws_error("upload", error)
            raise UserAvatarStorageError("upload") from error

        return StoredUserAvatarDTO(
            object_key=object_key,
            content_type=content_type,
            size_bytes=size_bytes,
            etag=self.__normalize_etag(response.get("ETag")),
            version_id=response.get("VersionId"),
        )

    async def delete(self, *, object_key: str) -> None:
        self.__validate_object_key(object_key)
        try:
            await asyncio.to_thread(
                self.__client.delete_object,
                Bucket=self.__settings.bucket_name,
                Key=object_key,
            )
        except (BotoCoreError, ClientError) as error:
            self.__log_aws_error("delete", error)
            raise UserAvatarStorageError("delete") from error

    async def create_read_url(self, *, object_key: str) -> str:
        self.__validate_object_key(object_key)
        try:
            return await asyncio.to_thread(
                self.__client.generate_presigned_url,
                "get_object",
                Params={
                    "Bucket": self.__settings.bucket_name,
                    "Key": object_key,
                },
                ExpiresIn=self.__read_url_ttl_seconds,
            )
        except (BotoCoreError, ClientError) as error:
            self.__log_aws_error("create_read_url", error)
            raise UserAvatarStorageError("create_read_url") from error

    def __put_object(
        self,
        object_key: str,
        content: BinaryIO,
        content_type: str,
        size_bytes: int,
    ) -> dict[str, Any]:
        if content.seekable():
            content.seek(0)
        return self.__client.put_object(
            Bucket=self.__settings.bucket_name,
            Key=object_key,
            Body=content,
            ContentType=content_type,
            ContentLength=size_bytes,
            CacheControl="private, max-age=900",
            ServerSideEncryption="AES256",
        )

    def __validate_object_key(self, object_key: str) -> None:
        if (
            not object_key.startswith(self.__settings.key_prefix)
            or "/avatar/" not in object_key
            or not object_key.endswith(".webp")
        ):
            raise ValueError("User avatar object key is outside the expected prefix.")

    @staticmethod
    def __normalize_etag(etag: Any) -> str | None:
        if not isinstance(etag, str):
            return None
        return etag.strip('"') or None

    @staticmethod
    def __log_aws_error(operation: str, error: Exception) -> None:
        if isinstance(error, ClientError):
            metadata = error.response.get("ResponseMetadata", {})
            _LOGGER.error(
                "Amazon S3 user avatar operation failed: operation=%s "
                "error_code=%s http_status=%s request_id=%s",
                operation,
                error.response.get("Error", {}).get("Code", "Unknown"),
                metadata.get("HTTPStatusCode", "Unknown"),
                metadata.get("RequestId", "Unknown"),
            )
            return
        _LOGGER.error(
            "Amazon S3 user avatar client failed: operation=%s error_type=%s",
            operation,
            type(error).__name__,
        )
