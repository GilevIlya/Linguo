from fastapi import APIRouter, Depends, Response
from urllib.parse import quote

from .utils.dependencies import get_file_service
from .security import get_current_user_id
from uuid import UUID

from api.v1.services.file_service import FileService

files_router = APIRouter(
    tags=["files"]
)


@files_router.get(
    path="/files/{file_key:path}",
    summary='Get a file by its key',

    description=(
    "Retrieves a file by its storage key. "
    "The file key supports path separators (e.g. `IMAGE/uuid.jpeg`, `CARDS/SOUNDS/uuid.mpeg`). "
    "Returns raw file bytes with the original content type and filename preserved in the response headers."
    )
)
async def get_file(
    file_key: str,
    owner_id: UUID = Depends(get_current_user_id),
    service: FileService = Depends(get_file_service)
):
    file, file_bytes = await service.get_file(file_key, owner_id)

    return Response(
        content=file_bytes,
        media_type=file.content_type,
        headers={
            "Content-Disposition": f'inline; filename="{quote(file.original_name)}"'
        }
    )