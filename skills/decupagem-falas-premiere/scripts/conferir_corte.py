"""Confere o corte montado ouvindo de novo, e mede o volume.

Uso: python -P conferir_corte.py <work_dir> [--cuts cuts.json] [--alvo -14]
     python -P conferir_corte.py --arquivo "<exportado.mp4>" [--alvo -14]   (só o volume de um arquivo pronto)

1. Monta o áudio da sequência exatamente como o cuts.json manda (os mesmos pedaços que foram para o Premiere),
   a partir de <work>/wav, e grava <work>/conferencia.wav.
2. Transcreve esse áudio de novo (faster-whisper large-v3 na GPU) e compara com as palavras que deveriam estar lá
   (as da transcrição original dentro de cada pedaço). Palavra que sumiu perto de uma emenda = EMENDA (quase sempre
   corte comendo a palavra); longe da emenda = CONFERIR (pode ser só o Whisper ouvindo diferente).
3. Mede o volume integrado (LUFS) e o pico, e diz quanto subir ou baixar para chegar no alvo (Reels/TikTok/YouTube: -14).
   Medida do áudio bruto da câmera: serve de guia; o número que vale é o do arquivo exportado (--arquivo).
Escreve <work>/conferencia.json e imprime um resumo em português.
"""
import json, os, re, subprocess, sys, unicodedata, wave
from difflib import SequenceMatcher
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -P tira a pasta do script do sys.path
from common import enable_cuda_dlls, ffmpeg, load_wav

sys.stdout.reconfigure(encoding="utf-8")
args = sys.argv[1:]
def opt(nome, padrao=None):
    if nome in args:
        i = args.index(nome); v = args[i + 1]; del args[i:i + 2]; return v
    return padrao
ALVO = float(opt("--alvo", "-14"))
ARQUIVO = opt("--arquivo")
CUTS = opt("--cuts", "cuts.json")
EMENDA = 0.6   # palavra a até 0,6 s de uma emenda conta como problema de emenda


def volume(caminho):
    r = subprocess.run([ffmpeg(), "-nostdin", "-hide_banner", "-i", caminho, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    txt = r.stderr[r.stderr.rfind("Summary:"):]
    lufs = re.search(r"I:\s+(-?[\d.]+) LUFS", txt)
    pico = re.search(r"Peak:\s+(-?[\d.]+) dBFS", txt)
    return (float(lufs.group(1)) if lufs else None), (float(pico.group(1)) if pico else None)


def frase_volume(lufs, pico):
    if lufs is None:
        return "Não consegui medir o volume."
    dif = ALVO - lufs
    s = f"Volume: {lufs:.1f} LUFS (alvo {ALVO:.0f})" + (f", pico {pico:.1f} dB" if pico is not None else "") + ". "
    if abs(dif) < 1:
        s += "Já está no padrão."
    elif dif > 0:
        s += f"Está baixo: suba uns {dif:.0f} dB no master."
        if pico is not None and pico + dif > -1:
            s += " Subindo isso o pico passa de -1 dB: use um limitador no master."
    else:
        s += f"Está alto: baixe uns {-dif:.0f} dB no master."
    return s


if ARQUIVO:
    l, p = volume(ARQUIVO)
    print(frase_volume(l, p))
    sys.exit(0)

work = args[0]
cuts = json.load(open(os.path.join(work, CUTS), encoding="utf-8"))
pecas = cuts["pieces"]
gaps_path = os.path.join(work, "gaps.json")
recuperadas = json.load(open(gaps_path, encoding="utf-8")) if os.path.exists(gaps_path) else []

cache = {}
def fonte(nome):
    if nome not in cache:
        d = json.load(open(os.path.join(work, "tr", nome + ".json"), encoding="utf-8"))
        ws = [w for s in d["segments"] for w in s["words"]]
        extra = [w for r in recuperadas if r["file"] == nome for w in r["words"]
                 if not any(w["s"] < o["e"] and w["e"] > o["s"] for o in ws)]
        x, sr = load_wav(os.path.join(work, "wav", nome + ".wav"))
        cache[nome] = (sorted(ws + extra, key=lambda w: w["s"]), x, sr)
    return cache[nome]


def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "", t)


# 1. monta o áudio e a lista do que deveria estar lá
partes, esperadas, emendas, t = [], [], [], 0.0
for k, p in enumerate(pecas):
    ws, x, sr = fonte(p["file"])
    a, b = p["in"], p["out"]
    partes.append(x[int(a * sr):int(b * sr)])
    for w in ws:
        # toda palavra que encosta no pedaço entra; a que fica mais fora do que dentro é "borda":
        # se sumir, não é problema (o Whisper estica a 1ª palavra para trás e a última para frente)
        dentro = min(w["e"], b) - max(w["s"], a)
        if dentro > 0.02 and norm(w["w"]):
            borda = dentro < 0.5 * max(w["e"] - w["s"], 0.01)
            esperadas.append({"w": w["w"].strip(), "n": norm(w["w"]), "t": round(t + max(w["s"], a) - a, 2), "peca": k, "borda": borda})
    if k: emendas.append(round(t, 2))
    t += b - a
audio = np.concatenate(partes) if partes else np.zeros(1, np.float32)
saida_wav = os.path.join(work, "conferencia.wav")
with wave.open(saida_wav, "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(16000)
    f.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())

# 2. transcreve de novo e compara
enable_cuda_dlls()
from faster_whisper import WhisperModel
try:
    model = WhisperModel("large-v3", device="cuda", compute_type="float16")
except Exception:
    model = WhisperModel("medium", device="cpu", compute_type="int8")
# meio segundo de silêncio nas pontas, só para transcrever: o Whisper perde palavra colada no começo ou no fim do áudio
PAD = 0.5
pad = np.zeros(int(PAD * 16000), np.float32)
segs, _ = model.transcribe(np.concatenate([pad, audio, pad]), language="pt", word_timestamps=True,
                           condition_on_previous_text=False, beam_size=5)
ouvidas = [{"w": w.word.strip(), "n": norm(w.word), "t": round(max(0.0, w.start - PAD), 2)} for s in segs for w in (s.words or []) if norm(w.word)]

if "--detalhe" in sys.argv:
    print("esperadas:", [(w["w"], w["t"], "borda" if w["borda"] else "") for w in esperadas])
    print("ouvidas:  ", [(w["w"], w["t"]) for w in ouvidas])
    print("pedaços:  ", [(p["in"], p["out"]) for p in pecas])
# A referência é o texto aprovado de cada fala ("texto" no selection, conferido pelo checar_selecao.py):
# os tempos de palavra do Whisper erram justamente na borda das falas, onde o corte acontece.
sel_nome = opt("--sel") or ("selection" + CUTS[len("cuts"):] if CUTS.startswith("cuts") else "selection.json")
sel_path = os.path.join(work, sel_nome)
sel = json.load(open(sel_path, encoding="utf-8")) if os.path.exists(sel_path) else []
if sel and all(s.get("texto") for s in sel):
    ref = "textos aprovados"
    esperadas = [{"w": x, "n": norm(x), "t": None, "borda": False} for s in sel for x in s["texto"].split() if norm(x)]
else:
    ref = "transcrição original (o selection não tem \"texto\": rode o checar_selecao.py)"

def tempo(i_esp, j_ouv):
    if esperadas[i_esp:i_esp + 1] and esperadas[i_esp]["t"] is not None:
        return esperadas[i_esp]["t"]
    if j_ouv < len(ouvidas): return ouvidas[j_ouv]["t"]
    return ouvidas[-1]["t"] if ouvidas else 0.0

perto = lambda tt: min((abs(tt - e) for e in emendas + [0.0, t]), default=99) <= EMENDA   # o começo e o fim também são cortes
problemas = []
sm = SequenceMatcher(a=[w["n"] for w in esperadas], b=[w["n"] for w in ouvidas], autojunk=False)
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op == "equal":
        continue
    faltou = esperadas[i1:i2]
    sobrou = ouvidas[j1:j2]
    if not sobrou and faltou and all(w["borda"] for w in faltou):
        continue   # só palavra de borda, mais fora do que dentro do corte: sumir é o esperado
    tt = tempo(i1, j1) if faltou else sobrou[0]["t"]
    tipo = "EMENDA" if perto(tt) or perto(tempo(i2 - 1, j2) if faltou else sobrou[-1]["t"]) else "CONFERIR"
    if op == "replace" and len(faltou) == len(sobrou) == 1 and SequenceMatcher(a=faltou[0]["n"], b=sobrou[0]["n"]).ratio() > .75:
        continue   # só grafia diferente ("pra"/"para", número por extenso)
    problemas.append({"tipo": tipo, "tempo": tt, "faltou": " ".join(w["w"] for w in faltou), "ouvi": " ".join(w["w"] for w in sobrou)})

lufs, pico = volume(saida_wav)
acerto = sm.ratio()
json.dump({"acerto": round(acerto, 3), "emendas": emendas, "problemas": problemas, "lufs": lufs, "pico": pico, "alvo": ALVO},
          open(os.path.join(work, "conferencia.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

mmss = lambda s: f"{int(s // 60)}:{s % 60:05.2f}"
print(f"Sequência de {mmss(t)} com {len(pecas)} pedaços e {len(emendas)} emendas. Comparei com: {ref}. Texto igual: {acerto * 100:.0f}%.")
emp = [p for p in problemas if p["tipo"] == "EMENDA"]
outros = [p for p in problemas if p["tipo"] == "CONFERIR"]
if emp:
    print(f"\nEMENDAS COM PALAVRA FALTANDO OU SOBRANDO ({len(emp)}): corrija antes de entregar")
    for p in emp:
        print(f"  {mmss(p['tempo'])}  faltou: \"{p['faltou']}\"  ouvi: \"{p['ouvi']}\"")
if outros:
    print(f"\nPARA CONFERIR NO OUVIDO ({len(outros)}): longe das emendas, pode ser só o Whisper")
    for p in outros[:30]:
        print(f"  {mmss(p['tempo'])}  esperado: \"{p['faltou']}\"  ouvi: \"{p['ouvi']}\"")
if not problemas:
    print("Nenhuma palavra comida nas emendas.")
print("\n" + frase_volume(lufs, pico) + " (áudio bruto da câmera; meça o exportado com --arquivo)")
