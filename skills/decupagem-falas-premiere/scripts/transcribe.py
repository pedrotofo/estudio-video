"""Transcribe every WAV with word timestamps (faster-whisper large-v3 on CUDA).

Usage: python -P transcribe.py <work_dir> [--cpu]
Reads <work_dir>/wav/*.wav, writes <work_dir>/tr/<name>.json and <work_dir>/all.txt (readable dump).
"""
import glob, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -P drops the script dir from sys.path
from common import enable_cuda_dlls, load_wav

enable_cuda_dlls()
from faster_whisper import WhisperModel

work = sys.argv[1]
cpu = "--cpu" in sys.argv
out_dir = os.path.join(work, "tr")
os.makedirs(out_dir, exist_ok=True)
model = WhisperModel("large-v3", device="cpu" if cpu else "cuda", compute_type="int8" if cpu else "float16")

# Prompt with disfluencies so Whisper keeps false starts and repetitions verbatim
PROMPT = "Então, é... a gente, a gente trabalha com, eh, com arquitetura. Não, peraí, vou de novo."

for wav in sorted(glob.glob(os.path.join(work, "wav", "*.wav"))):
    name = os.path.splitext(os.path.basename(wav))[0]
    out = os.path.join(out_dir, name + ".json")
    if os.path.exists(out):
        continue
    t0 = time.time()
    audio, _ = load_wav(wav)
    segs, info = model.transcribe(audio, language="pt", word_timestamps=True, vad_filter=False,
                                  condition_on_previous_text=False, initial_prompt=PROMPT, beam_size=5)
    data = [{"start": s.start, "end": s.end, "text": s.text.strip(),
             "words": [{"w": w.word, "s": w.start, "e": w.end, "p": round(w.probability, 3)} for w in (s.words or [])]}
            for s in segs]
    json.dump({"file": name, "duration": info.duration, "segments": data}, open(out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"{name}: {len(data)} segs, {time.time() - t0:.1f}s", flush=True)

with open(os.path.join(work, "all.txt"), "w", encoding="utf-8") as f:
    for p in sorted(glob.glob(os.path.join(out_dir, "*.json"))):
        d = json.load(open(p, encoding="utf-8"))
        f.write(f"\n=== {d['file']} ({d['duration']:.1f}s)\n")
        for s in d["segments"]:
            f.write(f"[{s['start']:6.2f}-{s['end']:6.2f}] {s['text']}\n")
print("DONE")
