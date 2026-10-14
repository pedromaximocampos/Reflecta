from io import BytesIO
from typing import Any

import pytest

from src.modules.ai_processing.application.dto import StorageObjectLocationDTO
from src.modules.ai_processing.application.exceptions import (
    WorkIngestionProcessingStorageError,
)
from src.modules.ai_processing.infrastructure.storage.aws.s3.configs import S3Settings
from src.modules.ai_processing.infrastructure.storage.aws.s3.work_ingestion_storage import (
    S3WorkIngestionStorage,
)


class FakeS3Client:
    def __init__(self) -> None:
        self.objects: dict[tuple[str, str], tuple[bytes, dict[str, str]]] = {}
        self.download_request: tuple[str, str] | None = None

    def download_fileobj(
        self,
        bucket: str,
        key: str,
        destination: BytesIO,
    ) -> None:
        self.download_request = (bucket, key)
        destination.write(self.objects[(bucket, key)][0])

    def put_object(self, **kwargs: Any) -> dict[str, str]:
        self.objects[(kwargs["Bucket"], kwargs["Key"])] = (
            kwargs["Body"],
            kwargs.get("Metadata", {}),
        )
        return {"ETag": '"normalized-etag"', "VersionId": "version-1"}

    def get_object(self, **kwargs: Any) -> dict[str, Any]:
        content, metadata = self.objects[(kwargs["Bucket"], kwargs["Key"])]
        return {"Body": BytesIO(content), "Metadata": metadata}

    def delete_object(self, **kwargs: Any) -> dict[str, Any]:
        self.objects.pop((kwargs["Bucket"], kwargs["Key"]), None)
        return {}


def make_storage(client: FakeS3Client) -> S3WorkIngestionStorage:
    return S3WorkIngestionStorage(  # type: ignore[arg-type]
        client,
        S3Settings(
            aws_region="us-east-1",
            bucket_name="reflecta-works-dev",
        ),
    )


@pytest.mark.asyncio
async def test_saves_and_loads_normalized_text_with_hash() -> None:
    client = FakeS3Client()
    storage = make_storage(client)
    key = "works/work-id/ingestions/ingestion-id/normalized-text.txt"

    stored = await storage.save_normalized_text(
        object_key=key,
        text="Texto normalizado entre duas paginas.",
        normalizer_version="v1",
    )
    loaded = await storage.load_normalized_text(
        location=stored.location,
        expected_sha256=stored.content_sha256,
    )

    assert loaded == "Texto normalizado entre duas paginas."
    assert stored.location.object_key == key
    assert stored.etag == "normalized-etag"


@pytest.mark.asyncio
async def test_downloads_source_document_to_stream() -> None:
    client = FakeS3Client()
    client.objects[("reflecta-works-dev", "works/work/source/book.pdf")] = (
        b"%PDF-book",
        {},
    )
    storage = make_storage(client)
    destination = BytesIO()

    await storage.download_document(
        location=StorageObjectLocationDTO(
            bucket="reflecta-works-dev",
            object_key="works/work/source/book.pdf",
        ),
        destination=destination,
    )

    assert destination.read() == b"%PDF-book"


@pytest.mark.asyncio
async def test_rejects_normalized_text_with_unexpected_hash() -> None:
    client = FakeS3Client()
    storage = make_storage(client)
    stored = await storage.save_normalized_text(
        object_key="works/work/ingestions/ingestion/normalized-text.txt",
        text="Texto normalizado.",
        normalizer_version="v1",
    )

    with pytest.raises(WorkIngestionProcessingStorageError):
        await storage.load_normalized_text(
            location=stored.location,
            expected_sha256="0" * 64,
        )
