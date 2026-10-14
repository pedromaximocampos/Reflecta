from io import BytesIO
from typing import Any

import pytest
from botocore.exceptions import ClientError

from src.modules.catalog.application.exceptions.work_document_storage_error import (
    WorkDocumentStorageError,
)
from src.modules.catalog.domain.value_objects.work_document_location import (
    WorkDocumentLocation,
)
from src.modules.catalog.infrastructure.storage.aws.s3.configs.s3_settings import (
    S3Settings,
)
from src.modules.catalog.infrastructure.storage.aws.s3.work_document_storage import (
    S3WorkDocumentStorage,
)


class FakeS3Client:
    def __init__(self) -> None:
        self.put_request: dict[str, Any] | None = None
        self.delete_request: dict[str, Any] | None = None
        self.head_request: dict[str, Any] | None = None

    def put_object(self, **kwargs: Any) -> dict[str, str]:
        self.put_request = kwargs
        return {"ETag": '"document-etag"', "VersionId": "document-version"}

    def delete_object(self, **kwargs: Any) -> dict[str, Any]:
        self.delete_request = kwargs
        return {}

    def head_object(self, **kwargs: Any) -> dict[str, Any]:
        self.head_request = kwargs
        return {"ContentLength": 16}


class MissingObjectS3Client(FakeS3Client):
    def head_object(self, **kwargs: Any) -> dict[str, Any]:
        raise ClientError(
            error_response={
                "Error": {"Code": "404", "Message": "Not Found"},
                "ResponseMetadata": {
                    "RequestId": "request-id",
                    "HTTPStatusCode": 404,
                },
            },
            operation_name="HeadObject",
        )


class DeniedS3Client(FakeS3Client):
    def put_object(self, **kwargs: Any) -> dict[str, str]:
        raise ClientError(
            error_response={
                "Error": {"Code": "AccessDenied", "Message": "Denied"},
                "ResponseMetadata": {
                    "RequestId": "request-id",
                    "HTTPStatusCode": 403,
                },
            },
            operation_name="PutObject",
        )


def make_settings() -> S3Settings:
    return S3Settings(
        aws_region="us-east-1",
        bucket_name="reflecta-works-dev",
    )


@pytest.mark.asyncio
async def test_uploads_private_encrypted_work_document() -> None:
    client = FakeS3Client()
    storage = S3WorkDocumentStorage(client, make_settings())  # type: ignore[arg-type]
    content = BytesIO(b"%PDF-test-content")

    stored = await storage.upload(
        object_key="works/work-id/source/document-id.pdf",
        content=content,
        content_type="application/pdf",
        size_bytes=len(content.getvalue()),
    )

    assert client.put_request is not None
    assert client.put_request["Bucket"] == "reflecta-works-dev"
    assert client.put_request["Key"] == "works/work-id/source/document-id.pdf"
    assert client.put_request["ServerSideEncryption"] == "AES256"
    assert client.put_request["ContentType"] == "application/pdf"
    assert stored.location == WorkDocumentLocation(
        bucket="reflecta-works-dev",
        object_key="works/work-id/source/document-id.pdf",
    )
    assert stored.etag == "document-etag"
    assert stored.version_id == "document-version"


@pytest.mark.asyncio
async def test_delete_is_scoped_to_configured_bucket_and_prefix() -> None:
    client = FakeS3Client()
    storage = S3WorkDocumentStorage(client, make_settings())  # type: ignore[arg-type]
    location = WorkDocumentLocation(
        bucket="reflecta-works-dev",
        object_key="works/work-id/source/document-id.pdf",
    )

    await storage.delete(location=location)

    assert client.delete_request == {
        "Bucket": "reflecta-works-dev",
        "Key": "works/work-id/source/document-id.pdf",
    }


@pytest.mark.asyncio
async def test_exists_returns_false_when_s3_reports_not_found() -> None:
    storage = S3WorkDocumentStorage(  # type: ignore[arg-type]
        MissingObjectS3Client(),
        make_settings(),
    )
    location = WorkDocumentLocation(
        bucket="reflecta-works-dev",
        object_key="works/work-id/source/missing.pdf",
    )

    assert await storage.exists(location=location) is False


@pytest.mark.asyncio
async def test_translates_aws_upload_error_without_exposing_details() -> None:
    storage = S3WorkDocumentStorage(  # type: ignore[arg-type]
        DeniedS3Client(),
        make_settings(),
    )

    with pytest.raises(WorkDocumentStorageError) as captured:
        await storage.upload(
            object_key="works/work-id/source/document-id.pdf",
            content=BytesIO(b"%PDF-test-content"),
            content_type="application/pdf",
            size_bytes=17,
        )

    assert captured.value.operation == "upload"
    assert "Denied" not in str(captured.value)


@pytest.mark.asyncio
async def test_rejects_object_key_outside_works_prefix() -> None:
    storage = S3WorkDocumentStorage(  # type: ignore[arg-type]
        FakeS3Client(),
        make_settings(),
    )

    with pytest.raises(ValueError, match="works prefix"):
        await storage.upload(
            object_key="avatars/user-id/avatar.png",
            content=BytesIO(b"avatar"),
            content_type="image/png",
            size_bytes=6,
        )
