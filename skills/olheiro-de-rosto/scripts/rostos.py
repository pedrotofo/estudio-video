"""Mede o rosto em cada take candidato e monta uma tira de quadros para olhar.

Uso: python -P rostos.py <work> --videos <pasta dos brutos> [--candidatos candidatos.json]
                         [--quadros 3] [--modelo <caminho.onnx>]

Este script MEDE. Ele não escolhe take: quem escolhe é o Pedro, e o texto ganha do rosto
(decisão de 28/11/2026). O que ele entrega é um voto com número, mais a tira de quadros para a
expressão ser julgada olhando.

Entrada: <work>/candidatos.json, no formato
  [{"fala": "abertura", "takes": [{"file": "TOFO9199", "start": 12.3, "end": 18.0}, ...]}, ...]
Sem esse arquivo, usa o selection.json (mede só os takes já escolhidos).

Por take, amostra N quadros e mede em cada um:
  altura_rosto_pct   altura do rosto em % da altura do quadro (enquadramento)
  centro_x/y_pct     onde o rosto está no quadro
  inclinacao_graus   ângulo da linha dos olhos (a câmera da Diamantes fica girada ~2°)
  nitidez            variância do laplaciano no recorte do rosto (take desfocado cai muito)
  luz_rosto          brilho médio do rosto, 0 a 255
  nevoa_baixo        contraste da faixa de baixo contra o meio (névoa do teleprompter)

Escreve <work>/rostos.json e <work>/rostos/<fala>__<file>__<start>.jpg (a tira).
Detector: YuNet (opencv_zoo, MIT, Shiqi Yu). Sem o modelo, o script avisa e sai sem medir rosto.
"""
import json, os, subprocess, sys
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
COMUM = os.path.normpath(os.path.join(AQUI, "..", "..", "decupagem-falas-premiere", "scripts"))
if os.path.exists(os.path.join(COMUM, "common.py")):
    sys.path.insert(0, COMUM)
    from common import ffmpeg
else:
    import shutil
    def ffmpeg():
        exe = shutil.which("ffmpeg")
        if not exe:
            raise SystemExit("ffmpeg não encontrado")
        return exe

sys.stdout.reconfigure(encoding="utf-8")


# ---------- as contas, separadas para poderem ser testadas sozinhas ----------

def inclinacao_graus(olho_dir, olho_esq):
    """Ângulo da linha dos olhos. 0 = reto; positivo = cabeça caída para a direita da imagem."""
    dx = olho_esq[0] - olho_dir[0]
    dy = olho_esq[1] - olho_dir[1]
    if dx == 0 and dy == 0:
        return None
    return round(float(np.degrees(np.arctan2(dy, dx))), 2)


def nitidez(cinza):
    """Variância do laplaciano: quanto maior, mais nítido. Comparável só entre quadros do mesmo vídeo."""
    import cv2
    return round(float(cv2.Laplacian(cinza, cv2.CV_64F).var()), 1)


def faixa_contraste(cinza, de_pct, ate_pct):
    """Desvio padrão e piso de brilho de uma faixa horizontal, em % da altura."""
    h = cinza.shape[0]
    a, b = int(h * de_pct / 100), int(h * ate_pct / 100)
    faixa = cinza[a:b]
    if faixa.size == 0:
        return None
    return {"contraste": round(float(faixa.std()), 1), "piso": round(float(np.percentile(faixa, 5)), 1)}


def nevoa_baixo(cinza):
    """Névoa do teleprompter: a faixa de baixo (15%) perde contraste e levanta o preto contra o meio."""
    baixo, meio = faixa_contraste(cinza, 85, 100), faixa_contraste(cinza, 30, 70)
    if not baixo or not meio or meio["contraste"] == 0:
        return None
    return {"contraste_baixo": baixo["contraste"], "contraste_meio": meio["contraste"],
            "razao": round(baixo["contraste"] / meio["contraste"], 2),
            "piso_subiu": round(baixo["piso"] - meio["piso"], 1)}


def resumo(valores):
    """Mediana dos quadros em que deu para medir. None se nenhum."""
    v = [x for x in valores if x is not None]
    return round(float(np.median(v)), 2) if v else None


# ---------- o resto ----------

def achar_modelo(dado):
    for c in [dado, os.path.join(AQUI, "face_detection_yunet_2023mar.onnx")]:
        if c and os.path.exists(c):
            return c
    return None


def achar_video(pasta, nome, mapa):
    if nome in mapa and os.path.exists(mapa[nome]):
        return mapa[nome]
    if not pasta or not os.path.isdir(pasta):
        return None
    for f in sorted(os.listdir(pasta)):
        raiz, ext = os.path.splitext(f)
        if raiz.lower() == nome.lower() and ext.lower() in (".mp4", ".mov", ".mxf", ".avi", ".mkv", ".m4v"):
            return os.path.join(pasta, f)
    return None


def quadro(video, t, destino):
    r = subprocess.run([ffmpeg(), "-nostdin", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}",
                        "-i", video, "-frames:v", "1", "-q:v", "3", "-y", destino],
                       capture_output=True, text=True)
    return os.path.exists(destino) and os.path.getsize(destino) > 0, r.stderr.strip()


def main():
    import cv2
    args = sys.argv[1:]

    def opt(nome, padrao=None):
        if nome in args:
            i = args.index(nome); v = args[i + 1]; del args[i:i + 2]; return v
        return padrao

    videos_dir = opt("--videos")
    cand_nome = opt("--candidatos", "candidatos.json")
    N = int(opt("--quadros", "3"))
    modelo = achar_modelo(opt("--modelo"))
    work = args[0]

    saida_dir = os.path.join(work, "rostos")
    os.makedirs(saida_dir, exist_ok=True)
    mapa = {}
    mp = os.path.join(work, "videos.json")
    if os.path.exists(mp):
        mapa = json.load(open(mp, encoding="utf-8"))

    cam = os.path.join(work, cand_nome)
    if os.path.exists(cam):
        falas = json.load(open(cam, encoding="utf-8"))
    else:
        sel_path = os.path.join(work, "selection.json")
        if not os.path.exists(sel_path):
            raise SystemExit(f"não achei {cand_nome} nem selection.json em {work}: "
                             "rode a decupagem primeiro, ou escreva o candidatos.json")
        sel = json.load(open(sel_path, encoding="utf-8"))
        falas = [{"fala": s.get("block", f"trecho {k+1}"),
                  "takes": [{"file": s["file"], "start": s["start"], "end": s["end"]}]}
                 for k, s in enumerate(sel)]
        print(f"sem {cand_nome}: medindo os {len(falas)} trechos do selection.json")

    det = None
    if modelo:
        det = cv2.FaceDetectorYN.create(modelo, "", (320, 320))
    else:
        print("AVISO: modelo YuNet não encontrado. Vou medir luz, nitidez e névoa, mas não o rosto.")
        print("       Rode: bash instalar.sh  (ele baixa o modelo), ou passe --modelo <caminho.onnx>")

    tudo, sem_video = [], []
    for f in falas:
        for take in f["takes"]:
            video = achar_video(videos_dir, take["file"], mapa)
            if not video:
                sem_video.append(take["file"]); continue
            a, b = float(take["start"]), float(take["end"])
            tempos = [a + (b - a) * p for p in np.linspace(0.2, 0.8, N)]
            medidas, tiras = [], []
            for k, t in enumerate(tempos):
                tmp = os.path.join(saida_dir, f"_tmp{k}.jpg")
                ok, err = quadro(video, t, tmp)
                if not ok:
                    medidas.append({"t": round(t, 2), "erro": err[:120] or "ffmpeg não gerou o quadro"}); continue
                img = cv2.imread(tmp)
                os.remove(tmp)
                if img is None:
                    medidas.append({"t": round(t, 2), "erro": "quadro ilegível"}); continue
                H, W = img.shape[:2]
                cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                m = {"t": round(t, 2), "nevoa_baixo": nevoa_baixo(cinza), "rosto": None}
                if det is not None:
                    det.setInputSize((W, H))
                    _, faces = det.detect(img)
                    if faces is not None and len(faces):
                        c = max(faces, key=lambda r: r[14])
                        x, y, w, h = [float(v) for v in c[:4]]
                        od, oe = (c[4], c[5]), (c[6], c[7])
                        x0, y0 = max(0, int(x)), max(0, int(y))
                        corte = cinza[y0:int(y + h), x0:int(x + w)]
                        m["rosto"] = {
                            "confianca": round(float(c[14]), 3),
                            "altura_rosto_pct": round(h / H * 100, 1),
                            "centro_x_pct": round((x + w / 2) / W * 100, 1),
                            "centro_y_pct": round((y + h / 2) / H * 100, 1),
                            "olhos_y_pct": round((od[1] + oe[1]) / 2 / H * 100, 1),
                            "inclinacao_graus": inclinacao_graus(od, oe),
                            "nitidez": nitidez(corte) if corte.size else None,
                            "luz_rosto": round(float(corte.mean()), 1) if corte.size else None,
                        }
                        cv2.rectangle(img, (int(x), int(y)), (int(x + w), int(y + h)), (0, 220, 0), 3)
                medidas.append(m)
                alvo_h = 360
                tiras.append(cv2.resize(img, (int(W * alvo_h / H), alvo_h)))

            tira_nome = None
            if tiras:
                largura = min(t.shape[1] for t in tiras)
                tira = np.hstack([t[:, :largura] for t in tiras])
                tira_nome = f"{f['fala']}__{take['file']}__{a:.1f}.jpg".replace("/", "-").replace("\\", "-")
                cv2.imwrite(os.path.join(saida_dir, tira_nome), tira, [cv2.IMWRITE_JPEG_QUALITY, 85])

            rs = [m["rosto"] for m in medidas if m.get("rosto")]
            tudo.append({
                "fala": f["fala"], "file": take["file"], "start": a, "end": b,
                "quadros_medidos": len(medidas), "quadros_com_rosto": len(rs),
                "mediana": {k: resumo([r.get(k) for r in rs]) for k in
                            ("altura_rosto_pct", "centro_x_pct", "centro_y_pct", "olhos_y_pct",
                             "inclinacao_graus", "nitidez", "luz_rosto")} if rs else None,
                "nevoa_baixo": next((m["nevoa_baixo"] for m in medidas if m.get("nevoa_baixo")), None),
                "tira": tira_nome, "quadros": medidas,
            })

    json.dump({"detector": "YuNet" if det is not None else "nenhum", "takes": tudo},
              open(os.path.join(work, "rostos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    for t in tudo:
        med = t["mediana"]
        linha = f"{t['fala'][:28]:28} {t['file']:12} {t['start']:7.2f}  rosto em {t['quadros_com_rosto']}/{t['quadros_medidos']}"
        if med:
            linha += (f"  alt {med['altura_rosto_pct']}%  x {med['centro_x_pct']}%  y {med['centro_y_pct']}%"
                      f"  incl {med['inclinacao_graus']}°  nitidez {med['nitidez']}  luz {med['luz_rosto']}")
        print(linha)
    if sem_video:
        print(f"\nsem vídeo para: {', '.join(sorted(set(sem_video)))} (use --videos <pasta> ou videos.json)")
    print(f"\n{len(tudo)} takes medidos -> rostos.json e {saida_dir}")
    print("A expressão não sai de número: OLHE as tiras em rostos/ antes de votar.")


if __name__ == "__main__":
    main()
