"""Confere as duas pontas de cada pedaço do corte, medindo pelo som (nunca pela transcrição).

Uso: python -P pontas.py <work_dir> [--cuts cuts.json]

Nasceu da reclamação de 24/11/2026 (Treinamento Nov26 da Diamantes): várias falas terminaram
cortadas e o take seguinte começou com silêncio até a pessoa falar, e o Pedro teve de ajustar
clipe por clipe. A regra dele: o fim de um clipe cai ~0,25 s depois da voz (nunca no meio dela) e
o começo do seguinte cai no ataque da voz, com no máximo ~0,05 s de silêncio antes.

Mede, para cada pedaço do cuts.json, sobre o wav original:
  respiro_fim       quanto tempo depois da última voz o pedaço termina
  silencio_inicio   quanto silêncio existe entre o começo do pedaço e a primeira voz
  quieto_antes      quanto silêncio existe logo ANTES do pedaço (pouco = contagem ou fala colada)

Só as pontas de verdade de cada fala seguem a regra apertada. Fronteira de pausa interna (o
build_cuts tira a pausa deixando PAD de 0,15 s dos dois lados) é medida, mas com a folga dela.

Escreve <work>/pontas.json e imprime um resumo em português. Sai com código 1 se houver GRAVE.
"""
import json, os, sys
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
# o envelope é o mesmo do build_cuts.py: uma conta só, para as duas skills nunca discordarem
COMUM = os.path.normpath(os.path.join(AQUI, "..", "..", "decupagem-falas-premiere", "scripts"))
if not os.path.exists(os.path.join(COMUM, "common.py")):
    raise SystemExit(f"common.py não encontrado em {COMUM}: instale a /decupagem-falas-premiere junto")
sys.path.insert(0, COMUM)
from common import envelope  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
args = sys.argv[1:]
CUTS = "cuts.json"
if "--cuts" in args:
    i = args.index("--cuts"); CUTS = args[i + 1]; del args[i:i + 2]
work = args[0]

H = 0.01            # quadros de 10 ms, como o fim do build_cuts (20 ms perdia finais fracos)
VOZ = 12            # voz = piso local + 12 dB
JANELA = 2.0        # o piso local sai dos 2 s em volta do ponto medido
TAIL = 0.25         # o respiro que o build_cuts deixa depois da voz
PAD = 0.15          # a folga que ele deixa dos dois lados de uma pausa interna
GAP = 0.25          # silêncio que separa a contagem da fala

CORTOU = 0.10       # respiro menor que isto = o corte comeu o fim da palavra
LONGO = 0.60        # respiro maior que isto = sobra ar no fim
ATRASO = 0.12       # silêncio maior que isto no começo de uma fala = o clipe entra antes da voz

cache = {}
def som(nome):
    if nome not in cache:
        caminho = os.path.join(work, "wav", nome + ".wav")
        if not os.path.exists(caminho):
            raise SystemExit(f"wav não encontrado: {caminho}")
        d = envelope(caminho, hop_s=H)[0]
        cache[nome] = (np.convolve(d, np.ones(5) / 5, mode="same"), len(d) * H)  # 50 ms: estalo não é voz
    return cache[nome]


def piso(sm, centro):
    a, b = int(max(0, centro - JANELA) / H), int(min(len(sm) * H, centro + JANELA) / H)
    return np.percentile(sm[a:b], 20) if b > a else -60.0


def ultima_voz(sm, ate, desde):
    """Último instante com voz em [desde, ate]. None se não houver voz nessa janela."""
    lim = piso(sm, ate) + VOZ
    a, b = int(max(0, desde) / H), min(len(sm), int(ate / H))
    for k in range(b - 1, a - 1, -1):
        if sm[k] >= lim:
            return (k + 1) * H
    return None


def primeira_voz(sm, de, ate):
    lim = piso(sm, de) + VOZ
    a, b = max(0, int(de / H)), min(len(sm), int(ate / H))
    for k in range(a, b):
        if sm[k] >= lim:
            return k * H
    return None


dados = json.load(open(os.path.join(work, CUTS), encoding="utf-8"))
pecas = dados["pieces"]

# pontas de verdade: primeiro e último pedaço de cada sequência de pedaços do mesmo arquivo e bloco
grupo = []
for k, p in enumerate(pecas):
    anterior = pecas[k - 1] if k else None
    novo = anterior is None or (p["file"], p.get("block", "")) != (anterior["file"], anterior.get("block", ""))
    if novo:
        grupo.append([])
    grupo[-1].append(k)
entrada = {g[0] for g in grupo}
saida = {g[-1] for g in grupo}

saidas, graves, avisos = [], 0, 0
for k, p in enumerate(pecas):
    sm, dur = som(p["file"])
    ini, fim = float(p["in"]), float(p["out"])
    e_entrada, e_saida = k in entrada, k in saida

    uv = ultima_voz(sm, fim, fim - JANELA)
    respiro = round(fim - uv, 3) if uv is not None else None
    pv = primeira_voz(sm, ini, min(ini + JANELA, dur))
    silencio = round(pv - ini, 3) if pv is not None else None
    av = ultima_voz(sm, ini, max(0.0, ini - 0.6))
    quieto_antes = round(ini - av, 3) if av is not None else None

    notas = []
    if respiro is None:
        notas.append(("AVISO", "sem voz nos 2 s antes do fim: pedaço só de pausa?"))
    elif respiro < CORTOU:
        notas.append(("GRAVE", f"o corte termina {respiro:.2f} s depois da voz: está comendo o fim da palavra"))
    elif e_saida and respiro > LONGO:
        notas.append(("AVISO", f"sobra {respiro:.2f} s de ar depois da última palavra"))
    elif not e_saida and respiro > PAD + 0.25:
        notas.append(("AVISO", f"pausa interna com {respiro:.2f} s de ar antes do corte"))

    folga = ATRASO if e_entrada else PAD + 0.12
    if silencio is None:
        notas.append(("AVISO", "sem voz nos 2 s depois do começo: pedaço só de pausa?"))
    elif silencio > folga:
        notas.append(("GRAVE" if e_entrada else "AVISO",
                      f"o clipe começa {silencio:.2f} s antes da voz" if e_entrada
                      else f"{silencio:.2f} s de silêncio no começo do pedaço"))

    if e_entrada and quieto_antes is not None and quieto_antes < GAP:
        notas.append(("AVISO", f"só {quieto_antes:.2f} s de silêncio antes do clipe: pode ser contagem "
                               "ou fala colada — conferir no ouvido"))

    for nivel, _ in notas:
        if nivel == "GRAVE":
            graves += 1
        else:
            avisos += 1
    saidas.append({"i": k, "file": p["file"], "block": p.get("block", ""), "in": round(ini, 3), "out": round(fim, 3),
                   "ponta_entrada": e_entrada, "ponta_saida": e_saida, "respiro_fim": respiro,
                   "silencio_inicio": silencio, "quieto_antes": quieto_antes,
                   "notas": [{"nivel": n, "texto": t} for n, t in notas]})

json.dump({"alvo": {"respiro_fim": TAIL, "silencio_inicio_max": ATRASO}, "pecas": saidas},
          open(os.path.join(work, "pontas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

for s in saidas:
    if not s["notas"]:
        continue
    marca = "entrada" if s["ponta_entrada"] else ("saída" if s["ponta_saida"] else "interna")
    print(f"{s['file']} {s['in']:7.2f}-{s['out']:7.2f}  ({marca})  {s['block']}")
    for n in s["notas"]:
        print(f"    {n['nivel']}: {n['texto']}")
print(f"\n{len(saidas)} pedaços conferidos: {graves} graves, {avisos} avisos -> pontas.json")
sys.exit(1 if graves else 0)
