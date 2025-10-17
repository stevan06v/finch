import os
import random
import re
import subprocess
import threading
from abc import ABC, abstractmethod

import yt_dlp
from yt_dlp import YoutubeDL
from models import Video
from src.helpers import generate_random_string, convert_video_to_audio, normalize_fragments
import whisper


class WhisperDownloader(ABC):
    def __init__(self, download_folder: str = "media"):
        self.path = os.getcwd()
        self.download_folder = download_folder
        self.downloads = set()
        self.model = whisper.load_model("small")

    @abstractmethod
    def download(self, url: str, callback=None):
        pass

    @abstractmethod
    def get_downloads(self):
        pass

    def transcribe(self, video: Video, progress_callback=None):
        result = self.model.transcribe(audio=video.audio_path)
        print(f"Transcribed: {result}")
        print(result)


class YoutubeDownloader(WhisperDownloader):
    def download(self, url, callback=None):
        def task():
            dir_name = generate_random_string(8)

            project_root = os.path.dirname(self.path)
            target_dir = os.path.join(project_root, self.download_folder, dir_name)

            os.makedirs(target_dir, exist_ok=True)
            print(f"Downloading video to {target_dir}")
            try:
                opts_video = {
                    "format": "bestvideo[height<=1080][vcodec^=avc]+bestaudio[acodec=aac]/best[ext=mp4]",
                    "outtmpl": f"{target_dir}/%(title)s.%(ext)s",
                    "merge_output_format": "mp4",
                    "prefer_ffmpeg": True,
                    "progress_hooks": [lambda d: self.download_progress_hook(d, callback)],
                }
                with YoutubeDL(opts_video) as ydl:
                    ydl.download([url])

                downloaded_file = os.listdir(target_dir)[0]
                downloaded_video = Video(
                    hash=str(hash(url)),
                    audio_path=f"{target_dir}/{downloaded_file.replace('.mp4', '.mp3')}",
                    video_path=f"{target_dir}/{downloaded_file}",
                    url=str(url)
                )

                convert_video_to_audio(downloaded_video.video_path)
                self.transcribe(video=downloaded_video)
                print(f"Download {downloaded_video}")

            except Exception as e:
                print(f"Failed to download video: {e}")
                callback({"status": "error", "message": str(e)})

        thread = threading.Thread(target=task)
        thread.start()

    def download_progress_hook(self, d, callback=None):
        if d['status'] == 'downloading':
            curr_fragment_idx = d.get('fragment_index', 0)
            fragment_count = d.get('fragment_count', 0)

            progress = {
                "status": "downloading",
                "percent": normalize_fragments(curr_fragment_idx, fragment_count, 0),
                "eta": d.get('eta', 0),
                "speed": d.get('speed', 0),
            }
            if callback:
                callback(progress)
        elif d['status'] == 'finished':
            if callback:
                callback({"status": "finished", "filename": d['filename']})

    def progress_callback(self, progress):
        percent = progress.get("percent", 0)
        print(f"Transcription Progress: {percent:.2f}%")

    def get_downloads(self):
        pass


class VimeoDownloader(WhisperDownloader):
    def download(self, url, callback=None):
        pass

    def get_downloads(self):
        pass


class DownloaderFactory:
    @staticmethod
    def get_downloader(url: str) -> WhisperDownloader:
        if re.search(r"(youtube\.com|youtu\.be)", url):
            return YoutubeDownloader()
        elif "vimeo.com" in url:
            return VimeoDownloader()
        else:
            raise ValueError("No matching downloader found for this URL")


def default_callback(progress):
    print(progress)


if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=DC2p3kFjcK0"
    downloader = DownloaderFactory.get_downloader(url)
    downloader.download(url, callback=default_callback)
