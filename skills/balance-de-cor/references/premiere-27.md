# Premiere Pro 27 + MCP: o que dá para controlar

Testado em 25/11/2026: Premiere 27.0.0 build 88 (Windows), MCP `adobe-premiere-pro-mcp` v1.2.11 (painel CEP "MCP Bridge").
## Regras de segurança
- Nunca testar nem aplicar em projeto de cliente sem pedir. Para experimentos, criar um projeto `Caravela 2026-11 - testes` (sem vírgula nem parênteses no nome).
- **Ler antes de escrever**: `list_clip_effects` / `get_effect_properties` no clipe antes de aplicar. Se já houver Lumetri ou módulo do Color Mode, ajustar o existente em vez de empilhar outro.
- O MCP **não remove efeitos**. Um efeito aplicado por engano fica até o usuário apagar. Por isso: preview antes, aplicar depois da escolha.
- Edição não destrutiva: preferir camada de ajuste ou cópia da sequência quando o usuário pedir algo reversível.

## Efeitos disponíveis no 27 (via `list_available_effects`)
- **Lumetri Color**: 130 propriedades (Basic, Creative/Look, RGB Curves, Hue/Sat Curves, Color Wheels, HSL Secondary, Vignette).
- **Módulos do Color Mode como efeitos comuns**: `Color And Contrast` (Exposure, Contrast, Pivot, Black, Temperature, Tint, Balance e 8 Zones: Highlights, Lighter, Lightest, Custom Highlights, Shadows, Darker, Darkest, Custom Shadows, cada uma com Exposure/Saturation/Direction/Threshold/Width/Temperature/Tint), `Film Color` (Negative, Print, Global Strength, proteções de meio-tom/alta luz/sombra, Saturation Contrast), `Contrast`, `Color Shift`, `Flare`, `Texture`, `HSL Mask`.
- Gerenciamento de cor: `Color Space Transform`, `LUT Transform`, `SDR Conform`, `ASC CDL`, `Video Limiter`, `Broadcast Colors`.
- Plugins de terceiros podem existir (na máquina de referência: Dehancer Pro, Beauty Box, ToneLab Chroma). Verificar antes de sugerir.

## Chamadas que funcionam
| Objetivo | Ferramenta | Argumentos |
|---|---|---|
| Aplicar efeito | `apply_effect` | `{clipId, effectName}`; devolve todas as propriedades com índice |
| Mudar parâmetro | `set_effect_property` | `{clipId, componentName, propertyName, value}`; devolve `before`/`after` |
| Exportar frame | `export_frame` | `{sequenceId, time, outputPath, format:"png"}` |
| Metadados | `get_metadata` | não traz câmera/log; ler o XML da Sony (ver `cameras/sony-slog3.md`) |

## Comportamentos observados
- `export_frame` **inclui** os efeitos aplicados. Sem efeito, sai igual ao arquivo (o projeto novo não converteu log para Rec.709 sozinho). Então: medir no arquivo original com ffmpeg; conferir o resultado com `export_frame`.
- PNG exportado é RGBA 8 bits.
- Propriedades com nome repetido (Temperature, Saturation, Exposure das zonas): pelo nome, só a primeira é atingida.

## Aprendido no primeiro teste real (comercial urbano, 25/11/2026)
- **A Input LUT do Lumetri roda antes de qualquer efeito**, não importa a posição na pilha. Um ASC CDL "acima" do Lumetri é aplicado DEPOIS da LUT (verificado: a mudança no export era exatamente o offset). Para corrigir antes da conversão: gerar uma LUT por clipe = correção no log + conversão (`scripts/assar_lut_wb.py`) e pôr no Input LUT.
- `apply_effect` insere o efeito novo no topo da pilha (posição 2, logo abaixo de Motion).
- O MCP não remove efeitos: para refazer um clipe numa sequência de trabalho, `remove_from_timeline` (lift) + `add_to_timeline` no mesmo ponto.
- `apply_lut` é a forma enxuta de pôr LUT no Input LUT (resposta curta).
- **Nunca chamar ferramenta em lote sem argumentos para "ver o formato"**: `batch_apply_effect {}` rodou em todos os clipes da sequência ativa.
- `export_as_fcp_xml` e qualquer export: a pasta de saída precisa existir, senão o Premiere abre um aviso modal que trava o MCP.
- **Câmera filmada na vertical**: os arquivos Sony têm rotação -90°. O ffmpeg e o Premiere giram; montar miniaturas em 9:16, não 16:9.
- **O instante do ffmpeg e o do Premiere não batem** nos arquivos Sony (diferença de 0,25-0,75 s). Para conferir um export do Premiere contra o original, achar o instante por correlação de imagem (`scripts/conferir_premiere.py`).
- **Lumetri que já existe numa edição com LUT escolhida pela lista do Premiere guarda a LUT embutida** (Blob/Embedded LUTs). `apply_lut` troca o caminho e `set_effect_property Input LUT=0` muda o valor, mas o render NÃO muda. Só funciona em Lumetri novo. Solução: o usuário usa "Remover atributos → Lumetri Color" nos clipes (o MCP não remove efeitos) e a skill aplica Lumetri novos. Conferir sempre exportando antes/depois.
- Uma pasta de "câmera lenta" no projeto não garante que a edição use os clipes interpretados: conferir por imagem (no teste, a edição usava tempo real).
- Uma sequência criada por `create_sequence_from_clips` herda o formato do primeiro clipe (aqui 2160x3840, 59,94).

## Em aberto (testar antes de depender)
1. Endereçar propriedade por índice no `set_effect_property`.
2. Efeitos aplicados via MCP aparecem e são editáveis no workspace Color Mode?
3. Valores do enum `Negative` / `Print` do Film Color (número -> emulação).
4. Color management do projeto (Direct Rec.709 SDR x Wide Gamut Tone Mapped, log automático) e efeito no export.
5. `apply_lut` no slot Look/Creative e no `LUT Transform`.
6. MCP alternativo `premiere-pro-mcp` (leancoderkavy, v1.31.0): lendo o código, ele tem `property_index` (recusa nome ambíguo), `remove_effect`, `paste_clip_attributes` sem perda de cor, ponte UXP com token e telemetria desligada. Riscos abertos: issue #1010 (não abre em certos Windows 11) e #995 (compatibilidade com o 27). Precisa de teste ao vivo antes de adotar; os nomes de argumentos são diferentes (`node_id`, `effect_name`, `property_name`).
