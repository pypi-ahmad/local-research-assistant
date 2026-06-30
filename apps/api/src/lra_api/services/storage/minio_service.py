"""MinIO object storage service."""

from __future__ import annotations

from io import BytesIO

import boto3
from botocore.client import BaseClient
from botocore.config import Config

from lra_api.core.config import get_settings


class MinioStorageService:
    """MinIO wrapper for raw and derived artifacts."""

    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        self.client: BaseClient = boto3.client(
            "s3",
            endpoint_url=f"http{'s' if settings.minio_secure else ''}://{settings.minio_endpoint}",
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            config=Config(connect_timeout=2, read_timeout=5, retries={"max_attempts": 2}),
        )

    def ensure_buckets(self) -> None:
        """Create required buckets if they do not exist."""
        existing = {bucket["Name"] for bucket in self.client.list_buckets().get("Buckets", [])}
        for bucket in (self.settings.minio_bucket_raw, self.settings.minio_bucket_derived):
            if bucket not in existing:
                self.client.create_bucket(Bucket=bucket)

    def put_raw_document(self, storage_key: str, data: bytes, content_type: str) -> str:
        """Upload raw document bytes to MinIO bucket."""
        self.client.put_object(
            Bucket=self.settings.minio_bucket_raw,
            Key=storage_key,
            Body=BytesIO(data),
            ContentType=content_type,
        )
        return storage_key

    def get_raw_document(self, storage_key: str) -> bytes:
        """Download raw document bytes by key."""
        response = self.client.get_object(Bucket=self.settings.minio_bucket_raw, Key=storage_key)
        return response["Body"].read()
