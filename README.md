# Estúdio de Vídeo

Skills do Claude para quem filma clientes falando, edita no Premiere e ilustra as falas com
motion. Este repositório é a **fonte única**: o que está aqui é o que aparece no Claude Code em
qualquer projeto, no computador ou na nuvem.

## Começar uma edição (o passo a passo)

**Uma vez, e sempre que o repositório mudar:**

```bash
cd estudio-video && git pull && bash instalar.sh
```

Use o `instalar.sh` completo, não o `--so-skills`: ele baixa o modelo do detector de rosto e o
opencv. Depois, abra uma **sessão nova** do Claude Code para as skills e os agentes aparecerem.

**A cada vídeo novo, na sua máquina, com o Premiere aberto no projeto:**

| # | Você faz | O que acontece |
|---|---|---|
| 1 | `/caravela-edicao` e manda o áudio do briefing | transcreve no computador, monta o briefing, pergunta só o que faltou e grava `BRIEFING.md` na pasta do job |
| 2 | `/diretor-edicao` | lê o `BRIEFING.md` e o `cliente.md`, acha a pasta de trabalho, e conduz a edição inteira |
| 3 | responde **uma** janela de pergunta | zooms (nenhum / dinâmico / calmo), balanço de cor, motions, sons do Artlist. Só isso é feito |
| 4 | espera nos **três portões** | o roteiro decupado, as prévias de motion e — só em mini-doc — a estrutura. Nada é montado sem o seu ok |
| 5 | no fim, se quiser vertical | peça: `/reel-export`. Não é automático |

Sem áudio de briefing, pule o passo 1 e comece no `/diretor-edicao`: ele faz as perguntas.

**Para uma etapa só**, chame a skill direto: `/decupagem-falas-premiere`, `/zooms-premiere`,
`/balance-de-cor`, `/ilustrar-fala`, `/conferidor-de-fala`, `/revisor-final`.

## O que tem

**Do bruto ao Premiere (skills próprias)**

| Skill | Faz |
|---|---|
| `estudio-video` | O mapa: qual skill usar em cada etapa |
| `diretor-edicao` | **O diretor do time.** Conduz a edição inteira: lê o briefing e o `cliente.md`, pergunta as quatro escolhas uma vez, despacha os especialistas, chama o conferidor antes de montar e segura os três portões que param. É o único que conversa com o Pedro e o único que mexe no Premiere |
| `caravela-edicao` | **A porta de entrada.** `/caravela-edicao`: manda o roteiro do áudio de briefing, transcreve o áudio no computador, monta o briefing, pergunta só o que faltou, grava o `BRIEFING.md` na pasta do job e começa a edição |
| `decupagem-falas-premiere` | **A decupagem.** Dentro do Premiere (MCP): transcreve com WhisperX, escolhe o melhor take de cada fala (com emendas), tira contagem e silêncios, mostra o roteiro decupado para aprovação e monta as sequências "Limpa" e "Alternativas". No fim, lista o que ilustrar e gera a transcrição, a legenda de uma linha e o `decupagem.json` |
| `conferidor-de-fala` | **O segundo par de olhos.** Recebe o corte e o som, nunca a opinião de quem escolheu os takes: mede as duas pontas de cada pedaço (fim comido, silêncio no começo, contagem colada), roda a trava contra fala inventada, ouve o corte de novo e mede o volume. Conserta o que é medida, aponta o que é escolha, escreve o laudo |
| `balance-de-cor` | **Versão de teste.** Balance de cor de uma edição no Premiere, como um colorista: mede cada corte, iguala exposição e branco (no log, antes da conversão Rec.709), cria uma LUT própria por corte e confere antes/depois exportado do Premiere. Hoje: Sony S-Log3 + drone |
| `olheiro-de-rosto` | **O voto do rosto.** Mede enquadramento, mira, giro da câmera, foco, luz e a névoa do teleprompter em cada take candidato, e monta tiras de quadros para a expressão ser julgada olhando. Vota; quando rosto e texto discordam, o texto ganha |
| `zooms-premiere` | Zooms no rosto direto no Premiere: estilo dinâmico (o aprovado no vídeo do luxo do Ivens) ou calmo (o da Diamantes), com backup e um comando para tirar |
| `estruturador` | **A história, quando não há roteiro.** Mapeia as falas (duração, números, nomes, viradas, perguntas, ideias repetidas) e propõe uma ordem — abertura, contexto, virada, prova, fechamento — com o motivo em duas linhas. Era o que faltava para mini-documentário |
| `ilustrar-fala` | Motions sincronizados com a fala, com fundo transparente: mapa do Brasil por estados (malha do IBGE), cidades, rotas, números, listas, lugares reais |
| `revisor-final` | **O último par de olhos.** Antes de entregar ou subir: formato (codec, tamanho, pixel format, faixa de cor, áudio), volume em LUFS e pico, e a área segura do vertical desenhada numa tira de quadros. Mede e conta — não mexe no áudio e não reprova entrega |
| `premiere-xml` | Sem o Premiere aberto: leva o corte, os motions e os marcadores de um arquivo único para o Premiere como timeline editável |

**Motion (pacote que já existia, agora aqui)**: `brand-intake`, `motion-effects`,
`animated-chart`, `title-sequence-3d`, `vox-explainer`, `launch-video`, `apple-launch-film`,
`milestone-reveal`, `interface-escura-3d`, `newsletter-promo`, `loop-cover`, `model-showdown`,
`reel-export`, `motion-brief-writer`, `reference-to-motion`.

**Agentes** (`agents/`): o time de edição, instalado em `~/.claude/agents`. Cada agente é uma casca de poucas linhas que carrega uma skill daqui — o conhecimento fica na skill, nunca no agente, então melhorar o ofício é editar um arquivo e não vários. O desenho do time inteiro está em `PLANO-AGENTES.md`. Hoje: `conferidor-de-fala`, `olheiro-de-rosto`, `estruturador`, `colorista`, `produtor-de-motion` e `revisor-final`. O `colorista` e o `produtor-de-motion` não têm skill própria: vestem a `/balance-de-cor` e a `/ilustrar-fala`, fazendo só a parte que não precisa do Premiere nem do Pedro.

Skills que saíram ficam em `removidas.txt`: o `instalar.sh` apaga a cópia velha delas do computador.

**De terceiros** (`terceiros.txt`, cada uma presa a um commit conferido):
- HyperFrames: `hyperframes`, `hyperframes-cli`, `hyperframes-registry`, `media-use`, e as regras
  de motion do time deles (`motion-doctrine`, `cut-the-curve`, `seam-craft`)
- GSAP oficial: `gsap-core`, `gsap-timeline`, `gsap-plugins`, `gsap-utils`, `gsap-performance`
- `motion-design` (LottieFiles): princípios de timing, easing e coreografia
- `design-taste-frontend` (Taste Skill): estética para páginas e sites
- `frontend-design` (Anthropic): direção visual, tipografia e textos de páginas e interfaces
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

Instala em `~/.claude/skills` e `~/.claude/agents` (vale para todos os projetos) e instala faster-whisper, PyTorch
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
