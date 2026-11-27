"""Turn the chosen takes into frame-accurate sub-clips with silences removed, plus the Premiere batch.

Usage: python -P build_cuts.py <work_dir> <seq_fps> [pad=0.25]
  seq_fps: sequence frame rate, e.g. 23.976 (= 254016000000 / sequence timebase ticks)

Inputs in <work_dir>:
  selection.json  [{"block": "...", "file": "TOFO8876", "start": 16.02, "end": 44.34}, ...]  (timeline order;
                  start/end = transcript segment bounds of the chosen take in the source clip)
  ids.json        {"TOFO8876": "<projectItemId>", ...}
  tr/*.json, gaps.json (optional), wav/*.wav
Outputs: cuts.json (pieces + report), batch.json (clips for add_to_timeline_batch, trackIndex 0)
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -P drops the script dir from sys.path
from common import envelope

# optional: --sel selection_alt.json  -> reads that file and writes cuts_alt.json / batch_alt.json
args = sys.argv[1:]
SEL = "selection.json"
if "--sel" in args:
    i = args.index("--sel")
    SEL = args[i + 1]
    del args[i:i + 2]
stem = os.path.splitext(SEL)[0]
SUFFIX = "" if stem == "selection" else "_" + stem.replace("selection_", "")
sys.argv = [sys.argv[0]] + args

work = sys.argv[1]
fps_in = float(sys.argv[2])
FPS = 24000 / 1001 if abs(fps_in - 23.976) < 0.01 else 30000 / 1001 if abs(fps_in - 29.97) < 0.01 \
    else 60000 / 1001 if abs(fps_in - 59.94) < 0.01 else fps_in
FRAME = 1 / FPS
PAD = float(sys.argv[3]) if len(sys.argv) > 3 else 0.15   # breathing room around inner pauses
TAIL = 0.25                                                # after the LAST word of a take (0.15 sounded glued, 17/11/2026)
LEAD = 0.02                                                # before the first word: only enough not to clip the attack
GAP = 0.25                                                 # a quiet run this long separates the count from the speech
MIN_CUT = 0.20                                             # only remove a pause if at least this much goes

sel = json.load(open(os.path.join(work, SEL), encoding="utf-8"))
ids = json.load(open(os.path.join(work, "ids.json"), encoding="utf-8"))
gaps_path = os.path.join(work, "gaps.json")
recovered = json.load(open(gaps_path, encoding="utf-8")) if os.path.exists(gaps_path) else []

cache = {}
def source(name):
    if name not in cache:
        d = json.load(open(os.path.join(work, "tr", name + ".json"), encoding="utf-8"))
        words = [w for s in d["segments"] for w in s["words"]]
        # recovered words come from padded re-transcriptions: skip any that overlap words we already have
        extra = [w for r in recovered if r["file"] == name for w in r["words"]
                 if not any(w["s"] < o["e"] and w["e"] > o["s"] for o in words)]
        words = sorted(words + extra, key=lambda w: w["s"])
        db, thr = envelope(os.path.join(work, "wav", name + ".wav"))
        cache[name] = (d["duration"], words, db, thr)
    return cache[name]

def loud(db, thr, a, b):
    i, j = max(0, int(a / 0.02)), min(len(db), int(b / 0.02))
    return db[i:j] > thr, i

pieces, report = [], []
for s in sel:
    name, ts, te = s["file"], s["start"], s["end"]
    dur, allw, db, thr = source(name)
    idx = [k for k, w in enumerate(allw) if w["s"] >= ts - 0.05 and w["e"] <= te + 0.05]
    if not idx:
        raise SystemExit(f"Nenhuma palavra em {name} {ts}-{te}")
    W = [allw[k] for k in idx]
    prev_e = allw[idx[0] - 1]["e"] if idx[0] > 0 else 0.0
    next_s = allw[idx[-1] + 1]["s"] if idx[-1] + 1 < len(allw) else dur

    # refine speech onset/offset on the energy envelope; never reach into neighbouring words.
    # Whisper stretches the first word back over the director's count ("um, dois, três, gravando") and the
    # silence before it, so the onset is the attack after the last pause (>= 0.25 s) before the 2nd word.
    ref = W[1]["s"] if len(W) > 1 else W[0]["e"]
    m, i0 = loud(db, thr, W[0]["s"] - 0.4, ref + 0.1)
    onset, quiet, found = W[0]["s"], 0, False
    for k in range(len(m) - 1, -1, -1):
        if m[k]:
            onset, quiet, found = (i0 + k) * 0.02, 0, True
        else:
            quiet += 1
            if found and quiet * 0.02 >= GAP:
                break
    # Offset (fixed 17/11/2026, Empresarial): WhisperX ends the last word EARLY and the clip-wide floor (p10+10)
    # sits above soft word endings in noisy rooms, so "Empresarial", "negócios", "shopping" lost their tails.
    # Now: LOCAL floor (p20 of the 2 s after the last word start), 100 ms smoothing, voice = floor + 12 dB,
    # walk from the last word's START until 0.2 s of quiet, never into the next word.
    la, H = W[-1]["s"], 0.01                               # 10 ms frames: 20 ms missed soft endings ("-ping")
    if name + "@10" not in cache:
        cache[name + "@10"] = envelope(os.path.join(work, "wav", name + ".wav"), hop_s=H)[0]
    d10 = cache[name + "@10"]
    a, b = int(la / H), int(min(dur, la + 2.0) / H)
    f_out = np.percentile(d10[a:b], 20) if b > a else thr - 10
    sm = np.convolve(d10, np.ones(5) / 5, mode="same")     # 50 ms smoothing: clicks and steps are not voice
    lim = int(min(next_s - 0.05, la + 2.5, dur) / H)
    k, last = a, a
    while k < lim:
        if sm[k] >= f_out + 12:
            last = k
        elif k - last >= 20:                               # 0.2 s of quiet = end of speech
            break
        k += 1
    # never trust W[-1]["e"]: WhisperX ends the last word early, OR stretches it for seconds over the silence after it
    offset = max((last + 1) * H, la + 0.1)
    start = max(onset - LEAD, (prev_e + onset) / 2, 0.0)   # the cut starts on the voice (Pedro's rule)
    end = min(offset + TAIL, next_s - 0.05, dur)

    # internal pauses straight from the envelope (Whisper word times stretch over pauses); use the lower of the
    # clip-wide threshold and this take's own floor + 10 dB, so soft syllables are never taken for silence
    tk = db[int(max(0, start - 1.5) / 0.02):int(min(dur, end + 1.5) / 0.02)]
    thr = min(thr, np.percentile(tk, 10) + 10) if len(tk) else thr
    m, i0 = loud(db, thr, start, end)
    m = m.copy()
    k = 0
    while k < len(m):                      # ignore clicks: loud runs shorter than 80 ms
        if m[k]:
            j = k
            while j < len(m) and m[j]: j += 1
            if j - k < 4: m[k:j] = False
            k = j
        else:
            k += 1
    keep, cur, k = [], start, 0
    while k < len(m):
        if not m[k]:
            j = k
            while j < len(m) and not m[j]: j += 1
            q0, q1 = (i0 + k) * 0.02, (i0 + j) * 0.02
            if k > 0 and j < len(m) and (q1 - q0) - 2 * PAD >= MIN_CUT:
                keep.append((cur, q0 + PAD)); cur = q1 - PAD
            k = j
        else:
            k += 1
    keep.append((cur, end))
    # drop short pieces touching no word (lip smacks, breaths, clicks)
    keep = [(a, b) for a, b in keep if b - a >= 0.6 or any(w["s"] < b and w["e"] > a for w in W)]

    report.append({"block": s.get("block", ""), "file": name, "in": round(start, 2), "out": round(end, 2),
                   "pieces": len(keep), "silence_removed": round((end - start) - sum(b - a for a, b in keep), 2),
                   "text": "".join(w["w"] for w in W).strip()})
    pieces += [{"file": name, "block": s.get("block", ""), "in": a, "out": b} for a, b in keep]

# lay out on the timeline, frame-quantised
t = 0
for p in pieces:
    fi, fo = round(p["in"] * FPS), round(p["out"] * FPS)
    p["in"], p["out"], p["time"] = fi * FRAME, fo * FRAME, t * FRAME
    t += fo - fi

# Premiere snaps source outs to the source frame grid (e.g. 59.94 inside a 23.976 sequence) and leaves
# 1-frame holes; overshoot each out by one sequence frame -- the next clip (overwrite mode) covers it.
batch = [{"projectItemId": ids[p["file"]], "trackIndex": 0, "time": round(p["time"], 6),
          "sourceInPoint": round(p["in"], 6),
          "sourceOutPoint": round(p["out"] + (FRAME if k + 1 < len(pieces) else 0), 6)}
         for k, p in enumerate(pieces)]

json.dump({"pieces": pieces, "report": report, "total": t * FRAME}, open(os.path.join(work, f"cuts{SUFFIX}.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(batch, open(os.path.join(work, f"batch{SUFFIX}.json"), "w"), separators=(",", ":"))
for r in report:
    print(f"{r['file']} {r['in']:7.2f}-{r['out']:7.2f}  [{r['pieces']} pç, -{r['silence_removed']:.1f}s]  {r['block']}")
    print("    " + r["text"])
print(f"\n{len(pieces)} pedaços, total {t * FRAME / 60:.2f} min -> batch{SUFFIX}.json")
