"""Mede o respiro dos motions até as bordas do quadro (vídeo com transparência: .mov ProRes 4444).

Para cada motion, amostra quadros, acha a área com conteúdo visível (alfa > limite) e diz a menor
distância até a borda de cima, de baixo, da esquerda e da direita, nos quadros em que o motion está
parado na tela (os quadros de entrada e saída, em que ele está se mexendo para fora, são ignorados).
Motion de tela cheia (sem transparência) é só avisado.

Uso:
  python margens.py motions/render/*.mov
  python margens.py m2.mov --lado 100 --topo 180 --base 380      # limites em px de um quadro 1080x1920

Limites padrão para vertical 1080x1920 (Reels/TikTok): 100 px nas laterais, 180 px em cima e 380 px
embaixo (a interface da rede cobre a base). Em 1920x1080 use --lado 120 --topo 90 --base 90.
Sai com código 1 se algum motion passar do limite.
"""
import argparse, subprocess, sys, shutil
import numpy as np

FF = shutil.which("ffmpeg") or "ffmpeg"
FP = shutil.which("ffprobe") or "ffprobe"


def sondar(path):
    s = subprocess.run([FP, "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,pix_fmt:format=duration", "-of", "default=nw=1", path],
                       capture_output=True, text=True).stdout
    d = dict(l.split("=", 1) for l in s.split() if "=" in l)
    return int(d["width"]), int(d["height"]), d.get("pix_fmt", ""), float(d.get("duration", 0))


def caixas(path, w, h, passos):
    """Caixa do conteúdo visível em cada quadro amostrado (em px do vídeo original), ou None se vazio."""
    W, H = w // 4, h // 4
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-vf", f"fps={passos},scale={W}:{H},format=rgba",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 4)[..., 3]
    out = []
    for q in a:
        m = q > 24
        if not m.any():
            out.append(None); continue
        ys, xs = np.where(m)
        out.append((xs.min() * 4, ys.min() * 4, (xs.max() + 1) * 4, (ys.max() + 1) * 4, float(m.mean())))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("videos", nargs="+")
    ap.add_argument("--lado", type=int, default=100)
    ap.add_argument("--topo", type=int, default=180)
    ap.add_argument("--base", type=int, default=380)
    ap.add_argument("--fps", type=float, default=12)
    a = ap.parse_args()
    falhou = False
    for v in a.videos:
        w, h, pix, dur = sondar(v)
        nome = v.replace("\\", "/").split("/")[-1]
        if "a" not in pix.replace("yuv", "").replace("p", "")[:3] and not pix.startswith(("yuva", "rgba", "argb", "gbrap")):
            print(f"{nome}: sem transparência ({pix}) — tela cheia, conferir a olho"); continue
        cx = caixas(v, w, h, a.fps)
        if sum(1 for c in cx if c and c[4] > 0.95) > len(cx) / 2:
            print(f"{nome}: tela cheia (fundo opaco) — conferir a olho"); continue
        # "parado na tela": a caixa quase não muda em relação ao quadro anterior e ao seguinte
        parados = []
        for i in range(1, len(cx) - 1):
            c, p, n = cx[i], cx[i - 1], cx[i + 1]
            if c and p and n and all(abs(c[k] - p[k]) <= 12 and abs(c[k] - n[k]) <= 12 for k in range(4)):
                parados.append((i / a.fps, c))
        if not parados:
            print(f"{nome}: sem quadro parado (motion só de passagem) — conferir a olho"); continue
        esq = min(c[0] for _, c in parados); topo = min(c[1] for _, c in parados)
        dir_ = min(w - c[2] for _, c in parados); base = min(h - c[3] for _, c in parados)
        prob = []
        if esq < a.lado: prob.append(f"esquerda {esq}px")
        if dir_ < a.lado: prob.append(f"direita {dir_}px")
        if topo < a.topo: prob.append(f"topo {topo}px")
        if base < a.base: prob.append(f"base {base}px")
        estado = "OK" if not prob else "PERTO DA BORDA: " + ", ".join(prob)
        print(f"{nome}: esq {esq} · dir {dir_} · topo {topo} · base {base}  →  {estado}")
        falhou |= bool(prob)
    sys.exit(1 if falhou else 0)


if __name__ == "__main__":
    main()
