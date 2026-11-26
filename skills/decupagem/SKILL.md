---
name: decupagem
description: >-
  Decupa um vídeo de cliente, entrevistado ou depoimento: transcreve local e de graça (faster-whisper,
  tempo por palavra, timecode no fps do vídeo), separa quem fala, marca pausas, divide em temas, dá
  nota às melhores falas (sound bites), aponta erros de transcrição e lista cada momento que pede
  ilustração em motion (um lugar ou mapa citado, um número, uma data, uma lista, um produto, uma
  citação). Pede a identidade visual mínima do cliente (logo, cores, fonte, PNGs/KV) e termina
  sempre num roteiro de motions com prévias sobre o vídeo, para aprovar antes de produzir. Entrega
  decupagem.md para ler, decupagem.json para as próximas skills, legenda .srt, marcadores para o
  Premiere e o roteiro de motions. Use quando pedirem "decupa esse vídeo", "decupagem", "logagem",
  "transcreve a fala", "separa as melhores falas", "quais trechos usar", "marca os sound bites",
  "o que dá para ilustrar nesse vídeo", ou mandarem um vídeo de alguém falando.
---

# Decupagem

Decupar é ouvir o material inteiro uma vez e deixar por escrito, com timecode, o que tem nele e o
que vale usar. A pessoa edita no Premiere; esta skill faz a leitura e entrega o mapa do material.

Regras que não mudam:

1. **As palavras do cliente não são editadas.** Corrija só o que a transcrição ouviu errado, nunca o
   que a pessoa disse. Na dúvida, marque `[?]` e diga o timecode para conferir.
2. **Timecode no fps do vídeo** (HH:MM:SS:FF). É o que o editor procura no Premiere.
3. **Nada sai do computador.** A transcrição é local. Não suba o vídeo do cliente para nenhum serviço.
4. **Material de cliente fica fora do git.** Trabalhe numa pasta de projeto, nunca dentro de um
   repositório de skills.

## Passo 0: o que perguntar (uma mensagem só, só o que não der para ver)

1. Qual arquivo (ou pasta, se forem vários takes) e de quem é a fala.
2. Nomes que vão aparecer: cliente, empresa, produtos, lugares, jargão. Vão em `--termos`.
3. Quantas pessoas falam (só a cliente? entrevistador junto?).
4. Para que é o vídeo e quanto tempo terá (ex.: Reels de 60 s, institucional de 3 min). Isso decide
   a nota das falas.
5. **A identidade visual do cliente, no mínimo** (toda decupagem termina num roteiro de motions,
   Passo 4, e ele precisa disso): logo em PNG com fundo transparente; 2 a 4 cores (ou o KV da
   campanha, de onde se tiram as cores); a fonte, ou uma arte onde ela apareça; e, se houver,
   os PNGs da campanha e um vídeo de referência de motion já aprovado. Se existir
   `brand.md`/`MOTION.md` (`/brand-intake`) ou um guia de edição do cliente, leia antes de
   perguntar. Sem nada disso, pergunte de novo: não invente paleta para cliente.

## Passo 1: transcrever

```bash
python3 <esta-skill>/scripts/transcrever.py VIDEO --saida decup/ --termos "Nome, Empresa, Produto"
# entrevista com duas pessoas:   --falantes 2
# legenda final, máquina com GPU: --modelo large-v3
```

Gera `transcricao.json` (palavras com tempo e confiança), `transcricao.txt`, `pausas.json` e
`legenda.srt`. Vários takes: rode uma vez por arquivo, cada um na sua pasta `decup/<take>/`.

Com `torch` e `torchaudio` instalados (o `instalar.sh` instala), o tempo de cada palavra é
refinado por alinhamento forçado: num teste com tempos conhecidos, erro médio de 18 ms (menos de
1 quadro) contra 125 ms do Whisper puro. É isso que faz o motion acender na palavra. Na primeira
vez ele baixa um modelo de 1,2 GB. `--rapido` pula esse passo.

Muitos `[?]` ou nomes e números errados: ofereça transcrever de novo com o ElevenLabs Scribe
(`/video-use`, `helpers/transcribe.py`), que erra menos, **avisando que o áudio vai para a
ElevenLabs**. Só com o sim da pessoa.

Se faltar `faster-whisper`: `pip install faster-whisper "av<16"` (a versão 16+ do PyAV quebra o
faster-whisper 1.2). Separar falantes pede `pip install pyannote.audio` e `HF_TOKEN`; sem isso,
siga sem separar e diga isso uma vez.

## Passo 2: ler tudo, uma vez

Leia `transcricao.txt` inteiro antes de escrever qualquer coisa. Repare:

- frases marcadas `[?]` (confiança baixa): é onde a transcrição mais erra, principalmente números
  e nomes. Confira no contexto; se não der, deixe para a pessoa ouvir;
- retakes (a mesma ideia dita duas vezes): o último costuma ser o bom;
- números, datas, lugares, nomes próprios, listas ("três coisas"), comparações ("antes e depois"):
  são as falas que pedem ilustração.

## Passo 3: escrever a decupagem

Escreva `decup/decupagem.json` no formato de `references/formato.md` e, a partir dele,
`decup/decupagem.md` para a pessoa ler:

```markdown
# Decupagem: <cliente> — <arquivo> (<duração>, <fps> fps)

## Resumo
3 a 5 linhas: do que a pessoa fala, o tom, a melhor fala do material.

## Melhores falas
| ★ | TC entrada | TC saída | Fala | Uso |
|---|---|---|---|---|
| ★★★ | 00:00:20:03 | 00:00:23:24 | "O nosso sonho agora é chegar em São Paulo..." | fechamento |

## Por tema
### 1. Origem da empresa (00:00:03:07 – 00:00:07:06)
...

## Para ilustrar (motion)
| # | TC | O que ela diz | Ilustração sugerida |
|---|---|---|---|
| I1 | 00:00:07:21 | "Ceará, Pernambuco e Bahia" | Mapa do Nordeste, os três estados acendem um a um no ritmo da fala |

## Conferir
- 00:00:07:21 — a transcrição ouviu "33 estados"; pelo contexto são "três". Ouvir.

## Cortes sugeridos
Pausas longas, hesitações e retakes, com o motivo de cada um.
```

Nota das falas: ★★★ usaria com certeza, ★★ boa, ★ só se faltar material. Seja exigente: num
material de 10 min, poucas falas são ★★★.

**Para ilustrar**, uma linha por momento, com o tempo exato das palavras que disparam a animação
(está em `transcricao.json`, palavra por palavra). A ilustração começa um pouco antes da palavra e
fica na tela enquanto a ideia dura. Escolha o tipo pela fala, não pelo efeito:

| A pessoa fala de | Ilustração |
|---|---|
| Lugares, regiões, rotas, "chegar em São Paulo" | Mapa (estados ou países acendendo, pino pulsando, rota se desenhando, zoom de satélite) |
| Um número, crescimento, "de 1.200 para 40 mil" | Contador ou gráfico que cresce no tempo da fala |
| Datas, uma história em etapas | Linha do tempo |
| "Três coisas", passos, benefícios | Lista que entra item a item |
| Uma frase forte | Citação em tipografia cinética, ou só a palavra-chave destacada |
| Um produto, marca, site, app | Imagem real do produto ou tela, nunca desenho genérico |
| Algo abstrato (confiança, crescimento) | Ícone animado ou metáfora simples; pouco, só se pedir |

## Passo 4: roteiro de motions (obrigatório em vídeo falado)

Vídeo falado sempre ganha motion: é o que deixa a peça agradável e acentua as informações-chave.
Depois da decupagem (e, se a pessoa já cortou a timeline, **sobre a timeline final dela**, com os
tempos recalculados), escreva `roteiro-motion/ROTEIRO DE MOTIONS.md` **antes de produzir qualquer
motion**:

1. **Reassista o material inteiro**: um quadro a cada 1 a 1,5 s da timeline (mosaico) e a fala
   palavra por palavra. Marque onde está o rosto em cada plano.
2. **Uma tabela**: tempo, fala (com a palavra-gatilho em negrito), o motion, onde fica no quadro e
   o som. Marque como *opcional* o que é bom mas não essencial.
3. **Regras de bom gosto** (vêm dos guias aprovados do Riomar e da Diamantes):
   - cada motion entra na palavra exata e sai antes do próximo; uns 6 a 8 motions por 40 s;
   - deixe **respiros** (pergunta para a câmera, stop motion, momento de expressão) sem nada;
   - nunca em cima do rosto, nem quando a pessoa anda ou chega perto: terço de cima ou faixa de
     60–82% da altura, conforme o plano;
   - **respiro nas bordas**: em vertical, 100 px nas laterais, 180 px em cima e 380 px embaixo
     (contando brilho e sombra); medido com `/ilustrar-fala` › `scripts/margens.py`;
   - encerramento termina montado e parado, sem fusão com arte de layout diferente;
   - sem caixa/card grande atrás do texto; pílulas pequenas, letreiros e ícones;
   - formatos variados (logo se montando, contador, calendário, lista, seta para o objeto real,
     balão), sem repetir a mesma animação o vídeo todo;
   - **os PNGs/KV do cliente são matéria-prima**: o motion é feito a partir deles (partes do logo
     se montando, data virando calendário, KV montando em camadas), não colado parado;
   - um efeito sonoro por motion, baixinho (~15 dB abaixo da voz).
4. **Prévias**: 4 a 6 quadros dos motions principais, feitos no HyperFrames **sobre o quadro real**
   do vídeo (com a cor final), juntos em `roteiro-motion/previas.jpg`.
5. **Mostre o roteiro e as prévias e espere o ok.** Só então produza com `/ilustrar-fala`
   (cada motion em `.mov` ProRes 4444 com transparência, numa faixa própria no Premiere).

## Passo 5: entregar

- Mostre o resumo, as ★★★, a lista "Para ilustrar" e o roteiro de motions com as prévias; o resto
  fica em `decupagem.md`.
- Ofereça os próximos passos:
  - **marcadores no Premiere**: `/premiere-xml` com `decupagem.json` cria a sequência com um
    marcador colorido em cada fala boa e em cada ponto de ilustração;
  - **ilustrar**: `/ilustrar-fala` gera os motions de cada linha de "Para ilustrar", já no tempo
    certo, com fundo transparente;
  - **tirar silêncios e "éé"**: `/video-editing-skill` faz o corte; `/premiere-xml` leva o corte
    para o Premiere como uma timeline editável.
