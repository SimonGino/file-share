import logging
import os
from datetime import timedelta
from io import BytesIO
from urllib.parse import unquote_plus

import filetype
import minio
from fastapi import UploadFile, File, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from minio.error import S3Error
from starlette.requests import Request
from starlette.responses import StreamingResponse

from source.core.config import get_settings
from source.storages.minio_client import minio_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save the uploaded file to a temporary location
        file_location = f"/tmp/{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())

        # Upload the file to MinIO
        minio_client.upload_file(get_settings().MINIO_BUCKET_NAME, file_location, file.filename)

        # Remove the temporary file
        os.remove(file_location)

        presigned_url = await get_file_preview_url(get_settings().MINIO_BUCKET_NAME, file.filename)

        return JSONResponse(status_code=200, content={"message": "File uploaded successfully", "url": presigned_url})
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def get_file_preview_url(bucket_name,filename):
    # Generate a presigned URL for the uploaded file with custom headers
    presigned_url = minio_client.client.presigned_get_object(
        get_settings().MINIO_BUCKET_NAME,
        filename,
        expires=timedelta(days=7),  # URL expiry time
    )
    return presigned_url


# Ensure the bucket exists on startup
@router.on_event("startup")
async def startup_event():
    settings = get_settings()
    if not minio_client.check_bucket_exists(settings.MINIO_BUCKET_NAME):
        try:
            minio_client.client.make_bucket(settings.MINIO_BUCKET_NAME)
            logger.info(f"Bucket {settings.MINIO_BUCKET_NAME} created successfully.")
        except S3Error as e:
            logger.error(f"Error occurred: {e}")


# Function to delete a file
@router.delete("/delete/{filename}")
async def delete_file(filename: str):
    try:
        minio_client.delete_file(get_settings().MINIO_BUCKET_NAME, filename)
        return JSONResponse(status_code=200, content={"message": "File deleted successfully"})
    except Exception as e:
        logger.error(f"File deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 文件列表接口
@router.get("/list")
async def list_files():
    try:
        bucket_name = get_settings().MINIO_BUCKET_NAME
        objects = minio_client.client.list_objects(bucket_name, recursive=True)

        file_list = []
        for obj in objects:
            # 解码对象名中的特殊字符，如+替换为空格
            object_name = unquote_plus(obj.object_name)
            file_info = {

                "object_name": object_name,
                "last_modified": obj.last_modified.strftime("%Y-%m-%d %H:%M:%S"),
                "etag": obj.etag,
                "size": obj.size,
                "content_type": obj.content_type,
                "metadata": obj.metadata,
                # Add more fields as needed
            }
            file_list.append(file_info)

        return JSONResponse(status_code=200, content={"files": file_list})

    except minio.error.S3Error as e:
        logger.error(f"MinIO error: {e}")
        raise HTTPException(status_code=500, detail="Error fetching file list from MinIO")
    except Exception as e:
        logger.error(f"Get file list failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 文件下载接口
@router.get("/download/{filename}")
async def download_file(filename: str, request: Request):
    try:
        bucket_name = get_settings().MINIO_BUCKET_NAME
        obj = minio_client.get_object(bucket_name, filename)

        # 从MinIO获取文件内容
        file_data = BytesIO()
        for d in obj.stream(32 * 1024):
            file_data.write(d)
        file_data.seek(0)

        # 获取Content-Type
        content_type = obj.headers.get("Content-Type")

        # 返回文件流作为响应
        return StreamingResponse(file_data, media_type=content_type,
                                 headers={"Content-Disposition": f"attachment; filename={filename}"})

    except Exception as e:
        logger.error(f"Download file failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 文件信息接口
@router.get("/info/{filename}")
async def get_file_info(filename: str):
    try:
        bucket_name = get_settings().MINIO_BUCKET_NAME
        file_info = minio_client.client.stat_object(bucket_name, filename)

        # 将 last_modified 转换为字符串
        last_modified_str = file_info.last_modified.strftime("%Y-%m-%d %H:%M:%S")
        presigned_url = await get_file_preview_url(bucket_name, filename)
        return JSONResponse(status_code=200, content={
            "filename": file_info.object_name,
            "size": file_info.size,
            "last_modified": last_modified_str,  # 现在是字符串
            "etag": file_info.etag,
            "content_type": file_info.content_type,
            "presigned_url": presigned_url,
        })
    except Exception as e:
        logger.error(f"Get file info failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
