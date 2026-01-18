import os
from io import BytesIO
from datetime import timedelta
from typing import Optional

from minio import Minio

# Internal endpoint used inside Docker network (api container -> minio container)
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")

# Public endpoint that your Mac browser can reach
PUBLIC_MINIO_HOST = os.getenv("PUBLIC_MINIO_HOST", "localhost:9000")

MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")

# Force region so the SDK doesn't try to call /?location= on the PUBLIC host
MINIO_REGION = os.getenv("MINIO_REGION", "us-east-1")

BUCKET_ORIGINAL = "images-original"
BUCKET_PROCESSED = "images-processed"

# Used for upload/download inside Docker network
internal_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
    region=MINIO_REGION,
)

# Used ONLY for generating presigned URLs (must match browser-reachable host)
# region is important to avoid network call to PUBLIC_MINIO_HOST for location
public_client = Minio(
    PUBLIC_MINIO_HOST,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
    region=MINIO_REGION,
)

def put_original(object_key: str, data: bytes, content_type: Optional[str]):
    internal_client.put_object(
        BUCKET_ORIGINAL,
        object_key,
        BytesIO(data),
        length=len(data),
        content_type=content_type or "application/octet-stream",
    )

def presigned_original_url(object_key: str, expiry_seconds: int = 3600) -> str:
    return public_client.presigned_get_object(
        BUCKET_ORIGINAL,
        object_key,
        expires=timedelta(seconds=expiry_seconds),
    )

def presigned_thumbnail_url(object_key: str, expiry_seconds: int = 3600) -> str:
    return public_client.presigned_get_object(
        BUCKET_PROCESSED,
        object_key,
        expires=timedelta(seconds=expiry_seconds),
    )
