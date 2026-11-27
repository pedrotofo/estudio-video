# Estúdio de Vídeo

Skills do Claude para quem filma clientes falando, edita no Premiere e ilustra as falas com
motion. Este repositório é a **fonte única**: o que está aqui é o que aparece no Claude Code em
qualquer projeto, no computador ou na nuvem.

## O que tem

**Do bruto ao Premiere (skills próprias)**

| Skill | Faz |
|---|---|
| `estudio-video` | O mapa: qual skill usar em cada etapa |
| `decupagem-falas-premiere` | **A decupagem.** Dentro do Premiere (MCP): transcreve com WhisperX, escolhe o melhor take de cada fala (com emendas), tira contagem e silêncios, mostra o roteiro decupado para aprovação e monta as sequências "Limpa" e "Alternativas". No fim, lista o que ilustrar e gera a transcrição, a legenda de uma linha e o `decupagem.json` |
| `balance-de-cor` | **Versão de teste.** Balance de cor de uma edição no Premiere, como um colorista: mede cada corte, iguala exposição e branco (no log, antes da conversão Rec.709), cria uma LUT própria por corte e confere antes/depois exportado do Premiere. Hoje: Sony S-Log3 + drone |
| `zooms-premiere` | Zooms no rosto direto no Premiere: estilo dinâmico (o aprovado no vídeo do luxo do Ivens) ou calmo (o da Diamantes), com backup e um comando para tirar |
| `ilustrar-fala` | Motions sincronizados com a fala, com fundo transparente: mapa do Brasil por estados (malha do IBGE), cidades, rotas, números, listas, lugares reais |
| `premiere-xml` | Sem o Premiere aberto: leva o corte, os motions e os marcadores de um arquivo único para o Premiere como timeline editável |

**Motion (pacote que já existia, agora aqui)**: `brand-intake`, `motion-effects`,
`animated-chart`, `title-sequence-3d`, `vox-explainer`, `launch-video`, `apple-launch-film`,
`milestone-reveal`, `interface-escura-3d`, `newsletter-promo`, `loop-cover`, `model-showdown`,
`reel-export`, `motion-brief-writer`, `reference-to-motion`.

Skills que saíram ficam em `removidas.txt`: o `instalar.sh` apaga a cópia velha delas do computador.

**De terceiros** (`terceiros.txt`, cada uma presa a um commit conferido):
- HyperFrames: `hyperframes`, `hyperframes-cli`, `hyperframes-registry`, `media-use`, e as regras
  de motion do time deles (`motion-doctrine`, `cut-the-curve`, `seam-craft`)
- GSAP oficial: `gsap-core`, `gsap-timeline`, `gsap-plugins`, `gsap-utils`, `gsap-performance`
- `motion-design` (LottieFiles): princípios de timing, easing e coreografia
- `design-taste-frontend` (Taste Skill): estética para páginas e sites
- `video-editing-skill`: silêncios, "éé", retakes, legenda
- `video-use`: edição por conversa com transcrição no ElevenLabs (envia o áudio para lá)

## Como instalar

### Sessões na nuvem (claude.ai/code, app do celular)

O ambiente da nuvem tem um script de preparação que roda `instalar.sh` sozinho em toda sessão
nova, em qualquer repositório. Nada a fazer.

### No seu computador (Claude Code no desktop ou no terminal)

Uma vez, e de novo quando quiser atualizar:

```bash
git clone https://github.com/pedrotofo/estudio-video.git
cd estudio-video
bash instalar.sh          # no Windows: rode no Git Bash
```

Instala em `~/.claude/skills` (vale para todos os projetos) e instala faster-whisper, PyTorch
(tempo preciso por palavra), HyperFrames e OpenTimelineIO. Para o `video-use`, ponha sua chave do
ElevenLabs em `~/.claude/skills/video-use/.env` (`ELEVENLABS_API_KEY=...`). Precisa de Python 3, Node.js 22+ e ffmpeg. Para atualizar depois:
`git pull && bash instalar.sh`.

## Como mudar uma skill

Edite aqui, faça commit e push. A próxima sessão na nuvem já vem com a mudança; no computador,
`git pull && bash instalar.sh`. Nunca edite a cópia em `~/.claude/skills`: ela é substituída a cada
instalação.

## Privacidade

- A transcrição padrão é local. Só o `video-use` (ElevenLabs) envia áudio, e só quando você pedir.
- O HyperFrames roda com `HYPERFRAMES_NO_TELEMETRY=1`.
- Material de cliente (bruto, `.mov`, decupagens) nunca entra neste repositório (`.gitignore`).
