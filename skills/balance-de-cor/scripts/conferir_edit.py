"""Confere o balance de uma edição Premiere x Premiere (mesmo quadro, mesmo enquadramento) e monta a imagem.
Uso: python conferir_edit.py <pasta>   (usa balance.json, p_antes/<i>.png, p_depois/<i>.png)
"""
import sys, os, json, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import cor
from wb_log import neutros, tom

D = sys.argv[1]
R = json.load(open(os.path.join(D, "balance.json"), encoding="utf-8"))
ld = lambda p: np.asarray(Image.open(p).convert("RGB").resize((540, 960), Image.LANCZOS)).astype(np.float64) / 255
br = lambda s: re.sub(r"(\d)\.(\d)", r"\1,\2", s)


def assunto(d):
    r, g, b = d[..., 0], d[..., 1], d[..., 2]
    return ~((b > r * 1.12) & (b >= g) & ((d @ cor.LUMA709) > 0.40))


hero = next(r for r in R if r["hero"])
out = []
for r in R:
    a = ld(os.path.join(D, "p_antes", f"{r['i']:02d}.png")); d = ld(os.path.join(D, "p_depois", f"{r['i']:02d}.png"))
    mn, ma = neutros(a), assunto(a)
    La = float(np.median((a @ cor.LUMA709)[ma])) if ma.mean() > 0.05 else float(np.median(a @ cor.LUMA709))
    Ld = float(np.median((d @ cor.LUMA709)[ma])) if ma.mean() > 0.05 else float(np.median(d @ cor.LUMA709))
    ta = tom(a[mn]) if mn.mean() >= 0.02 else (None, None)
    td = tom(d[mn]) if mn.mean() >= 0.02 else (None, None)
    out.append({**{k: r[k] for k in ("i", "nome", "drone", "hero")}, "L_antes": La, "L_depois": Ld,
                "rb_antes": ta[0], "rb_depois": td[0]})
    r["_a"], r["_d"] = a, d
hL = next(o for o in out if o["hero"])["L_depois"]
st = lambda L: np.log2(max(L, 1e-4) ** 2.4 / hL ** 2.4)     # stops de luz em relação ao hero
EA = np.array([st(o["L_antes"]) for o in out]); ED = np.array([st(o["L_depois"]) for o in out])
W = [o for o in out if o["rb_antes"] is not None]
TA = np.array([o["rb_antes"] for o in W]); TD = np.array([o["rb_depois"] for o in W])
print(f"EXPOSIÇÃO (stops vs hero, Premiere x Premiere): antes desvio {EA.std():.2f}  depois {ED.std():.2f}")
print(f"   cortes a mais de 1 stop do hero: antes {(abs(EA) > 1).sum()}  depois {(abs(ED) > 1).sum()}")
print(f"TEMPERATURA: antes desvio {TA.std():.2f} pior {TA[np.argmax(abs(TA))]:+.2f}  depois desvio {TD.std():.2f} pior {TD[np.argmax(abs(TD))]:+.2f}")
print(f"   fora de ±0,15: antes {(abs(TA) > 0.15).sum()}  depois {(abs(TD) > 0.15).sum()}  (de {len(W)})")
json.dump(out, open(os.path.join(D, "conferencia.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# ---------------- imagem ----------------
FN = lambda s, b=False: ImageFont.truetype("segoeuib.ttf" if b else "segoeui.ttf", s)
BG, FG, DIM, ACC, ANT = (18, 18, 20), (236, 236, 236), (150, 150, 155), (214, 168, 92), (120, 150, 200)
TW, TH, COLS, PAD = 84, 150, 14, 30
PAR = TW * 2 + 2; BLK = TH + 38
LIN = (len(R) + COLS - 1) // COLS
W_ = PAD * 2 + COLS * (PAR + 10)
CH = 300
H = 190 + LIN * BLK + CH * 2 + 90
im = Image.new("RGB", (W_, H), BG); dr = ImageDraw.Draw(im)
dr.text((PAD, 20), "Caravela Color · balance da edição", font=FN(40, True), fill=FG)
dr.text((PAD, 76), "Cópia da edição sem look nem grão. Cada corte medido no trecho usado. Ordem: exposição → branco → conversão Rec.709 por último.",
        font=FN(18), fill=DIM)
dr.text((PAD, 104), f"Referência (hero): corte {hero['i']:02d} · arquivo {hero['nome'][-8:-4]}. Silhuetas e interiores escuros ficam como estão (intenção).", font=FN(18), fill=DIM)
dr.text((PAD, 142), "Em cada par:", font=FN(17, True), fill=FG)
dr.text((PAD + 120, 142), "esquerda = ANTES (como está na edição, sem o look)", font=FN(17, True), fill=ANT)
dr.text((PAD + 600, 142), "direita = DEPOIS (balance da skill) · os dois exportados do Premiere", font=FN(17, True), fill=ACC)
y0 = 176
for k, r in enumerate(R):
    li, co = divmod(k, COLS); x = PAD + co * (PAR + 10); y = y0 + li * BLK
    for j, arr in enumerate((r["_a"], r["_d"])):
        im.paste(Image.fromarray((arr * 255).astype(np.uint8)).resize((TW, TH), Image.LANCZOS), (x + j * (TW + 2), y))
    o = out[k]
    t = f"{r['i']:02d}{' HERO' if r['hero'] else ''}  {st(o['L_antes']):+.1f}→{st(o['L_depois']):+.1f} st"
    dr.text((x, y + TH + 3), br(t), font=FN(12, r["hero"]), fill=ACC if r["hero"] else DIM)
    if o["rb_antes"] is not None:
        dr.text((x, y + TH + 18), br(f"cor {o['rb_antes']:+.2f}→{o['rb_depois']:+.2f}"), font=FN(12), fill=DIM)


def grafico(y, titulo, desc, A, B, faixa, linhas, banda):
    x0, x1 = PAD + 50, W_ - PAD
    dr.text((PAD, y), titulo, font=FN(22, True), fill=FG); dr.text((PAD, y + 32), desc, font=FN(15), fill=DIM)
    gy0, gy1 = y + 62, y + CH - 24; lo, hi = faixa
    Y = lambda v: gy1 - (np.clip(v, lo, hi) - lo) / (hi - lo) * (gy1 - gy0)
    X = lambda i: x0 + 10 + i * (x1 - x0 - 20) / max(len(A) - 1, 1)
    dr.rectangle([x0, Y(banda), x1, Y(-banda)], fill=(34, 40, 36))
    for v in linhas:
        dr.line([x0, Y(v), x1, Y(v)], fill=(48, 48, 52), width=2 if v == 0 else 1)
        dr.text((x0 - 46, Y(v) - 9), br(f"{v:+g}"), font=FN(13), fill=DIM)
    for vals, c, w in ((A, ANT, 2), (B, ACC, 3)):
        pts = [(X(i), Y(v)) for i, v in enumerate(vals)]
        dr.line(pts, fill=c, width=w)
        for p in pts:
            dr.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=c)
    dr.text((x1 - 260, y + 4), "● antes", font=FN(16, True), fill=ANT); dr.text((x1 - 140, y + 4), "● depois", font=FN(16, True), fill=ACC)


yg = y0 + LIN * BLK + 10
grafico(yg, "Exposição de cada corte em relação ao hero (stops de luz no assunto, sem céu)",
        br(f"Antes: desvio {EA.std():.2f} stop, {(abs(EA) > 1).sum()} cortes a mais de 1 stop. Depois: desvio {ED.std():.2f}, {(abs(ED) > 1).sum()} a mais de 1 stop. "
           "Faixa = ±0,5 stop. Silhuetas ficam fora de propósito."), EA, ED, (-4, 3), [-4, -2, 0, 2], 0.5)
grafico(yg + CH, "Temperatura de cada corte (medida nas áreas neutras · abaixo de 0 = frio)",
        br(f"Antes: desvio {TA.std():.2f}, {(abs(TA) > 0.15).sum()} cortes fora de ±0,15. Depois: desvio {TD.std():.2f}, {(abs(TD) > 0.15).sum()} fora. ({len(W)} cortes com área neutra.)"),
        TA, TD, (-0.8, 0.8), [-0.8, -0.4, 0, 0.4, 0.8], 0.15)
dr.text((PAD, H - 34), "Aplicação no Premiere: câmera = Lumetri › Input LUT “Caravela Balance <corte>” (exposição + branco no S-Log3 + conversão Adobe); drone = ASC CDL. "
        "Sequências aninhadas não são tratadas.", font=FN(14), fill=DIM)
im.save(os.path.join(D, "edicao - balance antes e depois.jpg"), quality=90)
print("imagem ok", im.size)
