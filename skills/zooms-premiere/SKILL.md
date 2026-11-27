---
name: zooms-premiere
description: >-
  Zooms de câmera na pessoa que fala, aplicados direto na sequência do Adobe Premiere Pro pelo MCP
  premiere-pro, com keyframes que o Pedro pode abrir, ajustar ou tirar. Dois estilos aprovados: dinâmico
  (Riomar/Ivens: zoom rápido nas palavras fortes, aproximação lenta entre elas, volta ao aberto na troca de
  ideia, mirando o rosto) e calmo (Diamantes: no máximo um zoom lento por trecho, no efeito Transform). Use
  quando pedirem zoom, zoom in, zoom out, punch-in, "aproxima no rosto", "dá um movimento de câmera", "deixa
  mais dinâmico", "brincadeira de câmera", ou depois da /decupagem-falas-premiere num vídeo falado.
---

# Zooms no Premiere

A receita do estilo dinâmico é a dos zooms que o Pedro aprovou no vídeo do luxo com o Ivens (03/11/2026,
sequência "Riomar - Ivens Outubro 2"). Não veio de skill nenhuma: foi feita na hora e virou esta. A do estilo
calmo é a que o próprio Pedro fez à mão no vídeo do bonder da Diamantes (24/11/2026), depois de apagar zooms
picados que não gostou.

Responda em português simples, sem termos técnicos.

## 1. Escolha o estilo pelo cliente

| | **Dinâmico** (Riomar, Maria Clara, conteúdo de redes) | **Calmo** (Diamantes, tom elegante) |
|---|---|---|
| Onde | Keyframes de Escala e Posição no **Movimento** do clipe | Escala no efeito **Transform**; o Movimento fica só com enquadramento, rotação e margem do teleprompter |
| Quantos | Um movimento a cada 2 a 3 s de fala | No máximo **um por trecho**, e só em alguns trechos (3 de 8 no bonder) |
| Zoom rápido (punch-in) | Nas palavras fortes: para 1,30× a 1,60× em **0,12 s** | **Nunca** |
| Aproximação lenta | Entre as palavras fortes: 1,08× a 1,25× ao longo de **2 a 3 s** | O clipe inteiro: 100% → 130% (aproxima) ou 130% → 100% (afasta), 5 a 7 s |
| Volta ao aberto | Quando muda a ideia, ou na troca de take: para 1,0× em 0,12 s | Não tem |
| Começo do clipe | Às vezes já entra um pouco fechado (1,10× a 1,20×) | Aberto ou fechado, conforme o movimento |
| Mira | O rosto (entre os olhos) fica parado na tela; a borda do quadro nunca aparece | Centro do quadro |
| Não fazer | Zoom em cima de imagem de apoio; mais de um punch por frase | Aceleração no rosto antes de cortar, zoom com rampa em palavra, punch no corte, aproximação em todo trecho |

O estilo vem da pergunta de abertura da edição (nenhum / dinâmico / calmo, ver `/estudio-video`). Se ninguém
perguntou, pergunte antes de aplicar: dinâmico para vídeo animado e interativo, calmo para institucional ou
documental (o Novais é calmo). Leia antes o guia do cliente,
se houver: `E:\Riomar - Guias\Guia de Edição e Animações - Riomar.md` (seção 3) e
`E:\Diamantes\Diamantes - Guias\Guia de Edição - Vídeos Falados Diamantes.md` (seções 4 e 5).

## 2. Passo a passo

1. **Conectar e achar a sequência:** `verify_premiere_connection`, `list_sequences`. Anote o `sequenceId`, o tamanho
   do quadro e a faixa da fala (quase sempre V1).
2. **Backup antes de mexer:** `duplicate_sequence` com o nome `"<nome> (backup antes dos zooms)"`.
3. **Ler os clipes da fala:** nodeId, início, fim e in point de cada clipe da faixa (`execute_extendscript` ou as
   ferramentas de leitura da timeline).
4. **Achar as palavras fortes:** use a `transcricao.json` da decupagem (está no tempo da sequência Limpa). Palavra
   forte = a que carrega a ideia da frase: número, nome, adjetivo de impacto, a virada ("mas", "só que"), a pergunta
   final. Em média uma por frase.
5. **Achar o rosto (só no dinâmico):** exporte um quadro de cada clipe com uma grade por cima e marque o ponto entre os
   olhos em pixels do quadro da sequência, no enquadramento base do clipe:
   `ffmpeg -ss <t> -i <clipe> -frames:v 1 -vf "scale=1080:1920,drawgrid=w=108:h=96:t=1:c=yellow@0.5" rosto.jpg`
   (use o tamanho e a escala que o clipe tem na sequência; no 4K vertical em sequência 1080×1920, escala base 50).
6. **Escrever o plano** `plano.json` (formato no começo de `scripts/zooms.py`): um item por clipe, com os eventos no
   tempo da sequência. No dinâmico, alterne: aproximação lenta → punch na palavra forte → segura → volta ao aberto
   na mudança de ideia.
7. **Mostrar o plano ao Pedro** em tabela simples (tempo, palavra, o que a câmera faz) e esperar o ok.
8. **Aplicar:**
   - Calmo: antes, ponha o efeito Transform nos clipes do plano (`search_tools` "apply_effect", efeito "Transform").
   - `python -P scripts/zooms.py plano.json` imprime o script; rode com `execute_extendscript`. Ele devolve uma linha
     por clipe. Clipe que já tinha keyframes ou com o Movimento fora do centro é pulado, com aviso: não force.
9. **Conferir:** exporte 3 a 4 quadros de 2 clipes (no começo, no punch, no fim) pelo próprio Premiere e veja se o
   rosto ficou no lugar e nenhuma borda preta apareceu. Não faça prévia em MP4 da sequência inteira: o Pedro assiste
   no Premiere.
10. **Entregar:** diga em quais clipes entrou zoom e como desfazer (abaixo). Lembre de salvar o projeto (Ctrl+S).

## 3. Desfazer (sem pedir ao Claude)

- Cada clipe: abra **Controles de efeito › Movimento** (dinâmico) ou **Transform** (calmo) e desligue o cronômetro
  de Escala e Posição; ou, no calmo, só desligue o efeito Transform (o "fx").
- Tudo de uma vez: `python -P scripts/zooms.py plano.json --remover` e rode o script; ou volte para a sequência
  "(backup antes dos zooms)".

## 4. O que está testado

- **Dinâmico:** a mesma conta do vídeo do Ivens (rosto parado, borda nunca aparece, keyframes lineares). O script
  daqui foi conferido num clipe simulado; o primeiro uso real deve ser conferido no passo 9 com mais cuidado.
- **Calmo:** os valores são os do Pedro no bonder. O script ainda não rodou num Premiere de verdade: no primeiro
  uso, aplique num clipe só, confira, e depois nos outros. Se o nome da propriedade de escala do Transform vier
  diferente, o script avisa ("Transform sem Escala"): veja o nome com `inspect_effect_parameter_catalog_uxp` ou
  lendo `components[i].properties` e acrescente na lista de nomes do script.
- Aprendeu algo num vídeo? Anote aqui, no repositório `pedrotofo/estudio-video`, e peça ao Pedro para aprovar.
