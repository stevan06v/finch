import os
import random
from pydub import AudioSegment
import string


def generate_random_string(length: int):
    return ''.join(random.sample(string.ascii_letters, length))


def convert_video_to_audio(video_file_path):
    audio = AudioSegment.from_file(video_file_path, format="mp4")
    audio = audio.set_frame_rate(20000)
    audio.export(video_file_path.replace(".mp4", ".mp3"), format="mp3")


def normalize_fragments(curr_fragment, max_fragment, min_fragment):
    normalized_value = ((curr_fragment - min_fragment) / (max_fragment - min_fragment)) * 100
    return normalized_value
