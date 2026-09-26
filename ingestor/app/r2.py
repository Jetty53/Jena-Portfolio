from pathlib import Path

import boto3
from botocore.config import Config

from app.config import settings


def _client():
    return boto3.client(
        "s3",
        endpoint_url=settings.r2_endpoint,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def key_for(prefix: str, request_id: str, filename: str) -> str:
    safe = Path(filename).name.replace("..", "")
    return f"{prefix}/{request_id}/{safe}"


def put_bytes(key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
    _client().put_object(Bucket=settings.r2_bucket, Key=key, Body=data, ContentType=content_type)


def download(key: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    _client().download_file(settings.r2_bucket, key, str(dest))


def copy_object(src_key: str, dest_key: str) -> None:
    _client().copy_object(
        Bucket=settings.r2_bucket,
        CopySource={"Bucket": settings.r2_bucket, "Key": src_key},
        Key=dest_key,
    )


def delete_object(key: str) -> None:
    _client().delete_object(Bucket=settings.r2_bucket, Key=key)


def promote(src_key: str, dest_prefix: str, request_id: str, filename: str) -> str:
    dest = key_for(dest_prefix, request_id, filename)
    copy_object(src_key, dest)
    delete_object(src_key)
    return dest
