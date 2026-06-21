import logging
import uuid
from contextlib import asynccontextmanager
from typing import Tuple

from aioboto3 import Session  # type: ignore[import-untyped]
from botocore.config import Config  # type: ignore[import-untyped]

from api.v1.configs.s3_config import s3_config
from api.v1.services.schemas.file_param import FileParam

logger = logging.getLogger("app")


class S3Service:
    def __init__(self, session: Session):
        self.s3_session = session

    @asynccontextmanager
    async def _get_client(self):
        """
        Asynchronous context manager to create and yield an S3 client.

        Yields:
            aioboto3.client: An S3 client configured with the provided settings.
        """
        async with self.s3_session.client(
            "s3",
            endpoint_url=s3_config.S3_ENDPOINT,
            aws_access_key_id=s3_config.S3_ACCESS_KEY,
            aws_secret_access_key=s3_config.S3_SECRET_KEY,
            region_name=s3_config.S3_REGION,
            config=Config(signature_version="s3v4"),
            verify=s3_config.S3_USE_SSL,
        ) as client:
            yield client

    async def save_file(self, prefix: str, file_param: FileParam) -> Tuple[str, uuid.UUID]:
        """
        Saves a file to the S3 bucket under a specified prefix.

        Args:
            prefix (str): The prefix (folder path) under which the file will be saved.
            stream (BinaryIO): The file content to be uploaded.
            file_extension (str): The content extension of the file being uploaded.

        Returns:
            str: The key of the saved file in the S3 bucket.
        """
        async with self._get_client() as client:
            file_id = uuid.uuid4()
            key = f"{prefix}/{file_id}.{file_param.file_extension}"
            await client.put_object(Bucket=s3_config.S3_BUCKET_NAME, Key=key, Body=file_param.content)
            logger.info(f"File saved to S3 with key: {key}")
            return key, file_id

    async def get_file(self, file_key: str) -> bytes:
        """
        Retrieves a file from the S3 bucket using the specified prefix and key.

        Args:
            file_key (str): The key (file name) of the file to retrieve.

        Returns:
            BinaryIO: A binary stream of the file content.
        """
        async with self._get_client() as client:
            response = await client.get_object(Bucket=s3_config.S3_BUCKET_NAME, Key=f"{file_key}")
            logger.info(f"File retrieved from S3 with key: {file_key}")
            async with response["Body"] as stream:
                return await stream.read()

    async def delete_file(self, file_key: str) -> None:
        """
        Deletes a file from the S3 bucket by its key.

        Args:
            file_key (str): The key (file name) of the file to delete.

        Returns:
            None
        """
        async with self._get_client() as client:
            await client.delete_object(Bucket=s3_config.S3_BUCKET_NAME, Key=file_key)
            logger.info(f"File deleted from S3 with key: {file_key}")
            return None