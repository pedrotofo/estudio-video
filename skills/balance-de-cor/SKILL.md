---
name: balance-de-cor
description: Correção de cor técnica (balance) de uma edição no Premiere Pro, como um colorista sênior. Detecta câmera, perfil log e gamut (ex. Sony S-Log3/S-Gamut3), mede cada corte no trecho usado (exposição, balanço de branco), escolhe o corte de referência (hero), iguala exposição e temperatura na ordem profissional (exposição → branco no log → conversão Rec.709 por último), cria uma LUT própria por corte, mostra antes/depois para aprovação e só então aplica via MCP premiere-pro, conferindo no quadro exportado do próprio Premiere. Use quando pedirem para corrigir cor, balancear, normalizar log, igualar takes, acertar branco ou exposição, mesmo sem dizer "balance". Vem antes de qualquer look criativo.
---

# Balance de cor (correção técnica)

> **Versão de teste 0.3 (26/11/2026).** Testada num comercial real: Sony S-Log3 10 bits + drone Rec.709, 55 cortes. Funciona de ponta a ponta, mas só foi usada num projeto. Limites no fim.

Scripts em `<esta-skill>/scripts/`. Referências (ler quando precisar):
- Ordem e princípios: `references/fluxo.md` e `references/metodo-coloristas.md`
- Curvas e matrizes da câmera: `references/cameras/`
- Métricas: `references/scopes.md`
- **Premiere 27 + MCP, armadilhas reais: `references/premiere-27.md` (ler antes de aplicar)**

Precisa de: Python 3 com numpy e pillow, ffmpeg no PATH e o MCP `premiere-pro` conectado.

## Papel da skill x olhar humano
A skill faz o trabalho objetivo: medir, propor, aplicar e conferir. **Quem decide a intenção é a pessoa**: qual corte é a referência, se uma silhueta fica escura, se o frio da sombra é clima, como está a pele. Por isso: **sempre mostrar o antes/depois e esperar o ok antes de aplicar**.

## Passo 0: material e segurança
- Trabalhar na **timeline que a pessoa indicar**. Nunca trocar por outro projeto "de exemplo".
- **Nunca mexer na sequência original**: `duplicate_sequence` e trabalhar na cópia. Na cópia, tirar look, grão e transições (camadas de cima) para avaliar o balance limpo.
- **Nunca usar LUT pronta de outra pasta** para corrigir. A única LUT externa é a de conversão técnica do próprio Premiere (ex. `Lumetri/LUTs/Technical/Sony S-Log3 to Rec.709 LUT 33x33.cube`); a correção é calculada pela skill.
- Exportar a timeline em XML (`export_as_fcp_xml`; **a pasta de saída tem que existir antes**, senão abre um diálogo que trava o MCP).
- Listar os IDs dos clipes da faixa V1 da cópia, na ordem, num `ids.txt` (um por linha, aninhadas incluídas).
- Exportar **antes de aplicar** um quadro do meio de cada corte da cópia (`export_frame`) para `<saida>/p_antes/NN.png`. É o "antes" da conferência.

## Passo 1: identificar
XML da câmera (Sony `<clipe>M01.XML`) e `ffprobe` (bits, croma, faixa, rotação). Se faltar perfil ou gamut, **perguntar**. Câmera na vertical: miniaturas em 9:16.

## Passo 2: medir e calcular (comando único)
```
python <esta-skill>/scripts/caravela.py balance --xml <timeline.xml> --saida <pasta> \
  --lut-conversao "<LUT técnica S-Log3 → 709 do Premiere>" --pasta-luts <pasta das LUTs> \
  --ids <ids.txt> --titulo "<projeto>"
```
Gera cortes, medidas, hero, uma LUT por corte de câmera, o CDL dos drones, a prévia (`previa - balance antes e depois.jpg`), `plano_aplicacao.json` e `relatorio.md`. Leva uns 8 minutos para ~55 cortes 4K.

O que ele decide:
- 3 quadros **dentro do trecho usado** de cada corte (20/50/80%).
- **Hero** = corte com exposição mais típica, branco mais neutro e boa área neutra. Explicar a escolha.
- **Exposição primeiro**: luma do assunto (sem céu) 75% do caminho até o hero, no máximo ±1,3 stop. Quadro dominado por céu: 35%. Silhueta ou interior escuro (luma < 8%): não mexe.
- **Branco depois**: áreas neutras (asfalto, concreto, carros; sem céu e vegetação) ficam cinza **na imagem convertida**; força 90% (verde/magenta 50%). Sem neutro (< 2% do quadro) ou verde/magenta > 0,35 (folhagem): não corrige e avisa.
- Tudo resolvido como **offset por canal no S-Log3** (exposição = mesmo offset nos 3 canais; branco = diferença entre eles) e conferido depois da conversão. Drone/Rec.709: slope por canal.

## Passo 3: mostrar e pedir aprovação
Mandar a prévia e o relatório, com a lista do que a skill decidiu não mexer e por quê. **Esperar o ok.**

## Passo 4: aplicar (seguir `plano_aplicacao.json`)
- Câmera: LUT do corte no **Input LUT de um Lumetri NOVO** (`apply_lut`, um corte por chamada).
- **Lumetri antigo com LUT escolhida pela lista do Premiere ignora troca de LUT** (fica embutida). O MCP atual não remove efeitos: pedir à pessoa "Remover atributos → Lumetri Color" nos clipes da cópia. O "Color Mode Effect" do Premiere 27, que aparece junto nessa janela, **não altera a cor** (testado: quadro sem Lumetri = arquivo cru).
- Drone: ASC CDL (Red/Green/Blue Slope); zerar ajustes manuais antigos de temperatura.
- **Nunca** chamar ferramenta em lote sem argumentos (`batch_apply_effect` com `{}` roda em todos os clipes).
- Salvar o projeto só com o ok da pessoa.

## Passo 5: conferir (obrigatório)
Exportar o **mesmo quadro** de cada corte depois de aplicar, para `<saida>/p_depois/NN.png`, e rodar:
```
python <esta-skill>/scripts/conferir_edit.py <saida>
```
Compara Premiere x Premiere (mesmo enquadramento) e monta `edicao - balance antes e depois.jpg`. Se o "depois" não mudou ou piorou, **parar e investigar** antes de dizer que funcionou. Números estranhos num corte: **olhar a imagem** antes de concluir (a medida às vezes toma uma lataria azul escura por área neutra).

Se o MCP responder "Bridge is not running" no meio de muitas chamadas, rodar `verify_premiere_connection` uma vez e refazer só as que falharam.

## Resultado no teste (comercial real, 26/11/2026)
- Temperatura: cortes fora da faixa caíram de 22 para 8 (de 52).
- Exposição: cortes a mais de 1 stop da referência caíram de 25 para 17. Melhorou menos do que a prévia indicava.

## Limites desta versão
- Só Sony S-Log3/S-Gamut3 e material Rec.709 (drone). Outras câmeras precisam da curva em `references/cameras/`.
- Sequências aninhadas ficam de fora.
- Depende do "Remover atributos" feito à mão quando a cópia já tinha Lumetri.
- A medida da conferência pode errar em cortes com pouca área neutra; conferir olhando.

## Regras
- Português simples com a pessoa. Números com vírgula.
- Uma etapa por vez: o balance precisa estar aprovado antes de qualquer look.
