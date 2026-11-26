"""Caravela Color — comando único do balance de uma edição.

Faz, em sequência, a parte que não precisa do Premiere:
  1. lê a timeline (XML FCP7 exportado do Premiere) -> cortes com arquivo e trecho usado
  2. mede cada corte e calcula exposição + branco no log (ordem profissional), escolhe o hero
  3. gera uma LUT por corte de câmera (correção + conversão Rec.709) e o CDL dos cortes Rec.709 (drone)
  4. monta a prévia antes/depois para o usuário aprovar
  5. escreve o plano de aplicação (o que o Claude vai mandar ao Premiere) e um relatório curto

Uso:
  python caravela.py balance --xml <timeline.xml> --saida <pasta> --lut-conversao <S-Log3->709.cube>
                             --pasta-luts <pasta das LUTs> [--ids <ids.txt>] [--titulo "nome"]
  ids.txt (opcional): IDs dos clipes da faixa V1 da cópia no Premiere, na ordem, um por linha
  (inclui aninhadas). Sem ele, o plano sai sem IDs e o Claude preenche depois.
"""
import argparse, json, os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def rodar(script, *args):
    r = subprocess.run([PY, os.path.join(AQUI, script), *map(str, args)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if r.returncode != 0:
        print(r.stdout[-2000:]); print(r.stderr[-3000:])
        raise SystemExit(f"falhou: {script}")
    return r.stdout


def balance(a):
    os.makedirs(a.saida, exist_ok=True)
    cortes = os.path.join(a.saida, "cortes.json")
    print("1/5 lendo a timeline ...")
    print("   ", rodar("timeline_xml.py", a.xml, cortes).splitlines()[0])
    n = len(json.load(open(cortes, encoding="utf-8")))
    ids = a.ids
    if not ids:
        ids = os.path.join(a.saida, "ids_vazios.txt")
        open(ids, "w").write("\n".join(f"sem-id-{i:02d}" for i in range(n)) + "\n")
    print(f"2/5 medindo {n} cortes e calculando exposição + branco (pode levar alguns minutos) ...")
    saida_bal = rodar("balance_edit.py", cortes, ids, a.saida, a.lut_conversao, a.pasta_luts)
    linhas = [l for l in saida_bal.splitlines() if l.startswith(("HERO", "exposição", "temperatura"))]
    for l in linhas:
        print("   ", l)
    print("3/5 LUTs por corte gravadas em", a.pasta_luts)
    print("4/5 montando a prévia ...")
    print("   ", rodar("previa.py", a.saida, a.titulo).strip())
    R = json.load(open(os.path.join(a.saida, "balance.json"), encoding="utf-8"))
    plano = []
    for r in R:
        if r["drone"]:
            plano.append({"corte": r["i"], "id": r["id"], "tipo": "cdl", "efeito": "ASC CDL",
                          "valores": {"Red Slope": round(r["p"][0], 5), "Green Slope": round(r["p"][1], 5),
                                      "Blue Slope": round(r["p"][2], 5)},
                          "nota": "zerar Temperatura manual antiga no Lumetri, se houver"})
        else:
            plano.append({"corte": r["i"], "id": r["id"], "tipo": "lut", "lut": r["lut"],
                          "nota": "Input LUT de um Lumetri NOVO (Lumetri antigo com LUT da lista ignora troca)"})
    json.dump(plano, open(os.path.join(a.saida, "plano_aplicacao.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    hero = next(r for r in R if r["hero"])
    nao_wb = [f"{r['i']:02d}" for r in R if not r["confiavel_wb"]]
    sil = [f"{r['i']:02d}" for r in R if r["luma"] < 0.08]
    rel = [f"# Balance — {a.titulo}", "",
           f"- Cortes medidos: {len(R)} (aninhadas e cortes sem arquivo ficam de fora)",
           f"- Referência (hero): corte {hero['i']:02d} ({os.path.basename(hero['arquivo'])})",
           *[f"- {l}" for l in linhas],
           f"- Branco não corrigido (sem neutro confiável): {', '.join(nao_wb) or 'nenhum'}",
           f"- Silhueta / interior escuro, exposição mantida: {', '.join(sil) or 'nenhum'}",
           "", "Prévia: `previa - balance antes e depois.jpg`. Plano para o Premiere: `plano_aplicacao.json`.",
           "Nada foi aplicado no Premiere. Aplicar só depois da aprovação do usuário e conferir exportando antes/depois."]
    open(os.path.join(a.saida, "relatorio.md"), "w", encoding="utf-8").write("\n".join(rel) + "\n")
    print("5/5 plano de aplicação e relatório prontos em", a.saida)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Caravela Color")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("balance")
    b.add_argument("--xml", required=True); b.add_argument("--saida", required=True)
    b.add_argument("--lut-conversao", required=True); b.add_argument("--pasta-luts", required=True)
    b.add_argument("--ids"); b.add_argument("--titulo", default="edição")
    a = ap.parse_args()
    if a.cmd == "balance":
        balance(a)
