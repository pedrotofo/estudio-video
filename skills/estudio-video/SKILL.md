---
name: estudio-video
description: >-
  Roteiro do Estúdio de Vídeo: qual skill usar em cada etapa de um vídeo filmado com cliente ou
  entrevistado, do bruto ao Premiere. Decupar falas, tirar silêncios e "éé", ilustrar a fala com
  motion (mapas, números, listas, lugares), legendar, exportar para Premiere e redes. Use no começo
  de qualquer trabalho de edição ou motion ("tenho um vídeo de cliente", "vamos editar", "o que
  dá para fazer com esse material", "monta o fluxo"), quando não estiver claro qual skill de vídeo
  usar, ou para conferir se o Estúdio está instalado.
---

# Estúdio de Vídeo

A pessoa filma clientes falando, edita no **Adobe Premiere Pro** e ilustra as falas com motion.
Este é o mapa das skills. Escolha pelo pedido; não rode tudo sempre.

## O fluxo principal: vídeo falado no Premiere

É o fluxo dos vídeos do Novais, da Diamantes, do Riomar e da Maria Clara. Tudo acontece dentro do Premiere aberto,
pelo MCP `premiere-pro`; nada mexe no bruto nem na sequência original. Antes de começar, leia o guia do cliente
(Riomar e Diamantes têm guias aprovados: veja o CLAUDE.md da pessoa).

**Projeto novo: `/caravela-edicao`.** Quando o Pedro chamar a skill ou disser "nova edição", "projeto novo de vídeo",
"vamos editar um vídeo novo", use a `/caravela-edicao`: ela manda o roteiro do áudio de briefing, transcreve no
computador, pergunta só o que faltou, grava `BRIEFING.md` na pasta do job e dá a largada. Num job que já tem
`BRIEFING.md`, leia ele antes de perguntar qualquer coisa. Se ele não quiser mandar áudio, faça a pergunta de abertura
abaixo.

**Nenhuma etapa além da decupagem é automática.** Sem briefing, em toda edição nova, pergunte primeiro (uma janela só, com
AskUserQuestion) o que o Pedro quer desta vez:
- **Zooms:** nenhum / dinâmico (vídeo animado, interativo, tipo Ivens) / calmo (institucional ou documental, tipo
  Novais e Diamantes);
- **Balanço de cor:** sim ou não;
- **Motions ilustrando a fala:** sim ou não;
- **Sons do Artlist:** sim ou não.

Faça só o que ele marcar. **Não pergunte da versão vertical** (etapa 7): ele pede no fim, se quiser. Se a mensagem
dele já disser o que quer, não pergunte de novo.

| Etapa | Skill | Sai |
|---|---|---|
| 1. Decupar: melhor take de cada fala, sem contagem nem silêncios, na ordem do roteiro; aprovação antes de montar | `/decupagem-falas-premiere` | sequências "Limpa" e "Alternativas", relatório, `decup/transcricao.json`, legenda de uma linha |
| 2. Cor: igualar exposição e branco entre os cortes (S-Log3 → Rec.709) | `/balance-de-cor` | cópia da sequência com uma LUT por corte, antes/depois para aprovar |
| 3. Câmera: zooms no rosto, dinâmico (Riomar) ou calmo (Diamantes) | `/zooms-premiere` | keyframes que dá para desligar, com backup da sequência |
| 4. O que ilustrar e roteiro de motions com prévias (aprovação antes de produzir) | `/decupagem-falas-premiere`, passo 16 | `roteiro-motion/` e `decupagem.json` |
| 5. Produzir os motions, sincronizados palavra por palavra, com fundo transparente | `/ilustrar-fala` (motor: `/hyperframes`; acabamento: `/motion-design`) | `motions/*.mov` numa faixa própria no Premiere |
| 6. Sons dos motions e trilha | Artlist (`search_sfx`, `search_music`), nunca Openverse | lista com o momento de cada som |
| 7. Versão vertical para Reels/TikTok (se o original for horizontal) | `/reel-export` | MP4 1080×1920 |

Atalhos comuns:
- "Só decupa" / "o que tem nesse bruto": etapa 1 no modo "só mapear o material".
- "Decupa e monta": etapa 1, depois as etapas que ele marcou na pergunta de abertura, parando nas aprovações.
- "Faz uns zooms": etapa 3. "Ilustra esse trecho": 4 e 5 só no trecho.

## Outras ferramentas de edição (fora do fluxo principal)

| Quando | Skill |
|---|---|
| Vídeo simples de uma pessoa só, sem Premiere (YouTube, aula): tirar silêncios e "éé" e gerar um MP4 | `/video-editing-skill`, sempre com `"punch_in": 0` (o zoom automático dela é fraco e vai contra a regra da Diamantes) |
| Segunda opinião na transcrição quando a decupagem marca muitos `[?]` | `/video-use` (ElevenLabs: envia o áudio, só com o ok da pessoa) |
| Sem Premiere aberto ou na nuvem, um arquivo único | `/premiere-xml` leva o corte e os motions como XML |
| Separar uma pessoa ou objeto do fundo do vídeo | `/object-separation` |

## Motion e animação

| Pedido | Skill |
|---|---|
| Qualquer vídeo em HTML (base de quase tudo abaixo) | `/hyperframes`, `/hyperframes-cli`, `/hyperframes-registry` (cerca de 450 blocos prontos), `/media-use` |
| Identidade de motion do cliente (cores, fontes, ritmo) | `/brand-intake`, uma vez por cliente |
| 16 efeitos prontos (interface, gráfico que vira linha, tipografia elástica, partículas no logo) | `/motion-effects` |
| Gráfico animado | `/animated-chart` |
| Abertura cinematográfica 3D | `/title-sequence-3d` |
| Explainer estilo documentário | `/vox-explainer` |
| Vídeo de lançamento | `/launch-video`, `/apple-launch-film` |
| Número de marco (seguidores, vendas) | `/milestone-reveal` |
| Apresentar um projeto numa janela 3D escura | `/interface-escura-3d` |
| Newsletter: promo e capa animada | `/newsletter-promo`, `/loop-cover` |
| Comparar 3 IAs no mesmo pedido | `/model-showdown` |
| Gosto e acabamento do motion: timing, easing, coreografia | `/motion-design` (princípios), `/motion-doctrine` e `/cut-the-curve` (continuidade e transições do time do HyperFrames), `/seam-craft` (cortes sem flash) |
| Escrever a animação em GSAP (o motor do HyperFrames) | `/gsap-core`, `/gsap-timeline`, `/gsap-plugins`, `/gsap-utils`, `/gsap-performance` |
| Direção visual de páginas e interfaces (tipografia, paleta, textos) | `/frontend-design` (Anthropic) |
| Estética de páginas e sites (landing page do cliente, portfólio) | `/design-taste-frontend` |
| Motion graphic com estilo de referência (galeria, 5 perguntas, cards para aprovar) | `/claude-video` (usa o HyperFrames) |
| Escrever o pedido de um motion | `/motion-brief-writer` (para construir aqui no Claude Code); `/reference-to-motion` (a partir de um vídeo de referência) |
| Prompt para IA que gera vídeo (MiniMax e parecidos) | `prompts-de-motion` (está na sua conta do Claude) |

**HyperFrames** é o motor de todo motion daqui: gera `.mov` com transparência para o Premiere, as
skills de motion exportam por ele e ele converte projetos Remotion (`npx hyperframes` + skill
`remotion-to-hyperframes` da biblioteca dele). O Remotion não faz parte do Estúdio.

Para um motion com acabamento de profissional: antes de animar, leia `/motion-design` (o porquê de
cada easing e tempo) e `/motion-doctrine` (continuidade entre cenas); depois do `check`, revise o
movimento quadro a quadro com `npx hyperframes snapshot`.

## Pasta de trabalho

Um projeto por vídeo, fora de qualquer repositório git:

```
<Cliente>/<Projeto>/
  bruto/      o material original (nunca alterado)
  decup/      transcrição e decupagem
  edited/     corte da video-editing-skill (prévia + manifest.json)
  motions/    um projeto HyperFrames por ilustração + os .mov
  premiere/   o XML para importar
```

## Regras do Estúdio

- **Material de cliente não sai do computador.** Transcrição local (faster-whisper) por padrão.
  O `/video-use` e o ElevenLabs **enviam o áudio para a ElevenLabs**: use só quando a pessoa pedir
  para aquele material ("pode usar o ElevenLabs"). Ele erra menos que o Whisper local (num teste,
  acertou "três estados" onde o Whisper ouviu "33"), então é uma boa segunda opinião quando a
  decupagem marca muitos `[?]`.
- **ElevenLabs na nuvem:** a chave está guardada no ambiente e é injetada pela rede. O `video-use`
  só pede que a variável exista: rode com `ELEVENLABS_API_KEY=proxy-injected`. No computador, a
  pessoa põe a chave real em `~/.claude/skills/video-use/.env` (o instalador preserva esse arquivo).
- **HyperFrames sem telemetria.** Rode os comandos com `HYPERFRAMES_NO_TELEMETRY=1` e pule as
  "usage notes" e `npx hyperframes events` que as skills dele pedem: o Estúdio deixa isso
  desligado para proteger o material de cliente. Só ligue se a pessoa pedir.
- **Nunca commitar** bruto, `.mov`, decupagem ou transcrição de cliente em repositório.
- O Premiere é o destino: entregue XML + `.mov` com alfa, não um MP4 achatado, a não ser que peçam.

## Onde rodar

- **Claude Code no computador da pessoa (desktop ou terminal):** o lugar certo para material de
  verdade. Os arquivos estão lá, o Premiere também, e transcrever ou renderizar com GPU é rápido.
- **Sessão na nuvem (claude.ai/code, celular):** boa para clipes curtos, testes, motions que não
  dependem do bruto (um mapa, um contador) e para planejar. Vídeo grande é ruim de subir.

## Conferir a instalação

```bash
ls ~/.claude/skills | grep -E 'decupagem|ilustrar-fala|premiere-xml|hyperframes|video-editing'
python3 -c "import faster_whisper" && hyperframes --version && ffmpeg -version | head -1
```

Faltando algo: `bash instalar.sh` no repositório `pedrotofo/estudio-video`.
