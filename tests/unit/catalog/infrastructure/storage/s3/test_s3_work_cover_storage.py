from io import BytesIO
from typing import Any

import pytest

from src.modules.catalog.infrastructure.storage.aws.s3 import S3WorkCoverStorage
from src.modules.catalog.infrastructure.storage.aws.s3.configs.s3_settings import (
    S3Settings,
)


class FakeS3Client:
    def __init__(self) -> None:
        self.put: dict[str, Any] | None = None
        self.deleted: dict[str, Any] | None = None

    def put_object(self, **kwargs: Any) -> dict[str, str]:
        self.put = kwargs
        return {"ETag": '"etag"', "VersionId": "version"}

    def delete_object(self, **kwargs: Any) -> dict:
        self.deleted = kwargs
        return {}

    def generate_presigned_url(self, operation: str, **kwargs: Any) -> str:
        assert operation == "get_object"
        assert kwargs["ExpiresIn"] == 900
        return "https://signed.example.test/cover.webp"


def make_storage(client: FakeS3Client) -> S3WorkCoverStorage:
    return S3WorkCoverStorage(
        client,  # type: ignore[arg-type]
        S3Settings(aws_region="us-east-1", bucket_name="reflecta-works"),
        read_url_ttl_seconds=900,
    )


@pytest.mark.asyncio
async def test_cover_storage_uploads_privately_and_generates_read_url() -> None:
    client = FakeS3Client()
    storage = make_storage(client)
    key = "works/work-id/cover/cover-id.webp"

    stored = await storage.upload(
        object_key=key,
        content=BytesIO(b"webp"),
        content_type="image/webp",
        size_bytes=4,
    )
    url = await storage.create_read_url(object_key=key)

    assert stored.object_key == key
    assert stored.etag == "etag"
    assert client.put is not None
    assert client.put["ServerSideEncryption"] == "AES256"
    assert client.put["CacheControl"].startswith("private")
    assert url == "https://signed.example.test/cover.webp"


@pytest.mark.asyncio
async def test_cover_storage_deletes_only_expected_cover_keys() -> None:
    client = FakeS3Client()
    storage = make_storage(client)
    key = "works/work-id/cover/cover-id.webp"

    await storage.delete(object_key=key)

    assert client.deleted == {"Bucket": "reflecta-works", "Key": key}
    with pytest.raises(ValueError):
        await storage.delete(object_key="works/work-id/source/document.pdf")
