"""Mapeia as falas de uma decupagem para quem vai montar a estrutura de um mini-documentário.

Uso: python -P mapa_falas.py <work> [--sel selection.json] [--parecidas 0.45]

Este script MAPEIA. Ele não ordena nada: quem propõe a ordem é a /estruturador, e quem aprova é o
Pedro. Nasceu do Novais Arquitetura, onde 36 min de bruto viraram 8 min 25 s sem roteiro nenhum: a
estrutura saiu da cabeça do Pedro e não estava escrita em lugar nenhum.

Por fala, calcula:
  dur            quanto tempo ela ocupa
  acumulado      quanto tempo passou até o fim dela, na ordem atual
  numero         tem número dito (serve de prova, e é candidata a motion)
  nome           tem nome próprio no meio da frase (lugar, produto, pessoa)
  virada         começa ou vira com "mas", "só que", "porém", "no entanto", "aí", "só agora"
  pergunta       termina em pergunta (quase sempre é o entrevistador, ou uma frase improvisada)
  tempo          cita ano, década ou "há N anos"

E aponta pares de falas com vocabulário parecido ("ideias repetidas"). Regra do Pedro: ideias
repetidas por pessoas diferentes ficam todas, ele escolhe na montagem. Aqui é só aviso.

Escreve <work>/mapa-falas.json e imprime uma tabela.
"""
import json, os, re, sys, unicodedata

sys.stdout.reconfigure(encoding="utf-8")

VIRADA = ("mas ", "só que", "porem", "porém", "no entanto", "entretanto", "aí ", "ai ", "só agora",
          "acontece que", "o problema", "a verdade")
TEMPO = re.compile(r"\b(19\d{2}|20\d{2}|h[aá]\s+\w+\s+anos?|d[eé]cada)\b", re.I)
NUM_PALAVRA = re.compile(r"\b(um|dois|tr[eê]s|quatro|cinco|seis|sete|oito|nove|dez|vinte|trinta|"
                         r"cem|mil|milh[oõ]es?|milh[aã]o|bilh[oõ]es?|por\s*cento)\b", re.I)
PAREI = set("""a o as os um uma uns umas de do da dos das em no na nos nas por para com sem sob
e ou que se ja já mais muito muita pouco tudo todo toda isso isto aquilo ele ela eles elas eu voce
você nos nós meu minha seu sua nosso nossa foi era e_ ser estar tem ter tinha tambem também aqui
ali la lá ne né tipo entao então assim quando como onde porque pois mesmo cada bem""".split())


def limpo(t):
    t = unicodedata.normalize("NFD", (t or "").lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]+", " ", t)


def tokens(t):
    return {p for p in limpo(t).split() if len(p) > 3 and p not in PAREI}


def parecido(a, b):
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0
    return round(len(ta & tb) / len(ta | tb), 3)


def marcas(texto):
    t = texto or ""
    baixo = " " + limpo(t) + " "
    meio = " ".join(t.split()[1:])                       # ignora a 1ª palavra, que é sempre maiúscula
    return {
        "numero": bool(re.search(r"\d", t)) or bool(NUM_PALAVRA.search(t)),
        "nome": bool(re.search(r"\b[A-ZÀ-Ý][a-zà-ÿ]{2,}", meio)),
        "virada": any(v in baixo for v in VIRADA),
        "pergunta": t.strip().endswith("?"),
        "tempo": bool(TEMPO.search(t)),
    }


args = sys.argv[1:]
def opt(n, p=None):
    if n in args:
        i = args.index(n); v = args[i + 1]; del args[i:i + 2]; return v
    return p

SEL = opt("--sel", "selection.json")
LIMITE = float(opt("--parecidas", "0.45"))
work = args[0]

caminho = os.path.join(work, SEL)
if not os.path.exists(caminho):
    raise SystemExit(f"não achei {caminho}: rode a decupagem primeiro")
sel = json.load(open(caminho, encoding="utf-8"))

falas, acum = [], 0.0
for k, s in enumerate(sel):
    dur = round(float(s["end"]) - float(s["start"]), 2)
    acum = round(acum + dur, 2)
    texto = (s.get("texto") or s.get("text") or "").strip()
    falas.append({"i": k, "bloco": s.get("block", ""), "file": s["file"],
                  "start": float(s["start"]), "end": float(s["end"]),
                  "dur": dur, "acumulado": acum, "texto": texto, "marcas": marcas(texto)})

pares = []
for a in range(len(falas)):
    for b in range(a + 1, len(falas)):
        v = parecido(falas[a]["texto"], falas[b]["texto"])
        if v >= LIMITE:
            pares.append({"a": a, "b": b, "parecenca": v})
pares.sort(key=lambda p: -p["parecenca"])

total = falas[-1]["acumulado"] if falas else 0.0
json.dump({"total_s": total, "total_min": round(total / 60, 2), "limite_parecidas": LIMITE,
           "falas": falas, "parecidas": pares},
          open(os.path.join(work, "mapa-falas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print(f"{len(falas)} falas, {total/60:.2f} min na ordem atual\n")
for f in falas:
    m = f["marcas"]
    sinais = "".join([" nº" if m["numero"] else "   ", " nome" if m["nome"] else "     ",
                      " VIRADA" if m["virada"] else "       ", " ?" if m["pergunta"] else "  ",
                      " ano" if m["tempo"] else "    "])
    print(f"{f['i']:3}  {f['dur']:6.2f}s  {f['acumulado']/60:5.2f}min {sinais}  {f['texto'][:70]}")
if pares:
    print(f"\nIdeias parecidas (ficam todas; o Pedro escolhe na montagem):")
    for p in pares[:12]:
        print(f"  {p['a']} e {p['b']}: {p['parecenca']:.0%} do vocabulário em comum")
        print(f"      {p['a']}: {falas[p['a']]['texto'][:62]}")
        print(f"      {p['b']}: {falas[p['b']]['texto'][:62]}")
print(f"\n-> mapa-falas.json")
