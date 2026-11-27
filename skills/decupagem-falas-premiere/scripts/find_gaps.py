"""Whisper large-v3 sometimes skips whole stretches of speech (seen: 25 s answers missing).
Find voiced audio with no transcript and re-transcribe each stretch in isolation.

Usage: python -P find_gaps.py <work_dir> [min_gap_seconds=3]
Prints recovered text and writes <work_dir>/gaps.json (same word format as tr/*.json, absolute times).
"""
import glob, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -P drops the script dir from sys.path
from common import enable_cuda_dlls, envelope, load_wav

enable_cuda_dlls()
from faster_whisper import WhisperModel

work = sys.argv[1]
MIN_GAP = float(sys.argv[2]) if len(sys.argv) > 2 else 3.0

todo = []
for p in sorted(glob.glob(os.path.join(work, "tr", "*.json"))):
    d = json.load(open(p, encoding="utf-8"))
    name = d["file"]
    db, thr = envelope(os.path.join(work, "wav", name + ".wav"))
    covered = np.zeros(len(db), bool)
    for s in d["segments"]:
        covered[int(s["start"] / 0.02):int(s["end"] / 0.02) + 1] = True
    voiced = (db > thr) & ~covered
    # group uncovered frames that contain sound, allowing short quiet holes
    k = 0
    while k < len(voiced):
        if voiced[k]:
            j, last = k, k
            while j < len(voiced) and (voiced[j] or j - last < 50):   # bridge holes < 1 s
                if voiced[j]: last = j
                j += 1
            a, b = k * 0.02, (last + 1) * 0.02
            if b - a >= MIN_GAP:
                todo.append((name, a, b))
            k = j
        else:
            k += 1

model = WhisperModel("large-v3", device="cuda", compute_type="float16")
found = []
for name, a, b in todo:
    x, sr = load_wav(os.path.join(work, "wav", name + ".wav"))
    off = max(0.0, a - 0.3)
    segs, _ = model.transcribe(x[int(off * sr):int((b + 0.3) * sr)], language="pt", word_timestamps=True,
                               condition_on_previous_text=False, beam_size=5)
    for s in segs:
        r = {"file": name, "start": s.start + off, "end": s.end + off, "text": s.text.strip(),
             "no_speech": round(s.no_speech_prob, 2),
             "words": [{"w": w.word, "s": w.start + off, "e": w.end + off, "p": round(w.probability, 3)} for w in (s.words or [])]}
        found.append(r)
        print(f"{name} [{r['start']:.2f}-{r['end']:.2f}] nsp={r['no_speech']} {r['text']}", flush=True)
json.dump(found, open(os.path.join(work, "gaps.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"DONE ({len(todo)} trechos verificados)")
