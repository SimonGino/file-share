import os

import aiofiles
import openai
from fastapi import APIRouter, HTTPException
from fastapi import File, UploadFile
from pydub import AudioSegment

from source.core.config import get_settings
from source.storages.minio_client import minio_client

router = APIRouter()

# 设置OpenAI API密钥
openai.api_key = get_settings().OPENAI_API_KEY
openai.base_url = get_settings().OPENAI_API_BASE_URL

# 创建临时文件夹
os.makedirs("temp", exist_ok=True)
bucket_name = get_settings().MINIO_BUCKET_NAME


async def save_audio_file(file: UploadFile, path: str):
    async with aiofiles.open(path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

def split_audio(input_file: str, max_size_mb: int = 25):
    try:
        audio = AudioSegment.from_file(input_file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading audio file: {str(e)}")

    part_length_ms = int((max_size_mb * 1024 * 1024) / (audio.frame_rate * audio.frame_width) * 1000)
    parts = [audio[i:i + part_length_ms] for i in range(0, len(audio), part_length_ms)]
    return parts


async def transcribe_audio(file_path: str) -> str:
    with open(file_path, 'rb') as audio_file:
        response = openai.audio.transcriptions.create(
          model="whisper-1",
          file=audio_file,
          response_format="text",
          language="zh"
        )
    return response


@router.post("/convert")
async def upload_file(file: UploadFile = File(...)):
    input_file_path = f"temp/{file.filename}"

    # 保存上传的文件
    await save_audio_file(file, input_file_path)
    # 分割音频文件（如果超过25MB）
    audio_parts = split_audio(input_file_path)

    transcript = ""
    for i, part in enumerate(audio_parts):
        part_file_path = f"temp/{file.filename}_part_{i}.mp3"
        part.export(part_file_path, format="mp3")
        # 转录音频文件
        part_transcript = await transcribe_audio(part_file_path)
        print(f"Transcription for part {i}: {part_transcript}")
        transcript += part_transcript

        # 删除临时文件
        os.remove(part_file_path)

    # 删除原始文件
    os.remove(input_file_path)

    return {"transcript": transcript}
