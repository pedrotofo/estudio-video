#!/usr/bin/env bash
# Instala o Estúdio de Vídeo: as skills deste repositório, as skills de terceiros nas versões
# conferidas (terceiros.txt) e as ferramentas (faster-whisper, HyperFrames, OpenTimelineIO).
#
#   bash instalar.sh            # instala em ~/.claude/skills e ~/.claude/agents (vale para todos os projetos)
#   bash instalar.sh --so-skills   # só copia as skills, sem pip/npm
#
# Roda no Linux (sessões na nuvem do Claude Code), no Mac e no Windows (Git Bash). Pode rodar de
# novo a qualquer hora: atualiza tudo para as versões deste repositório. Um passo que falha só
# avisa e segue, para nunca travar o início de uma sessão.
set -uo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESTINO="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
AGENTES="${CLAUDE_AGENTS_DIR:-$HOME/.claude/agents}"
SO_SKILLS=0; [ "${1:-}" = "--so-skills" ] && SO_SKILLS=1
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
aviso() { echo "  aviso: $*" >&2; }

mkdir -p "$DESTINO"
echo "Estúdio de Vídeo -> $DESTINO"

# 1. Skills deste repositório
for d in "$AQUI"/skills/*/; do
  n="$(basename "$d")"
  rm -rf "${DESTINO:?}/$n" && cp -R "$d" "$DESTINO/$n"
done
echo "  $(ls -d "$AQUI"/skills/*/ | wc -l | tr -d ' ') skills próprias"

# 1b. Skills que saíram do Estúdio (removidas.txt): apaga a cópia velha, se ainda estiver instalada
if [ -f "$AQUI/removidas.txt" ]; then
  tiradas=0
  while read -r n; do
    case "$n" in ""|\#*|*/*|.*) continue ;; esac
    [ -d "$DESTINO/$n" ] && rm -rf "${DESTINO:?}/$n" && tiradas=$((tiradas + 1))
  done < "$AQUI/removidas.txt"
  [ "$tiradas" -gt 0 ] && echo "  $tiradas skills antigas tiradas (removidas.txt)"
fi

# 1c. Agentes deste repositório (~/.claude/agents): os subagentes do time de edição. Um agente é uma
#     casca de poucas linhas que carrega uma skill daqui; o conhecimento fica na skill, nunca no agente.
if [ -d "$AQUI/agents" ]; then
  mkdir -p "$AGENTES"
  n=0
  for f in "$AQUI"/agents/*.md; do
    [ -e "$f" ] || continue
    cp -f "$f" "$AGENTES/$(basename "$f")" && n=$((n + 1))
  done
  echo "  $n agentes -> $AGENTES"
  # agentes que saíram: linhas "agents/<nome>" no removidas.txt (o laço de cima pula linhas com barra)
  if [ -f "$AQUI/removidas.txt" ]; then
    while read -r l; do
      case "$l" in agents/*) rm -f "$AGENTES/${l#agents/}.md" ;; esac
    done < "$AQUI/removidas.txt"
  fi
fi

# 2. Skills de terceiros, cada uma no commit conferido (terceiros.txt: repo commit pasta...)
#    pasta "." = o repositório inteiro é a skill (instalada com o nome do repositório);
#    pasta "origem:nome" = instala a pasta com outro nome.
copiar() {  # copia uma skill trocando a anterior, mas guardando um .env com chave que já estava lá
  local de="$1" n="$2" env=""
  [ -f "$DESTINO/$n/.env" ] && env="$(cat "$DESTINO/$n/.env")"
  rm -rf "${DESTINO:?}/$n" && cp -R "$de" "$DESTINO/$n" && rm -rf "$DESTINO/$n/.git"
  [ -n "$env" ] && printf '%s\n' "$env" > "$DESTINO/$n/.env"
  return 0
}
while read -r repo commit pastas; do
  case "$repo" in ""|\#*) continue ;; esac
  [[ "$commit" =~ ^[0-9a-f]{40}$ ]] || continue          # linhas que não são repositório
  dir="$TMP/$(echo "$repo" | tr / _)"
  # só as pastas das skills, sem o resto do repositório nem arquivos LFS
  esparsas="$(for p in $pastas; do o="${p%%:*}"; [ "$o" = "." ] || printf '/%s/ ' "$o"; done)"
  if git init -q "$dir" && { [ -z "$esparsas" ] || git -C "$dir" sparse-checkout set --no-cone $esparsas; } \
     && git -C "$dir" fetch -q --depth 1 --filter=blob:none "https://github.com/$repo" "$commit" \
     && GIT_LFS_SKIP_SMUDGE=1 git -C "$dir" checkout -q FETCH_HEAD 2>/dev/null; then
    for p in $pastas; do
      o="${p%%:*}"; n="${p#*:}"
      [ "$n" = "$p" ] && n="$(basename "$o")"
      [ "$o" = "." ] && [ "$n" = "." ] && n="${repo#*/}"
      copiar "$dir/$o" "$n"
    done
    echo "  $repo: $(echo $pastas | wc -w | tr -d ' ') skills"
  else
    aviso "não consegui baixar $repo (sem internet?); as outras seguem"
  fi
done < "$AQUI/terceiros.txt"

[ "$SO_SKILLS" = 1 ] && { echo "Pronto (só skills)."; exit 0; }

# 3. Ferramentas
PY="$(command -v python3 || command -v py || command -v python || true)"
if [ -n "$PY" ]; then
  # decupagem, premiere-xml e video-use (requests, librosa, matplotlib, numpy)
  PKGS="faster-whisper av<16 pillow opentimelineio otio-fcp-adapter requests librosa matplotlib numpy opencv-python-headless"
  "$PY" -m pip install -q $PKGS 2>/dev/null \
    || "$PY" -m pip install -q --user $PKGS 2>/dev/null \
    || "$PY" -m pip install -q --break-system-packages $PKGS 2>/dev/null \
    || aviso "pip falhou; rode à mão: $PY -m pip install faster-whisper 'av<16' pillow opentimelineio otio-fcp-adapter"
  "$PY" -c "import faster_whisper" 2>/dev/null && echo "  faster-whisper ok"
  # Tempo preciso por palavra (alinhamento wav2vec2, reserva da /decupagem-falas-premiere): torch + torchaudio.
  # Sem placa NVIDIA no Linux, a versão só-CPU (bem menor). O modelo (1,2 GB) baixa no primeiro uso.
  if ! "$PY" -c "import torch, torchaudio" 2>/dev/null; then
    TORCH_IDX=""
    if [ "$(uname -s)" = "Linux" ] && ! command -v nvidia-smi >/dev/null; then
      TORCH_IDX="--index-url https://download.pytorch.org/whl/cpu"
    fi
    "$PY" -m pip install -q torch torchaudio $TORCH_IDX 2>/dev/null \
      || "$PY" -m pip install -q --user torch torchaudio $TORCH_IDX 2>/dev/null \
      || "$PY" -m pip install -q --break-system-packages torch torchaudio $TORCH_IDX 2>/dev/null \
      || aviso "torch não instalou: a decupagem funciona, com tempo por palavra menos preciso"
  fi
  "$PY" -c "import torch, torchaudio" 2>/dev/null && echo "  alinhamento preciso por palavra ok"
else
  aviso "Python 3 não encontrado (a decupagem precisa dele)"
fi

# WhisperX: a transcrição principal da /decupagem-falas-premiere (tempo exato de cada palavra). Fica isolado num
# "uv tool"; sem o uv, a skill usa o faster-whisper acima como reserva.
if command -v uv >/dev/null; then
  command -v whisperx >/dev/null || uv tool install -q whisperx >/dev/null 2>&1 \
    || aviso "WhisperX não instalou; a decupagem usa o faster-whisper"
  command -v whisperx >/dev/null && echo "  whisperx ok"
fi

# 3b. Modelo do detector de rosto (YuNet, do opencv_zoo; MIT, Shiqi Yu): a /olheiro-de-rosto usa para
#     achar o rosto, medir o enquadramento e o giro da câmera. Preso pelo sha256, que é garantia melhor
#     que um commit: se o conteúdo mudar, não instala. Sem ele a skill ainda mede luz, nitidez e névoa.
MODELO_DIR="$DESTINO/olheiro-de-rosto/scripts"
MODELO="$MODELO_DIR/face_detection_yunet_2023mar.onnx"
MODELO_SHA="8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4"
MODELO_URL="https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
soma() {
  if command -v sha256sum >/dev/null; then sha256sum "$1" | cut -d' ' -f1
  elif command -v shasum >/dev/null; then shasum -a 256 "$1" | cut -d' ' -f1
  elif [ -n "${PY:-}" ]; then "$PY" -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "$1"
  fi
}
if [ -d "$MODELO_DIR" ]; then
  if [ "$(soma "$MODELO" 2>/dev/null)" != "$MODELO_SHA" ]; then
    tmp="$TMP/yunet.onnx"
    if curl -fsSL -o "$tmp" "$MODELO_URL" 2>/dev/null \
       || { [ -n "${PY:-}" ] && "$PY" -c "import urllib.request,sys;urllib.request.urlretrieve(sys.argv[1],sys.argv[2])" "$MODELO_URL" "$tmp" 2>/dev/null; }; then
      if [ "$(soma "$tmp")" = "$MODELO_SHA" ]; then
        mv "$tmp" "$MODELO" && echo "  detector de rosto (YuNet) ok"
      else
        aviso "o modelo YuNet baixou diferente do esperado: não instalei (a /olheiro-de-rosto segue sem rosto)"
      fi
    else
      aviso "não baixei o modelo YuNet (sem rede?): a /olheiro-de-rosto segue sem medir rosto"
    fi
  else
    echo "  detector de rosto (YuNet) ok"
  fi
fi

HF_VERSAO="$(awk '/^hyperframes-cli/{print $2}' "$AQUI/terceiros.txt" | head -1)"
if command -v npm >/dev/null; then
  if [ "$(hyperframes --version 2>/dev/null)" != "${HF_VERSAO:-x}" ]; then
    npm install -g -s "hyperframes@${HF_VERSAO:-latest}" >/dev/null 2>&1 \
      || aviso "npm install -g hyperframes falhou (no Mac/Linux pode pedir sudo); 'npx hyperframes' também funciona"
  fi
  command -v hyperframes >/dev/null && echo "  hyperframes $(hyperframes --version 2>/dev/null)"
else
  aviso "Node.js não encontrado (HyperFrames precisa do Node 22+)"
fi

command -v ffmpeg >/dev/null && echo "  ffmpeg ok" \
  || aviso "ffmpeg não encontrado: Mac 'brew install ffmpeg', Windows 'winget install ffmpeg', Linux 'apt install ffmpeg'"

echo "Pronto. Abra uma sessão nova do Claude Code para as skills aparecerem."
