"""Balanço de branco ANTES da conversão (ordem profissional), com o ALVO medido DEPOIS da conversão.

Câmera S-Log3: a correção é um Offset por canal no código log (o "Offset" dos coloristas), aplicado
antes da LUT S-Log3->Rec.709. Os offsets são resolvidos por iteração até os neutros (asfalto, concreto,
carros; sem céu e vegetação) ficarem cinza NA IMAGEM CONVERTIDA — o mesmo lugar onde se olha e onde
se confere. (Versão 1 resolvia no linear da câmera e conferia depois da LUT: os dois discordavam.)
Drone Rec.709: Slope por canal (ASC CDL), resolvido do mesmo jeito.

Uso: python wb_log.py <lista_clipes.json> <pasta_saida> <lut_entrada.cube>
"""
import sys, os, json, subprocess
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import cor

FORCA = 0.9                  # corrige 90% da dominante medida
LIM_STOPS = 1.0              # dominante máx. considerada (stops entre R e B)
LIM_CONFIAVEL_GM = 0.35      # verde/magenta maior que isso não é luz do dia: é a cena (folhagem)
AREA_MIN = 0.02              # menos que 2% de área neutra: não corrige


def ler(path, t, drone, largura=360, altura=640):
    faixa = "tv" if drone else "full"
    vf = f"scale={largura}:{altura}:in_range={faixa}:out_range=full:in_color_matrix=bt709,format=rgb48le"
    cmd = [cor.FFMPEG, "-v", "error", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1", "-vf", vf,
           "-f", "rawvideo", "-pix_fmt", "rgb48le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<u2").reshape(altura, largura, 3).astype(np.float64) / 65535


def neutros(disp):
    """Pixels quase sem cor e de meio-tom, sem céu e vegetação (mesma regra da conferência)."""
    mx, mn = disp.max(-1), disp.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1e-4)
    y = disp @ cor.LUMA709
    r, g, b = disp[..., 0], disp[..., 1], disp[..., 2]
    ceu = (b > r * 1.12) & (b >= g) & (y > 0.40)
    verde = (g > r * 1.10) & (g > b * 1.10)
    return (sat < 0.18) & (y > 0.12) & (y < 0.92) & ~ceu & ~verde


def tom(disp_px):
    """Dominante dos pixels neutros na imagem convertida (luz de display ~ gama 2.4)."""
    e = np.median(np.clip(disp_px, 0, 1) ** 2.4, 0)
    return float(np.log2(e[0] / e[2])), float(np.log2(e[1] / np.sqrt(e[0] * e[2])))


def main():
    clipes = json.load(open(sys.argv[1], encoding="utf-8"))
    saida = sys.argv[2]
    LUT = cor.ler_cube(sys.argv[3])
    os.makedirs(os.path.join(saida, "frames"), exist_ok=True)
    res = []
    for c in clipes:
        drone = c["drone"]
        codes = [ler(c["arquivo"], c["dur"] * f, drone) for f in (0.25, 0.5, 0.75)]
        if drone:
            render = lambda code, p: np.clip(code * np.array([p[0], 1.0, p[1]]), 0, 1)       # slope R, B
            p0 = np.array([1.0, 1.0])
        else:
            render = lambda code, p: cor.aplicar_cube(np.clip(code + np.array([p[0], 0.0, p[1]]), 0, 1), LUT)  # offset R, B
            p0 = np.array([0.0, 0.0])
        antes = [render(code, p0) for code in codes]
        masks = [neutros(a) for a in antes]
        area = float(np.mean([m.mean() for m in masks]))
        px = lambda imgs: np.concatenate([i[m] for i, m in zip(imgs, masks)])
        if area >= AREA_MIN:
            rb, gm = tom(px(antes))
        else:
            rb, gm = 0.0, 0.0
        confiavel = area >= AREA_MIN and abs(gm) <= LIM_CONFIAVEL_GM
        # alvo: tirar FORCA da dominante (limitada); verde/magenta só metade (é mais arriscado)
        alvo_rb = rb - np.clip(rb, -LIM_STOPS, LIM_STOPS) * FORCA if confiavel else rb
        alvo_gm = gm - np.clip(gm, -0.3, 0.3) * 0.5 if confiavel else gm
        p = p0.copy()
        if confiavel:
            for _ in range(12):                      # iteração: mede, corrige, mede de novo
                r_, g_ = tom(px([render(code, p) for code in codes]))
                er, eg = r_ - alvo_rb, g_ - alvo_gm
                if abs(er) < 0.01 and abs(eg) < 0.01:
                    break
                # erro em stops -> passo no parâmetro (verde fixo: mexe R e B juntos para o verde)
                # quente demais (er>0): baixa R, sobe B. verde demais (eg>0): sobe R e B juntos.
                dR, dB = (-er / 2 + eg / 2), (er / 2 + eg / 2)
                if drone:
                    p = np.clip(p * np.array([2 ** (dR * 0.7 / 2.4), 2 ** (dB * 0.7 / 2.4)]), 0.85, 1.15)
                else:
                    k = 261.5 / 1023 * np.log10(2) * 0.6
                    p = np.clip(p + np.array([dR, dB]) * k, -0.08, 0.08)
            if not np.all(np.isfinite(p)):
                p, confiavel = p0.copy(), False
        depois = [render(code, p) for code in codes]
        rb2, gm2 = tom(px(depois)) if area >= AREA_MIN else (0.0, 0.0)
        cdl = ({"Red Slope": float(p[0]), "Green Slope": 1.0, "Blue Slope": float(p[1])} if drone else
               {"Red Offset": float(p[0]), "Green Offset": 0.0, "Blue Offset": float(p[1])})
        np.save(os.path.join(saida, "frames", c["nome"] + "_antes.npy"), antes[1].astype(np.float32))
        np.save(os.path.join(saida, "frames", c["nome"] + "_wb.npy"), depois[1].astype(np.float32))
        res.append({**c, "rb_antes": rb, "gm_antes": gm, "rb_depois": rb2, "gm_depois": gm2,
                    "neutros_pct": area * 100, "cdl": cdl, "confiavel": bool(confiavel)})
        print(f"{c['nome']:>9} {'D' if drone else 'C'}  neutros {area*100:4.0f}%  rb {rb:+.2f} -> {rb2:+.2f}  "
              f"gm {gm:+.2f} -> {gm2:+.2f}  " + "  ".join(f"{k.split()[0][0]}{k.split()[1][0]} {v:+.4f}" for k, v in cdl.items())
              + ("" if confiavel else "   [não corrigido]"))
    json.dump(res, open(os.path.join(saida, "wb.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    RA = np.array([r["rb_antes"] for r in res if r["confiavel"]]); RD = np.array([r["rb_depois"] for r in res if r["confiavel"]])
    print(f"\nquente/frio  antes: desvio {RA.std():.2f}   depois (simulado): desvio {RD.std():.2f}")


if __name__ == "__main__":
    main()
