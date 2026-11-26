"""Prévia do balance (antes/depois calculados a partir dos arquivos originais) para o usuário aprovar.
Uso: python previa.py <pasta_saida> [titulo]
"""
import sys, os, json, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont
D = sys.argv[1]
TITULO = sys.argv[2] if len(sys.argv) > 2 else "edição"
R = json.load(open(os.path.join(D, "balance.json"), encoding="utf-8"))
FN = lambda s, b=False: ImageFont.truetype("segoeuib.ttf" if b else "segoeui.ttf", s)
BG, FG, DIM, ACC, ANT = (18, 18, 20), (236, 236, 236), (150, 150, 155), (214, 168, 92), (120, 150, 200)
br = lambda s: re.sub(r"(\d)\.(\d)", r"\1,\2", s)
hero = next(r for r in R if r["hero"]); hL = hero["luma_depois"]
st = lambda L: float(np.log2(max(L, 1e-4) ** 2.4 / hL ** 2.4))
TW, TH, COLS, PAD = 84, 150, 14, 30
PAR = TW * 2 + 2; BLK = TH + 38; LIN = (len(R) + COLS - 1) // COLS
W = PAD * 2 + COLS * (PAR + 10); CH = 290; H = 200 + LIN * BLK + CH * 2 + 60
im = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(im)
dr.text((PAD, 20), f"Caravela Color · balance · {TITULO} · PRÉVIA", font=FN(40, True), fill=FG)
dr.text((PAD, 76), "Cada corte medido no trecho usado da edição. Ordem: exposição → branco no S-Log3 → conversão Rec.709 (LUT Sony da Adobe) por último.", font=FN(18), fill=DIM)
dr.text((PAD, 104), f"Referência (hero): corte {hero['i']:02d}, arquivo {hero['nome'][-8:-4]}. Silhuetas e interiores escuros mantidos. Quadros inteiros (sem o zoom/recorte da edição).", font=FN(18), fill=DIM)
dr.text((PAD, 140), "esquerda = ANTES (só conversão)", font=FN(17, True), fill=ANT)
dr.text((PAD + 330, 140), "direita = DEPOIS (balance da skill) · calculado, aguardando aprovação", font=FN(17, True), fill=ACC)
y0 = 176
for k, r in enumerate(R):
    li, co = divmod(k, COLS); x = PAD + co * (PAR + 10); y = y0 + li * BLK
    for j, suf in enumerate(("_antes", "_depois")):
        a = np.load(os.path.join(D, "frames", f"{r['i']:02d}{suf}.npy"))
        im.paste(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((TW, TH), Image.LANCZOS), (x + j * (TW + 2), y))
    dr.text((x, y + TH + 3), br(f"{r['i']:02d}{' HERO' if r['hero'] else ''}  {st(r['luma']):+.1f}→{st(r['luma_depois']):+.1f} st"), font=FN(12, r["hero"]), fill=ACC if r["hero"] else DIM)
    dr.text((x, y + TH + 18), br(f"cor {r['rb']:+.2f}→{r['rb_depois']:+.2f}"), font=FN(12), fill=DIM)
EA = np.array([st(r["luma"]) for r in R]); ED = np.array([st(r["luma_depois"]) for r in R])
TA = np.array([r["rb"] for r in R]); TD = np.array([r["rb_depois"] for r in R])


def graf(y, tit, desc, A, B, faixa, lin, banda):
    x0, x1 = PAD + 50, W - PAD
    dr.text((PAD, y), tit, font=FN(22, True), fill=FG); dr.text((PAD, y + 32), desc, font=FN(15), fill=DIM)
    gy0, gy1 = y + 62, y + CH - 24; lo, hi = faixa
    Y = lambda v: gy1 - (np.clip(v, lo, hi) - lo) / (hi - lo) * (gy1 - gy0)
    X = lambda i: x0 + 10 + i * (x1 - x0 - 20) / (len(A) - 1)
    dr.rectangle([x0, Y(banda), x1, Y(-banda)], fill=(34, 40, 36))
    for v in lin:
        dr.line([x0, Y(v), x1, Y(v)], fill=(48, 48, 52), width=2 if v == 0 else 1); dr.text((x0 - 46, Y(v) - 9), br(f"{v:+g}"), font=FN(13), fill=DIM)
    for vals, c, w in ((A, ANT, 2), (B, ACC, 3)):
        pts = [(X(i), Y(v)) for i, v in enumerate(vals)]; dr.line(pts, fill=c, width=w)
        for p in pts:
            dr.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=c)
    dr.text((x1 - 260, y + 4), "● antes", font=FN(16, True), fill=ANT); dr.text((x1 - 140, y + 4), "● depois", font=FN(16, True), fill=ACC)


yg = y0 + LIN * BLK + 10
graf(yg, "Exposição de cada corte em relação ao hero (stops de luz no assunto, sem céu)",
     br(f"Antes: desvio {EA.std():.2f} stop, {(abs(EA) > 1).sum()} cortes a mais de 1 stop. Depois: desvio {ED.std():.2f}, {(abs(ED) > 1).sum()} a mais de 1 stop (silhuetas e céu de propósito)."),
     EA, ED, (-4, 3), [-4, -2, 0, 2], 0.5)
graf(yg + CH, "Temperatura de cada corte (neutro em asfalto, concreto, carros · abaixo de 0 = frio)",
     br(f"Antes: desvio {TA.std():.2f}, {(abs(TA) > 0.15).sum()} cortes fora de ±0,15. Depois: desvio {TD.std():.2f}, {(abs(TD) > 0.15).sum()} fora."),
     TA, TD, (-0.8, 0.8), [-0.8, -0.4, 0, 0.4, 0.8], 0.15)
im.save(os.path.join(D, "previa - balance antes e depois.jpg"), quality=90)
print(f"exp desvio {EA.std():.2f}->{ED.std():.2f}  >1st {(abs(EA)>1).sum()}->{(abs(ED)>1).sum()}  temp {TA.std():.2f}->{TD.std():.2f}  fora {(abs(TA)>0.15).sum()}->{(abs(TD)>0.15).sum()}")
