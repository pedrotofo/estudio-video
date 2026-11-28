"""Mede um vídeo exportado e monta a tira para olhar. Mede e conta: não mexe em nada.

Uso: python -P revisar.py <arquivo.mp4> [--saida <pasta>] [--quadros 6] [--alvo -14]

Regra do Pedro (28/11/2026): o revisor final mede e conta. **Não encosta no áudio** (ele é quem
limpa) e **não reprova entrega**: escreve o laudo, e o diretor mostra.

Mede:
  formato    codec, tamanho, fps, pixel format, faixa de cor, primárias, e se há faixa de áudio
  volume     LUFS integrado e pico real (ebur128), e quanto falta para o alvo
  margens    desenha a área segura do vertical na tira, para a pessoa ver o que encosta na borda

A área segura do vertical é a da /ilustrar-fala: 100 px nas laterais, 180 px em cima e 380 px
embaixo, em 1080x1920 (proporcional em outros tamanhos). Em vídeo horizontal, desenha 5% de margem.

Escreve <saida>/revisao.json e <saida>/tira-revisao.jpg.
"""
import json, os, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
COMUM = os.path.normpath(os.path.join(AQUI, "..", "..", "decupagem-falas-premiere", "scripts"))
if os.path.exists(os.path.join(COMUM, "common.py")):
    sys.path.insert(0, COMUM)
    from common import ffmpeg
else:
    import shutil
    def ffmpeg():
        e = shutil.which("ffmpeg")
        if not e:
            raise SystemExit("ffmpeg não encontrado")
        return e


def ffprobe():
    import shutil
    e = shutil.which("ffprobe") or os.path.join(os.path.dirname(ffmpeg()), "ffprobe")
    if not os.path.exists(e) and not shutil.which("ffprobe"):
        raise SystemExit("ffprobe não encontrado")
    return shutil.which("ffprobe") or e


def formato(caminho):
    r = subprocess.run([ffprobe(), "-v", "error", "-show_streams", "-show_format", "-of", "json", caminho],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    d = json.loads(r.stdout or "{}")
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), None)
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), None)
    if not v:
        raise SystemExit(f"sem faixa de vídeo em {caminho}")
    fps = v.get("avg_frame_rate", "0/1")
    try:
        n, m = fps.split("/"); fps = round(int(n) / int(m), 3) if int(m) else None
    except (ValueError, ZeroDivisionError):
        fps = None
    return {
        "codec": v.get("codec_name"), "largura": v.get("width"), "altura": v.get("height"),
        "fps": fps, "pix_fmt": v.get("pix_fmt"), "faixa_cor": v.get("color_range"),
        "primarias": v.get("color_primaries"), "matriz": v.get("color_space"),
        "duracao_s": round(float(d.get("format", {}).get("duration", 0) or 0), 2),
        "audio": {"codec": a.get("codec_name"), "canais": a.get("channels")} if a else None,
    }


def volume(caminho):
    r = subprocess.run([ffmpeg(), "-nostdin", "-hide_banner", "-i", caminho, "-vn",
                        "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    txt = r.stderr[r.stderr.rfind("Summary:"):]
    lufs = re.search(r"I:\s+(-?[\d.]+) LUFS", txt)
    pico = re.search(r"Peak:\s+(-?[\d.]+) dBFS", txt)
    return {"lufs": float(lufs.group(1)) if lufs else None,
            "pico_dbfs": float(pico.group(1)) if pico else None}


def margens(largura, altura):
    """Área segura. Vertical: a regra da /ilustrar-fala (100/180/380 em 1080x1920). Resto: 5%."""
    if altura > largura:
        e = round(largura * 100 / 1080)
        return {"lado": e, "cima": round(altura * 180 / 1920), "baixo": round(altura * 380 / 1920)}
    e = round(largura * 0.05)
    return {"lado": e, "cima": round(altura * 0.05), "baixo": round(altura * 0.05)}


def confere(f, vol, alvo):
    avisos = []
    if f["codec"] != "h264":
        avisos.append(f"codec {f['codec']}: a entrega para redes é h264 (hevc sobe estranho)")
    if f["pix_fmt"] != "yuv420p":
        avisos.append(f"pixel format {f['pix_fmt']}: as redes querem yuv420p")
    if f["faixa_cor"] == "pc":
        avisos.append("faixa de cor cheia (pc): exporte limitada (tv), senão lava na rede")
    if f["primarias"] and f["primarias"] != "bt709":
        avisos.append(f"primárias {f['primarias']}: o esperado é bt709")
    if not f["audio"]:
        avisos.append("sem faixa de áudio: as redes recusam ou re-codificam; ponha uma faixa muda")
    if f["altura"] > f["largura"] and (f["largura"], f["altura"]) != (1080, 1920):
        avisos.append(f"vertical em {f['largura']}x{f['altura']}: o padrão é 1080x1920")
    if vol["lufs"] is not None:
        d = round(alvo - vol["lufs"], 1)
        if abs(d) >= 1.0:
            avisos.append(f"volume {vol['lufs']} LUFS: faltam {d:+} dB para {alvo} "
                          "(diga ao Pedro; não mexa no áudio)")
    if vol["pico_dbfs"] is not None and vol["pico_dbfs"] > -1.0:
        avisos.append(f"pico em {vol['pico_dbfs']} dBFS: acima de -1 dB pode distorcer na rede")
    return avisos


def tira(caminho, f, m, saida, n):
    import cv2
    import numpy as np
    dur = f["duracao_s"] or 1
    tempos = [dur * p for p in [i / (n + 1) for i in range(1, n + 1)]]
    quadros = []
    for k, t in enumerate(tempos):
        tmp = os.path.join(saida, f"_q{k}.jpg")
        subprocess.run([ffmpeg(), "-nostdin", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}",
                        "-i", caminho, "-frames:v", "1", "-q:v", "3", "-y", tmp], capture_output=True)
        if not os.path.exists(tmp):
            continue
        img = cv2.imread(tmp); os.remove(tmp)
        if img is None:
            continue
        H, W = img.shape[:2]
        cv2.rectangle(img, (m["lado"], m["cima"]), (W - m["lado"], H - m["baixo"]), (0, 220, 255), 3)
        alvo_h = 420
        quadros.append(cv2.resize(img, (int(W * alvo_h / H), alvo_h)))
    if not quadros:
        return None
    larg = min(q.shape[1] for q in quadros)
    nome = os.path.join(saida, "tira-revisao.jpg")
    cv2.imwrite(nome, np.hstack([q[:, :larg] for q in quadros]), [cv2.IMWRITE_JPEG_QUALITY, 85])
    return nome


args = sys.argv[1:]
def opt(n, p=None):
    if n in args:
        i = args.index(n); v = args[i + 1]; del args[i:i + 2]; return v
    return p

SAIDA = opt("--saida")
N = int(opt("--quadros", "6"))
ALVO = float(opt("--alvo", "-14"))
if not args:
    raise SystemExit(__doc__)
arquivo = args[0]
if not os.path.exists(arquivo):
    raise SystemExit(f"não achei {arquivo}")
SAIDA = SAIDA or os.path.dirname(os.path.abspath(arquivo))
os.makedirs(SAIDA, exist_ok=True)

f = formato(arquivo)
vol = volume(arquivo)
m = margens(f["largura"], f["altura"])
avisos = confere(f, vol, ALVO)
try:
    caminho_tira = tira(arquivo, f, m, SAIDA, N)
except ImportError:
    caminho_tira = None
    avisos.append("sem opencv: não montei a tira (rode bash instalar.sh)")

json.dump({"arquivo": os.path.abspath(arquivo), "formato": f, "volume": vol, "alvo_lufs": ALVO,
           "area_segura": m, "avisos": avisos, "tira": caminho_tira},
          open(os.path.join(SAIDA, "revisao.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print(f"{f['largura']}x{f['altura']}  {f['codec']}  {f['fps']} fps  {f['pix_fmt']}  "
      f"faixa {f['faixa_cor']}  {f['duracao_s']}s  áudio: {f['audio'] or 'nenhum'}")
print(f"volume: {vol['lufs']} LUFS (alvo {ALVO}), pico {vol['pico_dbfs']} dBFS")
print(f"área segura desenhada: {m}")
if avisos:
    print("\nAvisos:")
    for a in avisos:
        print("  - " + a)
else:
    print("\nNenhum aviso de formato ou volume.")
print(f"\n-> revisao.json" + (f" e {os.path.basename(caminho_tira)}" if caminho_tira else ""))
print("A borda amarela é a área segura: OLHE a tira e diga o que encosta nela.")
