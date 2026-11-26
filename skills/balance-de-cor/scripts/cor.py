"""Caravela Color: núcleo de cor (protótipo da Fase 2).

Decodifica frames, converte S-Log3/S-Gamut3 -> Rec.709, mede e corrige.
Tudo em float64; o linear é cena-referido (0.18 = cinza 18%).
"""
import subprocess
import numpy as np
from PIL import Image

import shutil
FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
LUMA709 = np.array([0.2126, 0.7152, 0.0722])


# ---------- leitura ----------
def frame_do_video(path, t, largura=960):
    """Extrai 1 frame em 16 bits. Sony XAVC S vem como faixa cheia (yuvj420p):
    o código lido já é o código S-Log3 normalizado (preto ~95/1023)."""
    vf = (f"scale={largura}:-2:in_range=full:out_range=full:in_color_matrix=bt709,"
          "format=rgb48le")
    cmd = [FFMPEG, "-v", "error", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1",
           "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb48le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    h = len(raw) // (largura * 6)
    return np.frombuffer(raw, dtype="<u2").reshape(h, largura, 3).astype(np.float64) / 65535


def salvar(img, path, qualidade=92):
    Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(path, quality=qualidade)


# ---------- S-Log3 / S-Gamut3 ----------
def slog3_para_linear(v):
    c = v * 1023
    return np.where(c >= 171.2102946929,
                    10 ** ((c - 420) / 261.5) * 0.19 - 0.01,
                    (c - 95) * 0.01125 / (171.2102946929 - 95))


def _rgb2xyz(prim, branco=(0.3127, 0.3290)):
    xy = np.array(prim)
    P = np.stack([xy[:, 0] / xy[:, 1], np.ones(3), (1 - xy[:, 0] - xy[:, 1]) / xy[:, 1]])
    W = np.array([branco[0] / branco[1], 1, (1 - branco[0] - branco[1]) / branco[1]])
    return P * np.linalg.solve(P, W)


GAMUTS = {
    "s-gamut3": [(0.730, 0.280), (0.140, 0.855), (0.100, -0.050)],
    "s-gamut3-cine": [(0.766, 0.275), (0.225, 0.800), (0.089, -0.087)],
}
_R709 = _rgb2xyz([(0.64, 0.33), (0.30, 0.60), (0.15, 0.06)])


def matriz_para_709(gamut="s-gamut3"):
    return np.linalg.inv(_R709) @ _rgb2xyz(GAMUTS[gamut])


def log_para_linear709(log, gamut="s-gamut3"):
    """Linear cena-referido em primárias Rec.709."""
    return slog3_para_linear(log) @ matriz_para_709(gamut).T


def linear_para_display(lin):
    """Mapeamento de tons neutro (ombro suave sobre a norma, sem torcer matiz) + gama 2.4.
    Mesmo método do look 'Filme Quente' (24/11/2026)."""
    n = np.maximum(lin.max(-1, keepdims=True), 1e-6)
    W = 12.0
    tn = n * (1 + n / W ** 2) / (1 + n) * 1.12
    out = lin * (tn / n)
    y = out @ LUMA709
    acima = np.clip(out.max(-1) - 1, 0, None)[..., None]
    out = out + (y[..., None] - out) * np.clip(acima * 2, 0, 1)
    return np.clip(np.clip(out, 0, None), 0, 1) ** (1 / 2.4)


# ---------- medidas ----------
def medir(lin):
    """Métricas no linear Rec.709 (antes do mapeamento de tons)."""
    y = lin @ LUMA709
    yv = y[y > 1e-5]
    med = float(np.median(yv)) if yv.size else 1e-5
    # balanço: Shades of Gray (p=6) nos pixels de meio-tom (sem preto nem altas)
    m = (y > np.percentile(y, 10)) & (y < np.percentile(y, 97))
    px = np.clip(lin[m], 0, None)
    sog = (px ** 6).mean(0) ** (1 / 6)
    gw = px.mean(0)
    est = np.sqrt(sog * gw)            # média geométrica dos dois estimadores
    est = est / est[1]
    disp = linear_para_display(lin)
    yd = disp @ LUMA709
    return {
        "stops": float(np.log2(med / 0.18)),                     # mediana vs cinza 18%
        "rb": float(np.log2(est[0] / est[2])),                   # >0 quente, <0 frio (stops)
        "gm": float(np.log2(est[1] / np.sqrt(est[0] * est[2]))), # >0 verde, <0 magenta
        "est": est.tolist(),
        "p50_ire": float(np.median(yd) * 100),
        "p99_ire": float(np.percentile(yd, 99) * 100),
        "clip_pct": float((disp.max(-1) > 0.985).mean() * 100),
    }


def corrigir(lin, ganho_rgb, stops):
    """Correção primária no linear: balanço (von Kries) + exposição."""
    return lin * np.asarray(ganho_rgb) * (2 ** stops)


# ---------- LUT .cube ----------
def ler_cube(path):
    n, dados = None, []
    for linha in open(path, encoding="utf-8", errors="ignore"):
        s = linha.strip()
        if not s or s.startswith("#"):
            continue
        if s.upper().startswith("LUT_3D_SIZE"):
            n = int(s.split()[1]); continue
        if s[0].isalpha():
            continue
        dados.append([float(v) for v in s.split()[:3]])
    # ordem .cube: R varia mais rápido -> indexar [b, g, r]
    return np.array(dados).reshape(n, n, n, 3)


def aplicar_cube(img, lut, intensidade=1.0):
    n = lut.shape[0]
    p = np.clip(img, 0, 1) * (n - 1)
    i0 = np.floor(p).astype(int).clip(0, n - 2)
    f = p - i0
    r0, g0, b0 = i0[..., 0], i0[..., 1], i0[..., 2]
    fr, fg, fb = f[..., 0:1], f[..., 1:2], f[..., 2:3]
    out = 0
    for db in (0, 1):
        for dg in (0, 1):
            for dr in (0, 1):
                w = (fr if dr else 1 - fr) * (fg if dg else 1 - fg) * (fb if db else 1 - fb)
                out = out + w * lut[b0 + db, g0 + dg, r0 + dr]
    return img + (out - img) * intensidade


# ---------- scopes (desenho) ----------
def parade(disp, altura=180, largura=300):
    """Parade RGB simples: densidade de pixels por coluna/nível, por canal."""
    h, w, _ = disp.shape
    out = np.zeros((altura, largura * 3, 3))
    xs = (np.arange(w) * largura // w)
    for c in range(3):
        v = np.clip((1 - disp[..., c]) * (altura - 1), 0, altura - 1).astype(int)
        hist = np.zeros((altura, largura))
        np.add.at(hist, (v.ravel(), np.tile(xs, h)), 1)
        hist = np.clip(np.log1p(hist) / np.log1p(hist.max() * 0.25 + 1), 0, 1)
        cor = np.zeros(3); cor[c] = 1
        out[:, c * largura:(c + 1) * largura] = hist[..., None] * (cor * 0.85 + 0.15)
    for lvl in (0.0, 0.5, 1.0):  # linhas de 0, 50 e 100%
        out[int((1 - lvl) * (altura - 1))] = np.maximum(out[int((1 - lvl) * (altura - 1))], 0.25)
    return out
