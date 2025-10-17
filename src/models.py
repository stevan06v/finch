from pydantic import BaseModel


class Video(BaseModel):
    hash: str
    audio_path: str
    video_path: str
    url: str
