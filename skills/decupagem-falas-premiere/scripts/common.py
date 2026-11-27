"""Shared helpers: CUDA DLLs for faster-whisper on Windows, ffmpeg lookup, wav loading, energy envelope."""
import os, shutil, site, wave
import numpy as np


def enable_cuda_dlls():
    # pip-installed nvidia-cublas-cu12 / nvidia-cudnn-cu12 are not on PATH by default on Windows
    for base in site.getsitepackages() + [site.getusersitepackages()]:
        for sub in ("nvidia/cublas/bin", "nvidia/cudnn/bin"):
            p = os.path.join(base, sub)
            if os.path.isdir(p):
                os.add_dll_directory(p)
                os.environ["PATH"] = p + os.pathsep + os.environ["PATH"]


def ffmpeg():
    exe = shutil.which("ffmpeg")
    if not exe:
        winget = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe")
        exe = winget if os.path.exists(winget) else None
    if not exe:
        raise SystemExit("ffmpeg não encontrado (instale com: winget install ffmpeg)")
    return exe


def load_wav(path):
    # faster-whisper's own PyAV decoder breaks with av>=19, so we always feed it numpy audio
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    return x, sr


def envelope(path, hop_s=0.02):
    """RMS envelope in dB (20 ms frames) and an adaptive threshold: room-noise floor (p10) + 10 dB."""
    x, sr = load_wav(path)
    hop = int(sr * hop_s)
    n = len(x) // hop
    db = 20 * np.log10(np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1)) + 1e-9)
    return db, np.percentile(db, 10) + 10
