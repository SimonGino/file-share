import logging

import filetype
from minio import Minio
from minio.error import S3Error
from source.core.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MinioClient:
    def __init__(self):
        settings = get_settings()
        self.client = Minio(
            f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_SECURE
        )

    def upload_file(self, bucket_name, file_path, object_name):
        try:
            # 使用 filetype 获取文件的 MIME 类型
            kind = filetype.guess(file_path)
            content_type = kind.mime if kind else 'application/octet-stream'

            # 上传文件时指定 Content-Type
            self.client.fput_object(
                bucket_name, object_name, file_path,
                content_type=content_type
            )

            logger.info(f"File {file_path} is successfully uploaded as {object_name} to bucket {bucket_name}.")
        except S3Error as e:
            logger.error(f"Error occurred: {e}")

    def check_bucket_exists(self, bucket_name):
        try:
            found = self.client.bucket_exists(bucket_name)
            if found:
                logger.info(f"Bucket {bucket_name} exists.")
            else:
                logger.info(f"Bucket {bucket_name} does not exist.")
            return found
        except S3Error as e:
            logger.error(f"Error occurred: {e}")
            return False

    def delete_file(self, bucket_name, object_name):
        try:
            self.client.remove_object(bucket_name, object_name)
            logger.info(f"File {object_name} is successfully deleted from bucket {bucket_name}.")
        except S3Error as e:
            logger.error(f"Error occurred: {e}")

    def get_object(self, bucket_name, object_name):
        try:
            response = self.client.get_object(bucket_name, object_name)
            return response
        except S3Error as e:
            logger.error(f"Error occurred: {e}")
            return None

    def get_file_preview_url(self, bucket_name, filename, expiration=3600):
        try:
            presigned_url = self.client.presigned_get_object(
                bucket_name,
                filename,
                expires=expiration
            )
            return presigned_url
        except S3Error as e:
            logger.error(f"Error occurred: {e}")
            return None


minio_client = MinioClient()
