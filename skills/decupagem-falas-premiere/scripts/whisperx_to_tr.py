"""Convert WhisperX JSON output into the tr/*.json format the other scripts read, and rebuild all.txt.

Usage: python -P whisperx_to_tr.py <work_dir>
Reads  <work_dir>/wx/<name>.json   (whisperx ... --output_format json --output_dir <work_dir>/wx)
       <work_dir>/wav/<name>.wav   (only for the duration)
Writes <work_dir>/tr/<name>.json   {"file", "duration", "segments": [{"start","end","text","words":[{"w","s","e","p"}]}]}
       <work_dir>/all.txt
Words WhisperX could not align (numbers, symbols: no start/end) get times interpolated from their neighbours
and p = 0, so they show up as "conferir no ouvido".
"""
import glob, json, os, sys, wave

work = sys.argv[1]
wx_dir, tr_dir = os.path.join(work, "wx"), os.path.join(work, "tr")
os.makedirs(tr_dir, exist_ok=True)


def duration(name):
    path = os.path.join(work, "wav", name + ".wav")
    if not os.path.exists(path):
        return 0.0
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def fix_words(seg):
    words = seg.get("words") or []
    out = []
    for k, w in enumerate(words):
        s, e = w.get("start"), w.get("end")
        if s is None or e is None:
            prev_e = out[-1]["e"] if out else seg["start"]
            nxt = next((x["start"] for x in words[k + 1:] if x.get("start") is not None), seg["end"])
            s, e = prev_e, max(prev_e, nxt)
        out.append({"w": " " + w["word"].strip(), "s": round(s, 3), "e": round(e, 3),
                    "p": round(w.get("score", 0.0) or 0.0, 3)})
    return out


for path in sorted(glob.glob(os.path.join(wx_dir, "*.json"))):
    name = os.path.splitext(os.path.basename(path))[0]
    d = json.load(open(path, encoding="utf-8"))
    segs = [{"start": round(s["start"], 3), "end": round(s["end"], 3), "text": s["text"].strip(),
             "words": fix_words(s)} for s in d.get("segments", [])]
    json.dump({"file": name, "duration": duration(name), "segments": segs},
              open(os.path.join(tr_dir, name + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{name}: {len(segs)} segs")

with open(os.path.join(work, "all.txt"), "w", encoding="utf-8") as f:
    for p in sorted(glob.glob(os.path.join(tr_dir, "*.json"))):
        d = json.load(open(p, encoding="utf-8"))
        f.write(f"\n=== {d['file']} ({d['duration']:.1f}s)\n")
        for s in d["segments"]:
            f.write(f"[{s['start']:6.2f}-{s['end']:6.2f}] {s['text']}\n")
print("DONE")
