import asyncio
import logging
from typing import Any, BinaryIO

from botocore.exceptions import BotoCoreError, ClientError
from mypy_boto3_s3 import S3Client

from src.modules.catalog.application.dto.stored_work_document import (
    StoredWorkDocumentDTO,
)
from src.modules.catalog.application.exceptions.work_document_storage_error import (
    WorkDocumentStorageError,
)
from src.modules.catalog.application.ports.storage.iwork_document_storage import (
    IWorkDocumentStorage,
)
from src.modules.catalog.domain.value_objects.work_document_location import (
    WorkDocumentLocation,
)
from src.modules.catalog.infrastructure.storage.aws.s3.configs.s3_settings import (
    S3Settings,
)


_LOGGER = logging.getLogger(__name__)


class S3WorkDocumentStorage(IWorkDocumentStorage):
    _NOT_FOUND_ERROR_CODES = frozenset({"404", "NoSuchKey", "NotFound"})

    def __init__(self, client: S3Client, settings: S3Settings) -> None:
        self.__client = client
        self.__settings = settings

    async def upload(
        self,
        *,
        object_key: str,
        content: BinaryIO,
        content_type: str,
        size_bytes: int,
    ) -> StoredWorkDocumentDTO:
        self.__validate_object_key(object_key)
        if not content_type.strip():
            raise ValueError("Work document content type must not be empty.")
        if size_bytes <= 0:
            raise ValueError("Work document size must be greater than zero.")

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
            raise WorkDocumentStorageError("upload") from error

        return StoredWorkDocumentDTO(
            location=WorkDocumentLocation(
                bucket=self.__settings.bucket_name,
                object_key=object_key,
            ),
            content_type=content_type,
            size_bytes=size_bytes,
            etag=self.__normalize_etag(response.get("ETag")),
            version_id=response.get("VersionId"),
        )

    async def delete(self, *, location: WorkDocumentLocation) -> None:
        self.__validate_location(location)
        try:
            await asyncio.to_thread(
                self.__client.delete_object,
                Bucket=location.bucket,
                Key=location.object_key,
            )
        except (BotoCoreError, ClientError) as error:
            self.__log_aws_error("delete", error)
            raise WorkDocumentStorageError("delete") from error

    async def exists(self, *, location: WorkDocumentLocation) -> bool:
        self.__validate_location(location)
        try:
            await asyncio.to_thread(
                self.__client.head_object,
                Bucket=location.bucket,
                Key=location.object_key,
            )
            return True
        except ClientError as error:
            error_code = str(error.response.get("Error", {}).get("Code", ""))
            if error_code in self._NOT_FOUND_ERROR_CODES:
                return False
            self.__log_aws_error("exists", error)
            raise WorkDocumentStorageError("exists") from error
        except BotoCoreError as error:
            self.__log_aws_error("exists", error)
            raise WorkDocumentStorageError("exists") from error

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
            ServerSideEncryption="AES256",
        )

    def __validate_location(self, location: WorkDocumentLocation) -> None:
        if location.bucket != self.__settings.bucket_name:
            raise ValueError("Work document belongs to an unexpected bucket.")
        self.__validate_object_key(location.object_key)

    def __validate_object_key(self, object_key: str) -> None:
        if not object_key.startswith(self.__settings.key_prefix):
            raise ValueError(
                "Work document object key must use the configured works prefix."
            )

    @staticmethod
    def __normalize_etag(etag: Any) -> str | None:
        if not isinstance(etag, str):
            return None
        return etag.strip('"') or None

    @staticmethod
    def __log_aws_error(operation: str, error: Exception) -> None:
        if isinstance(error, ClientError):
            error_code = error.response.get("Error", {}).get("Code", "Unknown")
            metadata = error.response.get("ResponseMetadata", {})
            _LOGGER.error(
                "Amazon S3 operation failed: operation=%s error_code=%s "
                "http_status=%s request_id=%s",
                operation,
                error_code,
                metadata.get("HTTPStatusCode", "Unknown"),
                metadata.get("RequestId", "Unknown"),
            )
            return

        _LOGGER.error(
            "Amazon S3 client failed: operation=%s error_type=%s",
            operation,
            type(error).__name__,
        )
