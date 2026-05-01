from minio import Minio
from settings import Settings as ENV
import logging

logger = logging.getLogger(__name__)

_minio_client: Minio | None = None


def get_minio_client() -> Minio:
    global _minio_client
    if _minio_client is None:
        endpoint = ENV.MINIO_ENDPOINT
        access_key = ENV.MINIO_ACCESS_KEY
        secret_key = ENV.MINIO_SECRET_KEY
        region = ENV.MINIO_REGION
        use_ssl = ENV.MINIO_USE_SSL.lower() == "true" if ENV.MINIO_USE_SSL else False

        if not endpoint or not access_key or not secret_key:
            raise ValueError("MinIO environment variables are missing")

        _minio_client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=use_ssl,
            region=region
        )
        logger.info("MinIO connection initialized")
    return _minio_client


class MinioConnector:
    def __init__(self):
        self.client = get_minio_client()
        self.bucket_name = ENV.MINIO_BUCKET_NAME
        self.external_endpoint = ENV.MINIO_EXTERNAL_ENDPOINT

    def get_public_url(self, object_name: str) -> str:
        protocol = "https"
        return f"{protocol}://{self.external_endpoint}/{self.bucket_name}/{object_name}"

    def get_images(self, folder_path: str) -> list[str]:
        objects = self.client.list_objects(self.bucket_name, prefix=folder_path, recursive=True)
        return [
            self.get_public_url(obj.object_name)
            for obj in objects
            if not obj.is_dir
            and obj.object_name.lower().endswith(('.png', '.jpg', '.jpeg'))
        ]
