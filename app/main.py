from operator import length_hint
import os
import time

from fastapi import FastAPI, UploadFile, status
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
from fastapi.responses import FileResponse
from pydantic import BaseModel

from moviepy.editor import VideoFileClip

VIDEO_UPLOAD_DIR = "upload_files"


class VideoMetadata(BaseModel):
    size_in_bytes: int
    length_in_seconds: int
    type: str


app = FastAPI()


@app.post("/videos")
async def upload_video(video: UploadFile):
    # Content-Type Validation
    valid_types = ["video/mp4", "video/x-matroska"]
    valid_length_in_second = 600
    valid_size_in_mb = 1024
    content_type = video.content_type
    if content_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported media type {content_type}",
        )

    # Video size validation
    video_bytes = await video.read()
    size_in_mb = len(video_bytes) / (1024 * 1024)
    if size_in_mb >= valid_size_in_mb:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Unsupported file size",
        )

    # Save the file
    current_timestamp = str(time.time()).replace(".", "_")
    saved_file_name = f"{current_timestamp}--{video.filename.replace(' ', '_')}"
    file_location = f"{VIDEO_UPLOAD_DIR}/{saved_file_name}"

    with open(file_location, "wb+") as file_object:
        file_object.write(video_bytes)

    # Video length validation
    clip = VideoFileClip(file_location)
    length_in_second = clip.duration
    clip.close()
    if length_in_second > valid_length_in_second:
        os.remove(file_location)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Unsupported file size",
        )
    return {"filename": saved_file_name}


@app.get("/videos")
def get_all_videos(request: Request):
    base_url = request.base_url
    video_links = [
        f"{base_url}videos/{file}" for file in os.listdir(VIDEO_UPLOAD_DIR)]
    return {"videos": video_links}


@app.get("/videos/{filename}")
def get_video(filename: str):
    return FileResponse(f"{VIDEO_UPLOAD_DIR}/{filename}")


@app.post("/videos/price-calculator")
def calcuate_price(video: VideoMetadata):
    size_constraint = 500 * 1024 * 1024
    size_cost = 5 if video.size_in_bytes < size_constraint else 12.5
    length_constraint = 6 * 60 + 18
    length_cost = 12.5 if video.length_in_seconds < length_constraint else 20
    total_cost = f"{size_cost + length_cost}$"
    return {"total_cost": total_cost}
