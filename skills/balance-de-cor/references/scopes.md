# Scopes e métricas (o que o motor mede)

> Fase 1/2: este arquivo define as métricas. Os limites abaixo são pontos de partida e serão calibrados com o conjunto de testes (`testes/`).

Todas as medidas são feitas em frames amostrados do arquivo original (ffmpeg, 16 bits por canal), depois de converter para o espaço de trabalho (Rec.709 / gama 2.4 para entrega SDR, ou linear para cálculos de exposição).

## Exposição (forma de onda / histograma)
- Percentis de luma: p1, p5, p50, p95, p99.
- Cinza médio da cena, preto (p1) e branco (p99) em % IRE.
- **Clipping**: % de pixels com algum canal >= 99% (altas) ou <= 1% (sombras), por canal.
- Para log: medir também em stops relativos ao cinza 18% (via linearização da curva da câmera).

## Balanço de branco (parade RGB)
- Em áreas neutras detectadas (baixa saturação, luma média): desvio de R e B em relação a G.
- Estimativas de iluminante: Gray World, Shades of Gray (p=6) e White Patch, comparadas entre si; se discordarem muito, avisar que a cena não tem neutro confiável.
- Saída: desvio por canal e sugestão de Temperature/Tint.

## Pele (vetorscópio)
- Detectar pele por faixa em YCbCr e/ou detecção de rosto.
- Ângulo de matiz da pele vs **skin tone line** (~123° no vetorscópio Rec.709). Desvio em graus e saturação média da pele.

## Saturação e cor
- Saturação média e p95 (vetorscópio), colorfulness (Hasler e Süsstrunk).
- % de pixels fora do gamut legal de entrega.

## Contraste e curva
- Distância entre p5 e p95 em stops; inclinação nos meios-tons.

## Consistência entre takes
- Diferença de cinza médio, desvio de WB e matiz da pele entre cada take e o hero shot.

## Ruído e banding (para a nota de viabilidade)
- Ruído: desvio padrão em áreas planas das sombras.
- Banding: número de códigos distintos ocupados em degradês suaves (céu, parede) antes e depois do look.
