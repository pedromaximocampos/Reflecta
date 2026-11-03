from io import BytesIO
from typing import Any

import pytest

from src.modules.auth.infrastructure.storage.aws.s3.settings import (
    UserAvatarS3Settings,
)
from src.modules.auth.infrastructure.storage.aws.s3.user_avatar_storage import (
    S3UserAvatarStorage,
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
        return "https://signed.example.test/avatar.webp"


def make_storage(client: FakeS3Client) -> S3UserAvatarStorage:
    return S3UserAvatarStorage(
        client,  # type: ignore[arg-type]
        UserAvatarS3Settings(
            aws_region="us-east-1",
            bucket_name="reflecta-media",
        ),
        read_url_ttl_seconds=900,
    )


@pytest.mark.asyncio
async def test_avatar_storage_uploads_privately_and_generates_read_url() -> None:
    client = FakeS3Client()
    storage = make_storage(client)
    key = "users/user-id/avatar/avatar-id.webp"

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
    assert url == "https://signed.example.test/avatar.webp"


@pytest.mark.asyncio
async def test_avatar_storage_deletes_only_expected_avatar_keys() -> None:
    client = FakeS3Client()
    storage = make_storage(client)
    key = "users/user-id/avatar/avatar-id.webp"

    await storage.delete(object_key=key)

    assert client.deleted == {"Bucket": "reflecta-media", "Key": key}
    with pytest.raises(ValueError):
        await storage.delete(object_key="users/user-id/document.pdf")
