"""Acha e guarda as pastas do Estúdio, para nunca perguntar duas vezes.

Uso: python -P pastas.py                      mostra o que já está guardado
     python -P pastas.py --procurar           procura e guarda se achar uma só
     python -P pastas.py --definir "<caminho>"  grava a pasta do Claude à mão
     python -P pastas.py --raiz "<caminho>"     grava a raiz dos jobs à mão

O que fica guardado em ~/.claude/estudio-video.json:
  raiz_jobs      onde moram os jobs (no computador do Pedro: D:\\Jobs)
  pasta_claude   a pasta de trabalho do Claude (confirmada em 28/11/2026: D:\\Jobs\\_Claude)

Por que procurar em vez de fixar o caminho: a letra do disco muda (o SSD "E:" dos guias do Riomar
e da Diamantes nem sempre aparece), e a pasta começa com underscore, então um filtro ingênuo por
"Claude*" não acha. Aqui o nome só precisa conter "claude", em qualquer caixa.
"""
import json, os, sys

CONF = os.path.join(os.path.expanduser("~"), ".claude", "estudio-video.json")
sys.stdout.reconfigure(encoding="utf-8")


def ler():
    try:
        with open(CONF, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def gravar(c):
    os.makedirs(os.path.dirname(CONF), exist_ok=True)
    with open(CONF, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=1)
    return c


def raizes(conf):
    """Onde procurar, em ordem. A raiz guardada manda; depois os lugares prováveis."""
    fora = []
    if conf.get("raiz_jobs"):
        fora.append(conf["raiz_jobs"])
    if os.name == "nt":
        fora += [f"{d}:\\Jobs" for d in "DEFCG"]
    casa = os.path.expanduser("~")
    fora += [os.path.join(casa, "Jobs"), os.path.join(casa, "jobs"), "/mnt/d/Jobs"]
    vistos, limpas = set(), []
    for r in fora:
        if r and r not in vistos and os.path.isdir(r):
            vistos.add(r); limpas.append(r)
    return limpas


def candidatas(raiz):
    """Pastas com 'claude' no nome, na raiz ou um nível abaixo (pasta por job)."""
    achadas = []
    try:
        for nome in sorted(os.listdir(raiz)):
            cheio = os.path.join(raiz, nome)
            if not os.path.isdir(cheio):
                continue
            if "claude" in nome.lower():
                achadas.append(cheio)
                continue
            try:
                for dentro in sorted(os.listdir(cheio)):
                    if "claude" in dentro.lower() and os.path.isdir(os.path.join(cheio, dentro)):
                        achadas.append(os.path.join(cheio, dentro))
            except OSError:
                pass
    except OSError:
        pass
    return achadas


args = sys.argv[1:]
conf = ler()

def opcao(nome):
    if nome in args:
        i = args.index(nome)
        if i + 1 >= len(args):
            raise SystemExit(f"falta o caminho depois de {nome}")
        v = args[i + 1]; del args[i:i + 2]; return v
    return None

definir, raiz_mao = opcao("--definir"), opcao("--raiz")
if raiz_mao:
    if not os.path.isdir(raiz_mao):
        raise SystemExit(f"não existe: {raiz_mao}")
    conf = gravar({**conf, "raiz_jobs": raiz_mao}); print(f"raiz dos jobs: {raiz_mao}")
if definir:
    if not os.path.isdir(definir):
        raise SystemExit(f"não existe: {definir}")
    conf = gravar({**conf, "pasta_claude": definir}); print(f"pasta do Claude: {definir}")

if "--procurar" in args:
    rs = raizes(conf)
    if not rs:
        print("Nenhuma raiz de jobs encontrada. Pergunte ao Pedro e grave com --raiz.")
        sys.exit(2)
    achadas = []
    for r in rs:
        achadas += candidatas(r)
    if len(achadas) == 1:
        conf = gravar({**conf, "pasta_claude": achadas[0], "raiz_jobs": conf.get("raiz_jobs") or rs[0]})
        print(f"achei uma só e guardei: {achadas[0]}")
    elif achadas:
        print("Mais de uma pasta com 'claude' no nome. Pergunte ao Pedro qual é e grave com --definir:")
        for a in achadas:
            print("  " + a)
        sys.exit(2)
    else:
        print(f"Nenhuma pasta com 'claude' no nome em: {', '.join(rs)}")
        print("Pergunte ao Pedro (uma vez só) e grave com --definir.")
        sys.exit(2)

if not args or args == ["--procurar"]:
    conf = ler()
    print(f"arquivo: {CONF}")
    print(f"  raiz_jobs    = {conf.get('raiz_jobs') or '(não definida)'}")
    print(f"  pasta_claude = {conf.get('pasta_claude') or '(não definida)'}")
    sys.exit(0 if conf.get("pasta_claude") else 2)
