"""Write the files the other Estúdio skills read (/ilustrar-fala, /premiere-xml), in the time of the Limpa sequence.

Usage: python -P para_estudio.py <work_dir> <seq_fps> <saida_decup> [--midia "<caminho>"] [--cliente "<nome>"]

Reads  <work_dir>/cuts.json  (from build_cuts.py: pieces with file, in, out, time on the Limpa timeline)
       <work_dir>/tr/*.json  (from whisperx_to_tr.py or transcribe.py)
Writes <saida_decup>/transcricao.json  {"midia","fps","duracao","segmentos":[{"id","inicio","fim","texto","palavras":[{"p","inicio","fim","conf"}]}]}
       <saida_decup>/legenda.srt       one line per block of up to ~32 characters (Pedro's rule: captions are always one line)
       <saida_decup>/decupagem.json   skeleton in references/formato.md: midia, fps, duracao, trechos (one per piece).
                                       "ilustracoes" and "conferir" start empty: Claude fills them in step 15.
Times are seconds on the Limpa timeline, so a word found here is where it plays in the sequence.
Only words that fall inside a kept piece are written (cut pauses and other takes are left out).
"""
import glob, json, os, sys

args = sys.argv[1:]
def opt(name, default=""):
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
    return default
midia = opt("--midia"); cliente = opt("--cliente")
work, fps, out = args[0], float(args[1]), args[2]
os.makedirs(out, exist_ok=True)

cuts = json.load(open(os.path.join(work, "cuts.json"), encoding="utf-8"))
tr = {}
for p in glob.glob(os.path.join(work, "tr", "*.json")):
    d = json.load(open(p, encoding="utf-8"))
    tr[d["file"]] = d


def tc(t):
    f = int(round(t * fps)); fr = int(round(fps))
    return f"{f // (3600 * fr):02d}:{f // (60 * fr) % 60:02d}:{f // fr % 60:02d}:{f % fr:02d}"


segmentos, trechos = [], []
for k, piece in enumerate(cuts["pieces"]):
    d = tr.get(piece["file"])
    if not d:
        print(f"  aviso: sem transcrição para {piece['file']}", file=sys.stderr); continue
    a, b, t0 = piece["in"], piece["out"], piece["time"]
    palavras = []
    for s in d["segments"]:
        for w in s["words"]:
            meio = (w["s"] + w["e"]) / 2
            if a <= meio <= b:
                ini = t0 + max(w["s"], a) - a
                fim = t0 + min(w["e"], b) - a
                palavras.append({"p": w["w"].strip(), "inicio": round(ini, 3), "fim": round(fim, 3),
                                 "conf": w.get("p", 0.0)})
    if not palavras:
        continue
    texto = " ".join(w["p"] for w in palavras)
    seg = {"id": len(segmentos) + 1, "inicio": palavras[0]["inicio"], "fim": palavras[-1]["fim"],
           "texto": texto, "palavras": palavras, "arquivo": piece["file"], "bloco": piece.get("block", "")}
    segmentos.append(seg)
    trechos.append({"id": f"T{seg['id']}", "inicio": seg["inicio"], "fim": seg["fim"],
                    "tc_in": tc(seg["inicio"]), "tc_out": tc(seg["fim"]), "tema": seg["bloco"],
                    "texto": texto, "nota": 2, "uso": "meio", "obs": f"{piece['file']} {a:.2f}-{b:.2f}"})

duracao = round(cuts.get("total", segmentos[-1]["fim"] if segmentos else 0), 3)
json.dump({"midia": midia, "fps": fps, "duracao": duracao, "segmentos": segmentos},
          open(os.path.join(out, "transcricao.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"midia": midia, "fps": fps, "duracao": duracao, "cliente": cliente, "resumo": "",
           "trechos": trechos, "ilustracoes": [], "conferir": []},
          open(os.path.join(out, "decupagem.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# one-line captions: break at ~32 characters, preferring a comma or a pause of 0.3 s or more
def srt_t(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

blocos, atual = [], []
todas = [w for s in segmentos for w in s["palavras"]]
for i, w in enumerate(todas):
    atual.append(w)
    txt = " ".join(x["p"] for x in atual)
    prox = todas[i + 1] if i + 1 < len(todas) else None
    pausa = prox is None or prox["inicio"] - w["fim"] >= 0.3
    virgula = w["p"].endswith((",", ".", "?", "!", ":", ";"))
    cabe_mais = prox is not None and len(txt) + 1 + len(prox["p"]) <= 32
    if prox is None or not cabe_mais or pausa or (virgula and len(txt) >= 14):
        blocos.append(atual); atual = []
with open(os.path.join(out, "legenda.srt"), "w", encoding="utf-8") as f:
    for n, bl in enumerate(blocos, 1):
        f.write(f"{n}\n{srt_t(bl[0]['inicio'])} --> {srt_t(bl[-1]['fim'])}\n{' '.join(x['p'] for x in bl)}\n\n")

print(f"{len(segmentos)} trechos, {len(todas)} palavras, {len(blocos)} legendas, {duracao:.2f} s -> {out}")
