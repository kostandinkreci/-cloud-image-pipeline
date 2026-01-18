import os
from io import BytesIO
from minio import Minio

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")

BUCKET_ORIGINAL = "images-original"
BUCKET_PROCESSED = "images-processed"

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
)

def get_original(object_key: str) -> bytes:
    response = client.get_object(BUCKET_ORIGINAL, object_key)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()

def put_thumbnail(object_key: str, data: bytes):
    client.put_object(
        BUCKET_PROCESSED,
        object_key,
        BytesIO(data),
        length=len(data),
        content_type="image/jpeg",
    )
