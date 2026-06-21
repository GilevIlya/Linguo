from uuid import UUID
from typing import Tuple
import os


from api.v1.services.schemas.file_param import FileParam
from api.v1.models.files import Files
from api.v1.services.schemas.file_prefix import FilePrefix

from api.v1.services.s3_service import S3Service
from api.v1.repositories.interfaces.IFileRepository import IFileRepository

from api.v1.services.exceptions.base_exceptions import NotFoundException, PermissionDeniedException, ValidationException
from api.v1.services.exceptions.error_codes.files_error_codes import FilesErrorCodes


MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))

class FileService():
    def __init__(
        self,
        s3_service: S3Service,
        repository: IFileRepository,
    ):
        self.s3_service = s3_service
        self.repository = repository
        self.MAX_FILE_SIZE = MAX_FILE_SIZE

    async def upload_file(
        self,
        prefix: FilePrefix,
        file: FileParam,
        owner_id: UUID,
        is_public: bool = True,
    ) -> str:
        await self._check_size(file.size)

        key, file_id = await self._upload_to_s3(file, prefix)
        await self._save_to_db(
            file=file,
            file_id=file_id,
            owner_id=owner_id,
            key=key,
            is_public=is_public,
        )

        return key
    
    async def get_file(
        self,
        file_key: str,
        owner_id: UUID
    ) -> Tuple[Files, bytes]:
        file = await self._get_file_record_by_key(
            file_key=file_key,
            owner_id=owner_id
        )
        bytes_file = await self._get_file_from_s3(
            file_key=file_key
        )
        return file, bytes_file

    async def delete_file(
        self,
        file_key: str,
        owner_id: UUID
    ) -> bool:
        await self.s3_service.delete_file(file_key=file_key)
        await self.repository.delete_file_by_key(file_key=file_key, owner_id=owner_id)
        return True

    async def _upload_to_s3(self, file: FileParam, prefix: FilePrefix) -> Tuple[str, UUID]:
        return await self.s3_service.save_file(
            prefix=prefix.value,
            file_param=file
        )
    
    async def _save_to_db(self, file: FileParam, file_id: UUID, owner_id: UUID, key: str, is_public: bool) -> Files:
        return await self.repository.create(
            Files(
                id=file_id,
                owner_id=owner_id,
                file_key=key,
                original_name=file.original_name,
                extension=file.file_extension,
                content_type=file.content_type,
                size_bytes=file.size,
                is_public=is_public,
            )
        )
    
    async def _get_file_record_by_key(self, file_key: str, owner_id: UUID) -> Files:
        file = await self.repository.get_file_by_key(
            file_key=file_key
        )
        if not file:
            raise NotFoundException(
                error_code=FilesErrorCodes.FILE_NOT_FOUND.value,
                message="No such file exists"
            )
        if file.is_public is False and file.owner_id != owner_id:
            raise PermissionDeniedException(
                error_code=FilesErrorCodes.FILE_BELONGS_TO_ANOTHER_USER.value,
                message="You don't have permission for that file"
            )
        return file
    
    async def _get_file_from_s3(self, file_key: str) -> bytes:
        response = await self.s3_service.get_file(file_key=file_key)
        return response
    
    async def _check_size(self, size: int | None) -> bool:
        if size is None or size > self.MAX_FILE_SIZE:
            raise ValidationException(
                error_code=FilesErrorCodes.FILE_TOO_LARGE.value,
                message="The file size is too large"
            )
        return True