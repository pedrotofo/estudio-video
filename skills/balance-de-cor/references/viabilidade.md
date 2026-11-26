# Nota de viabilidade (0 a 10)

Toda sugestão de look vem com uma nota de quanto aquele material aguenta aquele look, e o porquê.

## O que derruba a nota
| Fator | Efeito | Como medir |
|---|---|---|
| 8 bits (principalmente em log) | banding em degradês ao puxar contraste ou saturação | `pix_fmt`; códigos ocupados nos degradês |
| 4:2:0 | bordas de cor sujas em keys e saturação alta | `pix_fmt` |
| Ruído nas sombras | grão de vídeo feio ao abrir sombras ou looks escuros com detalhe | desvio padrão em áreas planas |
| Alta luz estourada | branco duro, sem como recuperar; looks de alto contraste pioram | % clipping por canal |
| Subexposição em log | ruído e cor suja ao normalizar | cinza médio em stops vs 18% |
| Luz mista / sem neutro | WB não fecha para a cena toda | discordância entre estimadores de WB |
| Bitrate baixo | blocos em áreas planas | bitrate do ffprobe |

## Como escrever a nota
- Número + uma frase do motivo principal + o que fazer para proteger (ex.: "aplicar o look com intensidade 70%, adicionar grão leve para mascarar banding").
- **O que mudaria na captação**: 10 bits 4:2:2, ETTR +1 a +2 stops em S-Log3, ND para não estourar, bandeira para controlar luz, etc.
