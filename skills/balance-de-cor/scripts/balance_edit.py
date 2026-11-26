"""Balance de uma EDIÇÃO (cada corte medido no trecho usado), ordem profissional:
exposição -> branco -> conversão Rec.709 por último. Iguala os cortes a um hero.

Câmera S-Log3: correção = offset por canal no código log (exposição = mesmo offset nos 3 canais,
branco = diferença entre canais), resolvida medindo a imagem DEPOIS da LUT de conversão.
Drone Rec.709: slope por canal (ASC CDL).

Uso: python balance_edit.py <cortes.json> <ids.txt> <pasta_saida> <lut_conversao.cube> <pasta_luts>
ids.txt: IDs dos clipes da faixa V1 da cópia, na ordem (um por linha; aninhadas incluídas).
"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import cor
from wb_log import ler, neutros, tom

cortes = json.load(open(sys.argv[1], encoding="utf-8"))
ids = [l.strip() for l in open(sys.argv[2]) if l.strip()]
SAIDA, LUT, PASTA_LUT = sys.argv[3], cor.ler_cube(sys.argv[4]), sys.argv[5]
os.makedirs(os.path.join(SAIDA, "frames"), exist_ok=True); os.makedirs(PASTA_LUT, exist_ok=True)
assert len(ids) == len(cortes), (len(ids), len(cortes))

K = 261.5 / 1023 * np.log10(2)      # 1 stop em código S-Log3
FORCA_EXP, LIM_EXP = 0.75, 1.3      # exposição: 75% do caminho até o hero, no máx. ±1,3 stop
FORCA_WB, LIM_WB, AREA_MIN, LIM_GM = 0.9, 1.0, 0.02, 0.35


def assunto(disp):
    r, g, b = disp[..., 0], disp[..., 1], disp[..., 2]
    return ~((b > r * 1.12) & (b >= g) & ((disp @ cor.LUMA709) > 0.40))


def luma_assunto(imgs, masks_a):
    y = np.concatenate([(i @ cor.LUMA709)[m] for i, m in zip(imgs, masks_a)])
    return float(np.median(y)) if y.size else 0.4


def render_fn(drone):
    if drone:   # p = (sR, sG, sB)
        return lambda code, p: np.clip(code * p, 0, 1)
    return lambda code, p: cor.aplicar_cube(np.clip(code + p, 0, 1), LUT)   # p = (oR, oG, oB)


# ---------- 1) medir todos os cortes como estão (antes) ----------
dados = []
for i, (c, cid) in enumerate(zip(cortes, ids)):
    if not c["arquivo"]:
        dados.append(None); continue
    drone = "Drone" in os.path.basename(c["arquivo"])
    dur = c["src_out"] - c["src_in"]
    codes = [ler(c["arquivo"], c["src_in"] + dur * f, drone) for f in (0.2, 0.5, 0.8)]
    render = render_fn(drone)
    p0 = np.ones(3) if drone else np.zeros(3)
    antes = [render(cd, p0) for cd in codes]
    mn = [neutros(a) for a in antes]; ma = [assunto(a) for a in antes]
    area = float(np.mean([m.mean() for m in mn]))
    px = lambda imgs: np.concatenate([im[m] for im, m in zip(imgs, mn)])
    rb, gm = tom(px(antes)) if area >= AREA_MIN else (0.0, 0.0)
    dados.append({"i": i, "id": cid, "nome": c["nome"], "arquivo": c["arquivo"], "drone": drone, "seq_ini": c["seq_ini"],
                  "seq_fim": c["seq_fim"], "codes": codes, "mn": mn, "ma": ma, "area": area, "rb": rb, "gm": gm,
                  "luma": luma_assunto(antes, ma), "antes": antes})
    print(f"medido {i:02d} {c['nome'][-8:-4]}  luma {dados[-1]['luma']*100:4.1f}%  rb {rb:+.2f}  gm {gm:+.2f}  neutros {area*100:3.0f}%")

# ---------- 2) hero: exposição mais típica + branco mais neutro, com área neutra boa ----------
V = [d for d in dados if d]
med = np.median([d["luma"] for d in V])
cand = [d for d in V if d["area"] >= 0.15 and not d["drone"]] or V
hero = min(cand, key=lambda d: abs(np.log2(d["luma"] / med)) + abs(d["rb"]) + abs(d["gm"]))
ALVO = hero["luma"]
print(f"\nHERO: corte {hero['i']:02d} ({hero['nome'][-8:-4]}), luma {ALVO*100:.1f}%  rb {hero['rb']:+.2f}  (mediana da edição {med*100:.1f}%)\n")

# ---------- 3) por corte: exposição, depois branco ----------
res = []
for d in V:
    render = render_fn(d["drone"]); codes = d["codes"]
    p = np.ones(3) if d["drone"] else np.zeros(3)
    imgs = lambda: [render(cd, p) for cd in codes]
    # 3a) exposição: leva a luma do assunto 75% do caminho (em stops) até o hero
    frac_assunto = float(np.mean([m.mean() for m in d["ma"]]))
    forca = FORCA_EXP if frac_assunto >= 0.35 else 0.35          # quadro dominado por céu: mexe pouco
    if d["luma"] < 0.08:                                           # silhueta / interior escuro: intenção
        forca = 0.0
    stops_falta = np.log2((ALVO ** 2.4) / max(d["luma"] ** 2.4, 1e-6))
    stops_alvo = float(np.clip(stops_falta * forca, -LIM_EXP, LIM_EXP))
    alvo_luma = (d["luma"] ** 2.4 * 2 ** stops_alvo) ** (1 / 2.4)
    if abs(stops_alvo) > 0.02:
        # bissecção no parâmetro de exposição (a luma cresce com ele: não diverge)
        lo, hi = (-np.log2(2.5) * 2.4, np.log2(2.5) * 2.4) if d["drone"] else (-0.12, 0.12)
        def aplica(v):
            return np.full(3, 2 ** (v / 2.4)) if d["drone"] else np.full(3, v)
        for _ in range(16):
            mid = (lo + hi) / 2
            p = aplica(mid)
            if luma_assunto(imgs(), d["ma"]) < alvo_luma:
                lo = mid
            else:
                hi = mid
        p = aplica((lo + hi) / 2)
    # 3b) branco: neutros cinza na imagem convertida (verde/magenta com metade da força)
    confiavel = d["area"] >= AREA_MIN and abs(d["gm"]) <= LIM_GM
    if confiavel:
        px = lambda ims: np.concatenate([im[m] for im, m in zip(ims, d["mn"])])
        rb0, gm0 = tom(px(imgs()))
        alvo_rb = rb0 - np.clip(rb0, -LIM_WB, LIM_WB) * FORCA_WB
        alvo_gm = gm0 - np.clip(gm0, -0.3, 0.3) * 0.5
        for _ in range(12):
            r_, g_ = tom(px(imgs()))
            er, eg = r_ - alvo_rb, g_ - alvo_gm
            if abs(er) < 0.01 and abs(eg) < 0.01:
                break
            dR, dB = (-er / 2 + eg / 2), (er / 2 + eg / 2)
            if d["drone"]:
                p = np.clip(p * np.array([2 ** (dR * 0.7 / 2.4), 1, 2 ** (dB * 0.7 / 2.4)]), 0.4, 2.5)
            else:
                p = np.clip(p + np.array([dR, 0, dB]) * K * 0.6, -0.15, 0.15)
    if not np.all(np.isfinite(p)):
        p = np.ones(3) if d["drone"] else np.zeros(3); confiavel = False
    depois = imgs()
    L2 = luma_assunto(depois, d["ma"])
    rb2, gm2 = tom(np.concatenate([im[m] for im, m in zip(depois, d["mn"])])) if d["area"] >= AREA_MIN else (0.0, 0.0)
    np.save(os.path.join(SAIDA, "frames", f"{d['i']:02d}_antes.npy"), d["antes"][1].astype(np.float32))
    np.save(os.path.join(SAIDA, "frames", f"{d['i']:02d}_depois.npy"), depois[1].astype(np.float32))
    r = {k: d[k] for k in ("i", "id", "nome", "arquivo", "drone", "seq_ini", "seq_fim", "area", "rb", "gm", "luma")}
    r.update({"p": p.tolist(), "luma_depois": L2, "rb_depois": rb2, "gm_depois": gm2, "confiavel_wb": bool(confiavel),
              "hero": d is hero,
              "exposicao_stops": float(np.log2(p[1]) * 2.4) if d["drone"] else float(p[1] / K)})
    if not d["drone"]:   # LUT = correção no log + conversão
        N = 65; e = np.linspace(0, 1, N); bb, gg, rr = np.meshgrid(e, e, e, indexing="ij")
        grade = np.stack([rr, gg, bb], -1)
        out = cor.aplicar_cube(np.clip(grade + p, 0, 1), LUT)
        nome = f"Caravela Balance {d['i']:02d} {d['nome'][-8:-4]} + SLog3-709.cube"
        with open(os.path.join(PASTA_LUT, nome), "w", encoding="ascii") as f:
            f.write(f'TITLE "Caravela Balance corte {d["i"]:02d}"\n# offset log R {p[0]:+.5f} G {p[1]:+.5f} B {p[2]:+.5f} + Sony S-Log3 to Rec.709 (Adobe)\n')
            f.write(f"LUT_3D_SIZE {N}\nDOMAIN_MIN 0.0 0.0 0.0\nDOMAIN_MAX 1.0 1.0 1.0\n")
            np.savetxt(f, out.reshape(-1, 3), fmt="%.6f")
        r["lut"] = os.path.join(PASTA_LUT, nome)
    res.append(r)
    print(f"{d['i']:02d} {d['nome'][-8:-4]} {'D' if d['drone'] else 'C'}{' HERO' if d is hero else ''}  "
          f"exp {r['exposicao_stops']:+.2f} st  luma {d['luma']*100:4.1f}->{L2*100:4.1f}  rb {d['rb']:+.2f}->{rb2:+.2f}"
          + ("" if confiavel else "  [branco não corrigido]"))
json.dump(res, open(os.path.join(SAIDA, "balance.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
A = np.array([[r["luma"], r["rb"]] for r in res]); B = np.array([[r["luma_depois"], r["rb_depois"]] for r in res])
print(f"\nexposição (luma do assunto, stops vs hero)  antes: desvio {np.std(np.log2(A[:,0]/ALVO)*2.4):.2f}  depois: {np.std(np.log2(B[:,0]/ALVO)*2.4):.2f}")
print(f"temperatura  antes: desvio {A[:,1].std():.2f}  depois: {B[:,1].std():.2f}")
