---
name: estruturador
description: >-
  Propõe a ordem das falas de um mini-documentário ou vídeo institucional quando não existe
  roteiro: abertura, contexto, virada, prova, fechamento, com o motivo em duas linhas. Mapeia as
  falas (duração, números, nomes, viradas, perguntas, ideias repetidas) e devolve uma ordem só,
  para o Pedro aprovar. Use quando pedirem "monta a estrutura", "em que ordem isso conta melhor",
  "não tem roteiro, me ajuda a organizar", "que história dá para contar com isso", ou depois de uma
  decupagem de entrevista sem roteiro.
---

# Estruturador

A `/decupagem-falas-premiere` ordena as falas **pela lógica do roteiro**. Isso supõe que existe um
roteiro. Em mini-documentário de cliente quase nunca existe: no Novais Arquitetura, 36 minutos de
bruto viraram 8 min 25 s com 21 falas e 57 cortes, e a estrutura saiu da cabeça do Pedro, sem estar
escrita em lugar nenhum. Esta skill escreve.

Responda em português simples, sem termos técnicos.

## Três regras

1. **Uma ordem só, com o motivo em duas linhas.** Não três opções: três opções viram trabalho de
   leitura para o Pedro (decisão dele, 28/11/2026).
2. **Ideia repetida fica.** Quando duas pessoas dizem a mesma coisa, as duas entram no mapa e o
   Pedro escolhe na montagem. Você aponta, não apaga.
3. **Você propõe, ele decide.** A estrutura é um dos três portões que param o trabalho: o diretor
   mostra e espera o ok antes de qualquer coisa ser montada.

Você não abre o Premiere e não mexe no corte.

## Rodar

```
python -P <skills>/estruturador/scripts/mapa_falas.py <work>
```

Lê o `selection.json` da decupagem e escreve `<work>/mapa-falas.json`, com duração, tempo
acumulado e, por fala, as marcas:

| Marca | Para que serve |
|---|---|
| `numero` | prova. Quase sempre é também candidata a motion (`/ilustrar-fala`) |
| `nome` | nome próprio no meio da frase: lugar, produto, pessoa. Também vira motion |
| `virada` | "mas", "só que", "acontece que", "o problema". **É o eixo do vídeo** |
| `pergunta` | quase sempre o entrevistador, ou frase improvisada. Na Diamantes, frase fora do roteiro sai |
| `tempo` | ano, década, "há N anos": serve de começo ou de linha do tempo |

E lista pares de falas com vocabulário parecido, acima de 45%.

## Como montar a ordem

A forma que funciona nos vídeos do Pedro:

| Parte | O que é | Onde achar no mapa |
|---|---|---|
| **Abertura** | quem é e o que faz, numa frase que se entende sozinha | fala com `nome`, curta, sem "virada" |
| **Contexto** | como era, o que o cliente sentia | `tempo`, ou fala longa de história |
| **Virada** | o "mas" que faz o vídeo existir | `virada` |
| **Prova** | número, obra, lugar, resultado | `numero`, `nome` |
| **Fechamento** | o que fica, a frase que resume | fala sem marca, costuma ser a mais calma |

Duas travas ao montar:

- **Cada fala tem que causar a seguinte.** Entre uma e outra deve caber "então", "mas" ou "por
  isso". Se só couber "e também", as duas estão no mesmo degrau: junte ou corte uma.
- **A abertura não pode depender de nada anterior.** Se a primeira fala começa com "aí", "e então"
  ou responde uma pergunta que saiu, ela não é abertura.

Fique de olho na duração: o `acumulado` do mapa diz onde o vídeo está. Se a virada cair depois da
metade, o começo está longo demais.

## O que entregar (`<work>/estrutura.md`)

1. **A ordem**, uma linha por fala: posição, o número dela no mapa, a parte (abertura, contexto,
   virada, prova, fechamento), a fala em até 70 caracteres e a duração.
2. **O motivo, em duas linhas.** Por que esta ordem e não a do bruto.
3. **Duração:** quanto dá no total, e onde cai a virada em % do vídeo.
4. **Fora:** falas que você não usou, cada uma com um motivo de meia linha (repetida, pergunta do
   entrevistador, ideia que não encaixa).
5. **Para decidir:** o que depende do Pedro — ideias repetidas, uma fala que serve em dois lugares.
6. **Para ilustrar:** as falas com `numero`, `nome` ou `tempo`, que a `/ilustrar-fala` vai querer.

Nunca dê nota à estrutura. Se estiver escolhendo entre duas ordens, compare as duas nas duas
ordens de apresentação e só declare uma vencedora se ela ganhar das duas vezes; senão, "empate,
decide o Pedro".

## Limites desta versão

- O mapa foi testado com seis falas de exemplo: número, nome, ano, virada, pergunta e uma repetida
  de propósito foram todos acusados certo (60% de vocabulário em comum na repetida).
- A parecença olha **vocabulário**, não sentido: duas falas que dizem a mesma coisa com palavras
  diferentes não aparecem. Leia o mapa inteiro, não só a lista de parecidas.
- O marcador `nome` pega qualquer maiúscula no meio da frase, então nome de mês e começo de frase
  mal transcrito entram. É pista, não verdade.
- Nunca mude o texto de uma fala para a ordem ficar melhor. O texto é o que a pessoa disse.
- Aprendeu algo num vídeo? Anote aqui, no repositório `pedrotofo/estudio-video`, e peça ao Pedro
  para aprovar.
