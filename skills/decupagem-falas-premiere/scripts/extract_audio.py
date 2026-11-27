"""Extract 16 kHz mono WAVs from source clips.

Usage: python -P extract_audio.py <work_dir> <clip_path> [<clip_path> ...]
Writes <work_dir>/wav/<clip name>.wav
"""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -P drops the script dir from sys.path
from common import ffmpeg

work, clips = sys.argv[1], sys.argv[2:]
os.makedirs(os.path.join(work, "wav"), exist_ok=True)
ff = ffmpeg()


def one(src):
    name = os.path.splitext(os.path.basename(src))[0]
    out = os.path.join(work, "wav", name + ".wav")
    if not os.path.exists(out):
        subprocess.run([ff, "-nostdin", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000", out], check=True)
    return name


with ThreadPoolExecutor(6) as ex:
    for name in ex.map(one, clips):
        print(name, flush=True)
print("DONE")
