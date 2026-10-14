import asyncio
import hashlib
import logging
from typing import Any, BinaryIO

from botocore.exceptions import BotoCoreError, ClientError
from mypy_boto3_s3 import S3Client

from src.modules.ai_processing.application.dto import (
    StorageObjectLocationDTO,
    StoredNormalizedTextDTO,
)
from src.modules.ai_processing.application.exceptions import (
    WorkIngestionProcessingStorageError,
)
from src.modules.ai_processing.application.ports.storage import (
    IWorkIngestionStorage,
)
from src.modules.ai_processing.infrastructure.storage.aws.s3.configs import S3Settings


_LOGGER = logging.getLogger(__name__)


class S3WorkIngestionStorage(IWorkIngestionStorage):
    def __init__(self, client: S3Client, settings: S3Settings) -> None:
        self.__client = client
        self.__settings = settings

    async def download_document(
        self,
        *,
        location: StorageObjectLocationDTO,
        destination: BinaryIO,
    ) -> None:
        self.__validate_location(location)
        try:
            await asyncio.to_thread(
                self.__client.download_fileobj,
                location.bucket,
                location.object_key,
                destination,
            )
            if destination.seekable():
                destination.seek(0)
        except (BotoCoreError, ClientError, OSError) as error:
            self.__log_storage_error("download_document", error)
            raise WorkIngestionProcessingStorageError("download_document") from error

    async def save_normalized_text(
        self,
        *,
        object_key: str,
        text: str,
        normalizer_version: str,
    ) -> StoredNormalizedTextDTO:
        self.__validate_object_key(object_key)
        if not text:
            raise ValueError("Normalized text must not be empty.")
        if not normalizer_version.strip():
            raise ValueError("Normalizer version must not be empty.")

        content = text.encode("utf-8")
        content_sha256 = hashlib.sha256(content).hexdigest()
        try:
            response = await asyncio.to_thread(
                self.__client.put_object,
                Bucket=self.__settings.bucket_name,
                Key=object_key,
                Body=content,
                ContentLength=len(content),
                ContentType="text/plain; charset=utf-8",
                ServerSideEncryption="AES256",
                Metadata={
                    "sha256": content_sha256,
                    "normalizer-version": normalizer_version,
                },
            )
        except (BotoCoreError, ClientError) as error:
            self.__log_storage_error("save_normalized_text", error)
            raise WorkIngestionProcessingStorageError("save_normalized_text") from error

        return StoredNormalizedTextDTO(
            location=StorageObjectLocationDTO(
                bucket=self.__settings.bucket_name,
                object_key=object_key,
            ),
            content_sha256=content_sha256,
            size_bytes=len(content),
            etag=self.__normalize_etag(response.get("ETag")),
            version_id=response.get("VersionId"),
        )

    async def load_normalized_text(
        self,
        *,
        location: StorageObjectLocationDTO,
        expected_sha256: str | None = None,
    ) -> str:
        self.__validate_location(location)
        try:
            content, metadata = await asyncio.to_thread(
                self.__read_object,
                location,
            )
            text = content.decode("utf-8")
        except (BotoCoreError, ClientError, UnicodeDecodeError) as error:
            self.__log_storage_error("load_normalized_text", error)
            raise WorkIngestionProcessingStorageError("load_normalized_text") from error

        actual_sha256 = hashlib.sha256(content).hexdigest()
        stored_sha256 = metadata.get("sha256")
        if stored_sha256 and stored_sha256 != actual_sha256:
            raise WorkIngestionProcessingStorageError("verify_normalized_text_hash")
        if expected_sha256 and expected_sha256 != actual_sha256:
            raise WorkIngestionProcessingStorageError("verify_normalized_text_hash")
        return text

    async def delete(self, *, location: StorageObjectLocationDTO) -> None:
        self.__validate_location(location)
        try:
            await asyncio.to_thread(
                self.__client.delete_object,
                Bucket=location.bucket,
                Key=location.object_key,
            )
        except (BotoCoreError, ClientError) as error:
            self.__log_storage_error("delete", error)
            raise WorkIngestionProcessingStorageError("delete") from error

    def __read_object(
        self,
        location: StorageObjectLocationDTO,
    ) -> tuple[bytes, dict[str, str]]:
        response = self.__client.get_object(
            Bucket=location.bucket,
            Key=location.object_key,
        )
        body = response["Body"]
        try:
            content = body.read()
        finally:
            body.close()
        return content, response.get("Metadata", {})

    def __validate_location(self, location: StorageObjectLocationDTO) -> None:
        if location.bucket != self.__settings.bucket_name:
            raise ValueError("Storage object belongs to an unexpected bucket.")
        self.__validate_object_key(location.object_key)

    def __validate_object_key(self, object_key: str) -> None:
        if not object_key.startswith(self.__settings.key_prefix):
            raise ValueError("Storage object key must use the configured works prefix.")

    @staticmethod
    def __normalize_etag(etag: Any) -> str | None:
        if not isinstance(etag, str):
            return None
        return etag.strip('"') or None

    @staticmethod
    def __log_storage_error(operation: str, error: Exception) -> None:
        if isinstance(error, ClientError):
            metadata = error.response.get("ResponseMetadata", {})
            _LOGGER.error(
                "Amazon S3 operation failed: operation=%s error_code=%s "
                "http_status=%s request_id=%s",
                operation,
                error.response.get("Error", {}).get("Code", "Unknown"),
                metadata.get("HTTPStatusCode", "Unknown"),
                metadata.get("RequestId", "Unknown"),
            )
            return
        _LOGGER.error(
            "Amazon S3 client failed: operation=%s error_type=%s",
            operation,
            type(error).__name__,
        )
