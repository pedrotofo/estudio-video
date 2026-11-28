---
name: conferidor-de-fala
description: >-
  Confere um corte de decupagem já escolhido, com olhos frescos, antes de ir para o Premiere ou
  antes de entregar. Mede pelo som as duas pontas de cada pedaço (fim comido, silêncio no começo,
  contagem colada), roda a trava contra fala inventada, ouve o corte de novo comparando com a
  transcrição e mede o volume. Conserta o que é medida e aponta o que é escolha. Escreve um laudo.
  Use quando pedirem "confere esse corte", "revisa a decupagem", "passa o pente fino", "está tudo
  certo para montar?", depois da /decupagem-falas-premiere e antes de qualquer entrega, ou quando
  uma fala soar cortada, sobreposta ou com o começo comido.
---

# Conferidor de fala

Quem corta não enxerga o próprio erro. Esta skill é o segundo par de olhos: ela recebe **o corte e
o som**, nunca a opinião de quem escolheu os takes.

Nasceu de quatro reclamações do Pedro que a regra já previa e ninguém conferiu:

| Reclamação | Quando |
|---|---|
| Falas "cortadas e sobrepostas" | 17/11/2026, Empresarial da Maria Clara |
| Emendas ajustadas clipe por clipe à mão | 24/11/2026, Treinamento Nov26 da Diamantes |
| Resposta curta comida no começo ("Dá sim.") | 27/11/2026, Black Friday da Maria Clara |
| Fala inventada no roteiro decupado | antes da trava |

Responda em português simples, sem termos técnicos.

## O que esta skill nunca faz

- **Não encosta no Premiere.** Ela confere arquivos. Quem monta é o Premiere, com o Pedro.
- **Não escolhe take.** Se o take está ruim, ela aponta; trocar é decisão do Pedro.
- **Não "melhora" a fala de ninguém.** O texto é o que a pessoa disse.
- **Não dá nota.** Ver "Como julgar", no fim.

## Entradas

A pasta de trabalho da `/decupagem-falas-premiere` (`<work>`), com:

```
<work>/
  wav/<arquivo>.wav     o áudio original de cada clipe
  tr/<arquivo>.json     a transcrição com tempo de cada palavra
  selection.json        os trechos escolhidos (com o campo "texto")
  cuts.json             os pedaços que foram (ou vão) para o Premiere
  gaps.json             falas que o Whisper pulou, se houver
```

Sem `cuts.json` não há o que conferir: peça para rodar o passo 8 da decupagem primeiro.

## Os quatro exames, nesta ordem

**1. Fala inventada** (a trava obrigatória)

```
python -P <skills>/decupagem-falas-premiere/scripts/checar_selecao.py <work>
python -P <skills>/decupagem-falas-premiere/scripts/checar_selecao.py <work> --sel selection_alt.json
```

`DIVERGE` ou `SEM TEXTO` param tudo: o texto do roteiro não é o que a pessoa disse. **Aponta, não
conserta** — pode ser o `start`/`end` cobrindo a fala errada, e isso é escolha.

**2. As duas pontas de cada pedaço**

```
python -P <skills>/conferidor-de-fala/scripts/pontas.py <work>
python -P <skills>/conferidor-de-fala/scripts/pontas.py <work> --cuts cuts_alt.json
```

Mede sobre o som, nunca sobre a transcrição (o WhisperX termina a última palavra cedo demais, ou
estica por segundos sobre o silêncio). Para cada pedaço:

| Medida | O que é | Alvo |
|---|---|---|
| `respiro_fim` | quanto tempo depois da última voz o pedaço termina | ~0,25 s |
| `silencio_inicio` | silêncio entre o começo do pedaço e a primeira voz | até 0,12 s numa ponta de entrada |
| `quieto_antes` | silêncio logo antes do pedaço | 0,25 s ou mais |

`GRAVE` é corte na voz (`respiro_fim` abaixo de 0,10 s) ou clipe entrando antes da voz.
`quieto_antes` curto num começo de fala quase sempre é **contagem colada** — o Ivens grava assim.
Pausa interna (fronteira que não é ponta de fala) tem a folga de 0,15 s que o `build_cuts` deixa.

**3. Ouvir o corte de novo**

```
python -P <skills>/decupagem-falas-premiere/scripts/conferir_corte.py <work>
```

Remonta o áudio exatamente como o `cuts.json` manda, transcreve de novo e compara com o que
deveria estar lá. Palavra que sumiu perto de uma emenda é corte comendo a palavra; longe da
emenda, costuma ser só o Whisper ouvindo diferente. Também mede o volume.

**4. Volume**

O número que vale é o do arquivo exportado, não o do áudio bruto da câmera:

```
python -P <skills>/decupagem-falas-premiere/scripts/conferir_corte.py --arquivo "<exportado.mp4>"
```

Alvo −14 LUFS. **Só mede e conta.** O Pedro é quem limpa e ajusta o áudio.

## Conserta o quê, aponta o quê

| Conserta e conta | Aponta e espera |
|---|---|
| `respiro_fim` curto: estende o `out` até a voz + 0,25 s | take errado ou take ruim |
| `respiro_fim` longo numa ponta de saída: encurta o `out` | fala que deveria ter saído |
| `silencio_inicio` numa ponta de entrada: puxa o `in` para o ataque da voz | ordem das falas |
| pausa interna com ar sobrando | qualquer `DIVERGE` da trava |

Depois de consertar, **rode o `pontas.py` de novo** e diga quantos pedaços foram ajustados. Nunca
conserte invadindo a palavra vizinha: o limite é o som, não o número.

Se o Pedro mandar usar um take que tem defeito: **obedece e registra no laudo**. A palavra é dele.

## Como julgar (regra dura)

Nunca dê nota ("ficou 7 de 10", "está bom"). Nota absoluta não é confiável — a mesma peça vira
"ótima" ou "sem graça" só mudando a pergunta. **Compare duas versões**: a de antes e a de depois do
conserto, ou duas alternativas de take. Rode a comparação **nas duas ordens** (A contra B e B
contra A) e só diga que uma ganhou se ela vencer das duas vezes. Se cada ordem der um vencedor
diferente, a resposta certa é "empate, decide o Pedro".

## O laudo (`<work>/laudo.md`)

1. **Veredito numa linha:** pode montar / conserte antes / pare e decida.
2. **Graves**, um por linha: arquivo, tempo, o que é, o que foi feito.
3. **Avisos** (contagem colada, palavra de confiança baixa, ar sobrando).
4. **Consertado:** quantos pedaços, e quais.
5. **Conferir no ouvido:** a lista curta do que a máquina não resolve.
6. **Volume:** a medida, e quanto falta para −14 LUFS.

## Limites desta versão

- Ela confere o **`cuts.json`**, que é o que foi mandado para o Premiere. Se o Pedro mexeu nos
  clipes à mão depois, o laudo não sabe disso: rode antes de montar, ou peça o `cuts.json` novo.
- O `pontas.py` foi testado em áudio sintético (fim comido, entrada atrasada, contagem colada: os
  três acusados, e o pedaço bom passou limpo). **Primeiro uso em material de verdade: confira o
  laudo contra o ouvido antes de confiar nele.**
- O exame 3 precisa de GPU para ser rápido; sem ela, demora.
- Aprendeu algo num vídeo? Anote aqui, no repositório `pedrotofo/estudio-video`, e peça ao Pedro
  para aprovar.
