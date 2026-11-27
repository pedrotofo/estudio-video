"""Trava contra fala inventada: confere se o texto de cada trecho escolhido existe na transcrição.

Uso: python -P checar_selecao.py <work_dir> [--sel selection.json]

Cada item do selection.json precisa de "texto": a fala como você vai mostrar no roteiro decupado.
O script pega as palavras que a transcrição tem entre "start" e "end" daquele arquivo e compara.
  OK       o texto bate com o que foi dito (diferença só de pontuação ou grafia)
  DIVERGE  o texto escrito não é o que está na transcrição: corrija o "texto" (ou o start/end) e rode de novo
  SEM TEXTO  falta o campo "texto"
Sai com código 1 se houver DIVERGE ou SEM TEXTO. Rode antes de mostrar o roteiro decupado ao Pedro.
"""
import json, os, re, sys, unicodedata
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding="utf-8")
args = sys.argv[1:]
sel_nome = "selection.json"
if "--sel" in args:
    i = args.index("--sel"); sel_nome = args[i + 1]; del args[i:i + 2]
work = args[0]
sel = json.load(open(os.path.join(work, sel_nome), encoding="utf-8"))
gaps_path = os.path.join(work, "gaps.json")
recuperadas = json.load(open(gaps_path, encoding="utf-8")) if os.path.exists(gaps_path) else []

cache = {}
def palavras(nome):
    if nome not in cache:
        d = json.load(open(os.path.join(work, "tr", nome + ".json"), encoding="utf-8"))
        ws = [w for s in d["segments"] for w in s["words"]]
        extra = [w for r in recuperadas if r["file"] == nome for w in r["words"]
                 if not any(w["s"] < o["e"] and w["e"] > o["s"] for o in ws)]
        cache[nome] = sorted(ws + extra, key=lambda w: w["s"])
    return cache[nome]

def toks(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return [x for x in re.split(r"[^a-z0-9]+", t) if x]

ruins = 0
for k, s in enumerate(sel, 1):
    # conta a palavra que encosta no trecho: o Whisper estica a 1ª palavra para trás (por cima da contagem)
    ditas = " ".join(w["w"].strip() for w in palavras(s["file"]) if w["e"] > s["start"] + 0.05 and w["s"] < s["end"] - 0.05)
    escrito = s.get("texto", "").strip()
    rot = f"{k:>2}. {s.get('block', '')} | {s['file']} {s['start']:.2f}-{s['end']:.2f}"
    if not escrito:
        ruins += 1; print(f"SEM TEXTO  {rot}\n           transcrição: \"{ditas}\""); continue
    a, b = toks(escrito), toks(ditas)
    sm = SequenceMatcher(a=a, b=b, autojunk=False)
    nota = sm.ratio()
    if nota >= 0.9:
        print(f"OK {nota * 100:3.0f}%   {rot}")
        continue
    ruins += 1
    dif = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != "equal":
            dif.append(f"escrito \"{' '.join(a[i1:i2])}\" / dito \"{' '.join(b[j1:j2])}\"")
    print(f"DIVERGE {nota * 100:3.0f}%  {rot}\n           escrito:     \"{escrito}\"\n           transcrição: \"{ditas}\"\n           diferenças:  " + "; ".join(dif[:6]))

print(f"\n{len(sel) - ruins} de {len(sel)} trechos conferidos com a transcrição." + ("" if not ruins else f" {ruins} para corrigir antes do roteiro decupado."))
sys.exit(1 if ruins else 0)
