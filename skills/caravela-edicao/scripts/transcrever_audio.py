"""Transcreve o áudio de briefing do Pedro, no computador dele (nada sai da máquina).

Uso: python -P transcrever_audio.py <audio> [--saida briefing.txt] [--cpu]
Aceita qualquer formato que o ffmpeg abre (.ogg/.opus do WhatsApp, .m4a do iPhone, .mp3, .wav, .mp4).
Imprime o texto em parágrafos (um a cada pausa longa) e, com --saida, grava num .txt.
Usa faster-whisper large-v3 na placa de vídeo; sem placa (ou com --cpu), o modelo "medium" no processador.
"""
import os, shutil, site, subprocess, sys
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
args = sys.argv[1:]
cpu = "--cpu" in args
if cpu: args.remove("--cpu")
saida = None
if "--saida" in args:
    i = args.index("--saida"); saida = args[i + 1]; del args[i:i + 2]
if not args:
    raise SystemExit(__doc__)
audio_path = args[0]
if not os.path.exists(audio_path):
    raise SystemExit(f"Não achei o arquivo: {audio_path}")

# as DLLs da placa de vídeo instaladas pelo pip não ficam no PATH do Windows
for base in site.getsitepackages() + [site.getusersitepackages()]:
    for sub in ("nvidia/cublas/bin", "nvidia/cudnn/bin"):
        p = os.path.join(base, sub)
        if os.path.isdir(p):
            os.add_dll_directory(p); os.environ["PATH"] = p + os.pathsep + os.environ["PATH"]

ff = shutil.which("ffmpeg") or os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe")
if not os.path.exists(ff) and not shutil.which("ffmpeg"):
    raise SystemExit("ffmpeg não encontrado (instale com: winget install ffmpeg)")
pcm = subprocess.run([ff, "-v", "error", "-i", audio_path, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                     stdout=subprocess.PIPE, check=True).stdout
audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
dur = len(audio) / 16000

from faster_whisper import WhisperModel
try:
    if cpu: raise RuntimeError("cpu pedido")
    model = WhisperModel("large-v3", device="cuda", compute_type="float16")
except Exception:
    model = WhisperModel("medium", device="cpu", compute_type="int8")

PROMPT = ("Briefing de edição de vídeo. Cliente, pasta do material, Premiere, decupagem, zoom dinâmico, zoom calmo, "
          "balanço de cor, motions, Artlist, trilha, Reels, vertical, Riomar, Diamantes, Maria Clara, Novais.")
segs, info = model.transcribe(audio, language="pt", vad_filter=True, initial_prompt=PROMPT, beam_size=5)

paragrafos, atual, fim_ant = [], [], None
for s in segs:
    if fim_ant is not None and s.start - fim_ant > 1.5 and atual:
        paragrafos.append(" ".join(atual)); atual = []
    atual.append(s.text.strip()); fim_ant = s.end
if atual: paragrafos.append(" ".join(atual))
texto = "\n\n".join(paragrafos)

m, s = divmod(int(round(dur)), 60)
print(f"[áudio de {m} min {s:02d} s]\n")
print(texto)
if saida:
    with open(saida, "w", encoding="utf-8") as f:
        f.write(texto + "\n")
