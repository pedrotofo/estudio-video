# Sony S-Log3 / S-Gamut3 e S-Gamut3.Cine

Câmeras: A7 IV (ILCE-7M4), A7 V (ILCE-7M5), A7S III, FX3, FX30, FX6, FX9, Venice e outras.

## Como detectar (nesta ordem)
1. **XML da Sony ao lado do clipe** (`<clipe>M01.XML`). Campos úteis:
   - `Device modelName` (ex.: `ILCE-7M5`), `Lens modelName`
   - `CaptureGammaEquation` (`s-log3`, `s-log2`, `rec709`, `hlg`...)
   - `CaptureColorPrimaries` (`s-gamut3`, `s-gamut3-cine`, `rec709`...)
   - `VideoFrame videoCodec` e `captureFps`
   O Premiere 27 **não** mostra esses dados pelo MCP (testado em 25/11/2026), então o script lê o XML direto do disco.
2. **ffprobe**: `pix_fmt` (8 ou 10 bits, 4:2:0 ou 4:2:2), `color_range`, `profile`, bitrate.
3. **Perguntar ao usuário** se não houver XML.
4. **Estatística** (último recurso): histograma comprimido, pretos perto de 9-10% do código e quase nada acima de ~70% indicam log. Avisar que a precisão cai.

## Curva S-Log3 (pública, documento técnico da Sony)
Entrada `x` = reflectância linear (0,18 = cinza 18%). Saída `y` normalizada em código de 10 bits (0-1023):

```
se x >= 0.01125:  y = (420 + log10((x + 0.01) / 0.19) * 261.5) / 1023
senão:            y = (x * (171.2102946929 - 95) / 0.01125 + 95) / 1023
```
Inversa (para linearizar), com `c = y * 1023`:
```
se c >= 171.2102946929:  x = 10^((c - 420) / 261.5) * 0.19 - 0.01
senão:                   x = (c - 95) * 0.01125 / (171.2102946929 - 95)
```

Verificado em 25/11/2026: as constantes da curva e da inversa batem com a IDT da ACES fornecida pela própria Sony (`IDT.Sony.SLog3_SGamut3Cine.ctl`) e com a implementação da colour-science, que cita o documento técnico da Sony. Os valores da tabela abaixo foram recalculados com a fórmula e conferem (90% dá 597,9).
Observação: a fórmula usa `0.19` porque é `0.18 + 0.01`. A entrada é reflectância de cena; a colour-science tem uma opção que multiplica por 0,9 (reflexão x IRE), que **não** se usa aqui.

| Referência | Código 10 bits | % IRE (faixa legal 64-940) |
|---|---|---|
| Preto (0%) | 95 | ~3,5% |
| Cinza 18% | 420 | ~41% |
| Branco 90% | 598 | ~61% |

## Primárias (CIE xy, branco D65 = 0,3127 / 0,3290)
| | R | G | B |
|---|---|---|---|
| S-Gamut3 | 0,730 / 0,280 | 0,140 / 0,855 | 0,100 / -0,050 |
| S-Gamut3.Cine | 0,766 / 0,275 | 0,225 / 0,800 | 0,089 / -0,087 |
| Rec.709 | 0,640 / 0,330 | 0,300 / 0,600 | 0,150 / 0,060 |

Verificado em 25/11/2026 na colour-science (`colour/models/rgb/datasets/sony.py`, que cita o documento técnico e a planilha de matrizes da Sony). Todos os números conferem; nenhum precisou de correção. A matriz RGB→XYZ calculada a partir dessas primárias bate com a da colour-science até a 10ª casa.

## Matrizes lineares para Rec.709 (mesmo branco D65, sem adaptação cromática)
Aplicar **depois** de linearizar com a inversa da S-Log3. Saída: RGB linear com primárias Rec.709 (ainda sem a curva de exibição). Cada linha soma 1, então cinza continua cinza. Valores negativos na saída são cores fora do Rec.709 e precisam de tratamento (clip ou compressão de gamut).

S-Gamut3 → Rec.709:
```
[ 1.8779151284  -0.7941687613  -0.0837463671 ]
[-0.1768069813   1.3509996209  -0.1741926396 ]
[-0.0262011264  -0.1484222623   1.1746233888 ]
```
S-Gamut3.Cine → Rec.709:
```
[ 1.6269474097  -0.5401385389  -0.0868088709 ]
[-0.1785155271   1.4179409275  -0.2394254003 ]
[-0.0444361150  -0.1959199662   1.2403560812 ]
```
Como foram calculadas: `inversa(M_709→XYZ) × M_gamut→XYZ`, com as matrizes normalizadas montadas das primárias acima (método padrão SMPTE RP 177).
Para referência, RGB→XYZ: S-Gamut3 `[0.7064827132 0.1288010498 0.1151721641 / 0.2709796708 0.7866064112 -0.0575860820 / -0.0096778454 0.0046000375 1.0941355587]`; S-Gamut3.Cine `[0.5990839208 0.2489255161 0.1024464902 / 0.2150758201 0.8850685017 -0.1001443219 / -0.0320658495 -0.0276583907 1.1487819910]`.

S-Gamut3 é mais amplo que o .Cine. Aplicar a transformação do .Cine num clipe S-Gamut3 (ou o contrário) desloca matiz e saturação, principalmente em verdes e pele. Sempre usar a transformação do gamut certo.

## Pontos práticos para captação
- S-Log3 pede **ETTR de +1 a +2 stops** (expor acima do "correto" do fotômetro) para limpar ruído nas sombras.
- O ISO base em S-Log3 é alto (a A7 IV/V começam em ISO 800, com segundo ISO base mais alto, conferir por modelo).
- **8 bits + S-Log3 é frágil**: a curva espalha poucos códigos por stop, então puxar contraste gera banding em céu, parede lisa e degradê. Preferir 10 bits 4:2:2 (XAVC S-I ou XAVC HS 10 bits) quando o projeto for ser gradado de verdade.

## Armadilha de faixa (full x legal) — a resolver na Fase 2
Os arquivos H.264 da A7 V testados vêm marcados como `yuvj420p` / `color_range=pc` (faixa cheia). A curva da Sony é definida em código de 10 bits com o preto em 95. Antes de linearizar é preciso confirmar como o código do arquivo se mapeia para esses valores (faixa cheia ou legal), comparando com o que o Premiere e a LUT oficial da Sony produzem. Errar isso desloca toda a exposição medida.

## Dados do material real do usuário (25/11/2026)
- Sony A7 V (ILCE-7M5), S-Log3 / S-Gamut3, H.264 High 8 bits 4:2:0 faixa cheia, 1080p 23,976, ~49 Mbps. A câmera grava ao lado do clipe a referência `SL3SG3tos709.cube`.

## Fontes
- Sony, "Technical Summary for S-Gamut3.Cine/S-Log3 and S-Gamut3/S-Log3" (endereço original, hoje fora do ar): http://community.sony.com/sony/attachments/sony/large-sensor-camera-F5-F55/12359/2/TechnicalSummary_for_S-Gamut3Cine_S-Gamut3_S-Log3_V1_00.pdf
- Sony, planilha de matrizes S-Gamut3/S-Gamut3.Cine (citada pela colour-science): https://community.sony.com/sony/attachments/sony/large-sensor-camera-F5-F55/12359/3/S-Gamut3_S-Gamut3Cine_Matrix.xlsx
- IDT ACES fornecida pela Sony (curva S-Log3): https://github.com/ampas/aces-dev/blob/710ecbe52c87ce9f4a1e02c8ddf7ea0d6b611cc8/transforms/ctl/idt/vendorSupplied/sony/IDT.Sony.SLog3_SGamut3Cine.ctl
- colour-science, curva S-Log3: https://github.com/colour-science/colour/blob/develop/colour/models/rgb/transfer_functions/sony.py
- colour-science, primárias e matrizes Sony: https://github.com/colour-science/colour/blob/develop/colour/models/rgb/datasets/sony.py
