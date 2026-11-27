---
name: decupagem-falas-premiere
description: A decupagem do Estúdio de Vídeo (a única). Decupa falas no Adobe Premiere Pro via MCP premiere-pro, para os vídeos do Pedro (Riomar/Ivens, Maria Clara, Diamantes, Novais e outros). Cobre fala para a câmera com vários takes, entrevista com perguntas, locução/narração e fala gravada andando ou em loja com ruído. Transcreve com WhisperX (tempo de cada palavra), compara os takes com o roteiro quando houver, escolhe o melhor take de cada fala (podendo emendar takes), tira contagem, equipe e silêncios, ordena pela lógica do roteiro, mostra o roteiro decupado para aprovação e só então monta uma sequência limpa, uma sequência de alternativas e um relatório. No fim, lista o que pede motion (lugar, número, lista, produto, citação) com o tempo de cada palavra e gera a transcrição, a legenda de uma linha e o decupagem.json que a /ilustrar-fala usa. Use sempre que o Pedro pedir para decupar, fazer a decupagem ou logagem, transcrever a fala, limpar falas, tirar erros, takes ruins ou silêncios, montar os selects de fala, separar as melhores falas, "o que dá para ilustrar" ou "deixar as falas certinhas", mesmo sem dizer "decupagem".
---

# Decupagem de falas no Premiere (versão 3, 27/11/2026)

A versão 3 juntou aqui o que só a antiga `/decupagem` do Estúdio fazia: a lista do que ilustrar, o roteiro de
motions com prévias e os arquivos que a `/ilustrar-fala` lê (passos 15 e 16). A `/decupagem` foi apagada para não
haver duas skills disputando o mesmo pedido.

O objetivo é entregar ao Pedro uma sequência em que cada fala aparece uma vez, no melhor take, começando
exatamente na primeira sílaba, sem contagem, sem equipe e sem silêncio sobrando, na ordem que conta a história.
O material bruto e a sequência original nunca são alterados.

Já funcionou em: Novais Arquitetura (36 min de bruto viraram 8 min 25 s, com 21 falas e 57 cortes) e no vídeo
do luxo do Riomar com o Ivens. A versão 2 trouxe WhisperX, aprovação antes de montar, sequência de alternativas
e regras para cada tipo de gravação. Backup da versão 1: `C:\Users\pedro\.claude\decupagem-falas-premiere.backup-2026-11-17`.

Responda sempre em português simples, sem termos técnicos.

---

## 1. Decisões já tomadas pelo Pedro (não pergunte de novo)

| Assunto | Regra |
|---|---|
| **Saída** | Sequência NOVA `"<nome> - Limpa"`. Nunca mexer na original. |
| **Alternativas** | Uma segunda sequência `"<nome> - Alternativas"`, com o 2º melhor take de cada fala **na mesma ordem** da Limpa. Fala sem alternativa boa: pula, e o relatório diz isso. |
| **Aprovação** | **Antes de montar no Premiere**, mostrar o *roteiro decupado* (passo 9) e esperar o ok. Só monte depois. |
| **Ordem** | **Pela lógica do roteiro**: abertura, argumento, fechamento. Se o Pedro mandou roteiro ou texto, siga a ordem dele. |
| **Takes** | O melhor take completo de cada fala. **Pode emendar takes** (começo de um com o fim de outro, ou uma retomada pedida pelo diretor) quando o resultado ficar melhor, sempre com a emenda numa pausa natural. |
| **Microcortes** | **NÃO fazer.** Não tirar "é", "né", "tipo", "bom" nem autocorreções de dentro de um take. O Pedro faz isso na edição. |
| **Início da fala** | **Regra crucial (03/11/2026):** o corte começa **exatamente** onde a pessoa começa a falar. Zero silêncio antes e nada da contagem ("vamos lá, um, dois, três, gravando"). Nunca deixe respiro antes. |
| **Fim da fala** | A palavra inteira, **medida pelo som** (nunca pelo tempo da transcrição), mais ~0,25 s de respiro. Com 0,15 s e o fim comido, as falas soaram "cortadas e sobrepostas" (reclamação de 17/11/2026). |
| **Silêncios internos** | Cortar pausas acima de ~0,7 s. Pausas de 0,6 a 0,9 s que soam como respiração natural podem ficar. |
| **Ideias repetidas por pessoas diferentes** | Manter todas. O Pedro escolhe na montagem. |
| **Remover sempre** | Perguntas do entrevistador, conversa da equipe, claquete e contagem, comentários depois do take ("ficou bom?"). |
| **Ruído do áudio** | **O Pedro limpa.** Não coloque áudio tratado na sequência. A limpeza (DeepFilterNet/Demucs) serve **só para transcrever melhor**, por dentro. |
| **Câmeras** | Quase sempre 1 câmera. Se aparecer mais de uma, ou som de lapela separado, pare e pergunte como ele quer. |
| **Roteiro** | Às vezes vem junto. Com roteiro: comparar palavra por palavra. Sem roteiro: deduzir a frase pretendida comparando as repetições. |

**Briefing primeiro:** se o Pedro citar um projeto do Caravela Edit, leia o briefing antes de perguntar qualquer coisa
(`ArtifactData`, `action: "list"`, url `https://claude.ai/artifact/YZiZzizxcHoWPpxcw9hpfa`, `collection: "briefings"`).
Ele já responde quase tudo abaixo: material, roteiro, tipo de gravação e a pergunta 5. Pergunte só o que faltar.

**Pergunte no começo** (AskUserQuestion, uma vez só) apenas o que não dá para saber pelo material:
1. Qual sequência ou quais clipes decupar, se não estiver óbvio.
2. Se tem roteiro ou texto (peça o arquivo, ou que ele cole).
3. Que tipo de gravação é, se não der para ver (seção 3).
4. Algo específico do cliente (seção 4).
5. **O que mais ele quer nesta edição, além da decupagem** (pergunta obrigatória em todo projeto novo, regra do
   Pedro de 27/11/2026; nada disso é automático). Na mesma janela do AskUserQuestion:
   - **Zooms:** nenhum / **dinâmico**, para vídeo animado e interativo (tipo Ivens/Riomar) / **calmo**, para vídeo
     institucional ou documental (tipo Novais, Diamantes). Faz com `/zooms-premiere`.
   - **Balanço de cor:** sim ou não (`/balance-de-cor`).
   - **Motions ilustrando a fala:** sim ou não (passo 16 e `/ilustrar-fala`).
   - **Sons do Artlist** nos motions e na edição: sim ou não.
   Faça só o que ele marcar, na ordem do fluxo (decupagem → cor → zooms → motions → sons). **Não pergunte da versão
   vertical:** ele pede no fim, se quiser. Se ele já disse na mensagem o que quer, não pergunte de novo.

---

## 2. Ferramentas (já instaladas na máquina, RTX 3060 Ti)

Instaladas com `uv tool` em 17/11/2026. Cada uma fica isolada e o executável está em `C:\Users\pedro\.local\bin`.
No Bash, coloque no PATH: `/c/Users/pedro/.local/bin`, `/c/Program Files/nodejs`,
`/c/Users/pedro/AppData/Local/Microsoft/WinGet/Links` (ffmpeg) e `/c/Program Files/Python312`.
As ferramentas só funcionam de dentro do Claude: os ambientes ficam na pasta virtual do app.

| Ferramenta | Para que serve aqui | Comando base |
|---|---|---|
| **WhisperX** (principal) | Transcrição com tempo exato de cada palavra (alinhamento wav2vec2 em português). Mais preciso nos inícios e fins do que o faster-whisper sozinho. Usa a GPU. | `whisperx <wavs> --model large-v3 --language pt --compute_type float16 --batch_size 8 --output_format json --output_dir <work>/wx --initial_prompt "<PROMPT>"` |
| **faster-whisper** (reserva) | Transcrição antiga da skill. Use se o WhisperX falhar, e no `find_gaps.py`. | `python -P scripts/transcribe.py <work>` |
| **DeepFilterNet** | Tira ruído de loja, shopping e ar-condicionado de uma **cópia** do áudio, só para transcrever. | `deepFilter <wav> -o <work>/clean` |
| **Demucs** | Separa a voz da música de fundo (som de loja tocando) numa **cópia**, só para transcrever. | `demucs --two-stems vocals -o <work>/demucs <wav>` |
| **auto-editor** | Mapa rápido de onde tem fala e onde tem silêncio. Na locução longa, gera um pré-corte de referência para o Premiere. | `auto-editor <arquivo> --edit audio:threshold=0.04 --margin 0s,0.15s --export premiere -o <work>/precorte.xml` |
| **PySceneDetect** | Achar mudanças de plano dentro de um arquivo longo (câmera religada, enquadramento trocado). Só quando precisar. | `scenedetect -i <video> detect-content list-scenes -o <work>/cenas` |
| **ffmpeg** | Extrair o áudio dos clipes (`extract_audio.py`). | já é usado pelos scripts |

`PROMPT` do WhisperX (mantém as hesitações e repetições escritas, o que ajuda a ver tropeços):
`Então, é... a gente, a gente trabalha com, eh, com arquitetura. Não, peraí, vou de novo.`

Na primeira vez, o WhisperX baixa os modelos (alguns GB). Rode-o em segundo plano. Os comandos de
DeepFilterNet, Demucs, auto-editor e PySceneDetect acima ainda não foram usados num job real: se algum
parâmetro der erro, veja o `--help` da ferramenta, corrija e atualize esta tabela.

---

## 3. Os quatro tipos de gravação

Identifique o tipo de cada clipe ao ler a transcrição. Um projeto pode misturar tipos.

### A. Fala para a câmera com vários takes (estilo Ivens/Riomar)
- A pessoa repete a mesma fala; o diretor conta antes e comenta depois ("de novo", "perfeito", "só a última frase").
- Agrupe os takes por fala e compare. O melhor é o que está **completo, sem tropeço, com a entonação firme e o
  texto mais fiel** (ao roteiro, se houver). Pese os comentários do diretor.
- Emenda: quando nenhum take está perfeito inteiro, junte a 1ª metade boa de um com a 2ª metade boa de outro,
  **numa pausa natural**, e marque a emenda no roteiro decupado e no relatório.
- Retomada ("só a primeira parte de novo") → emende ao resto do take anterior.

### B. Entrevista com perguntas
- Quem pergunta fala fora de quadro: em geral a voz está **mais baixa ou mais distante** e o texto é pergunta.
  Corte todas as perguntas.
- As respostas são livres e longas. Não existe "take" aqui; o trabalho é **escolher os trechos que contam a
  história** e cortar pausas, recomeços longos ("deixa eu começar de novo") e desvios sem relação com o tema.
- Ideias repetidas em respostas diferentes: mantenha as duas e anote no relatório qual parece melhor.
- Ordem: monte o argumento (apresentação, problema, solução, resultado, fechamento), não a ordem das perguntas.

### C. Locução / narração (ex.: manifesto da Diamantes, locutoras Essence e Jessica)
- Quase sempre tem texto. **Peça o texto** se ele não vier.
- A locutora lê cada frase ou parágrafo mais de uma vez. Decupe **frase por frase**: para cada frase do texto,
  liste as leituras, escolha a melhor e monte na ordem do texto.
- Critério: palavra exata do texto, sem tropeço, sem estalo de boca nem respiração forte no começo, e entonação
  que combine com a frase anterior. O relatório aponta frases em que trocou palavra em **todas** as leituras.
- Pausas entre frases: deixe a respiração natural entre frases (até ~0,6 s). Corte só os silêncios longos.
- Se houver duas locutoras, faça uma Limpa por locutora (`"<nome> - Locução <Nome> - Limpa"`), como no
  projeto Cartas Mágicas (`Manifesto - Locucao Essence.xml` e `Manifesto - Locucao Jessica.xml`).
- O `auto-editor` com `--export premiere` serve como pré-corte de comparação, nunca como entrega.

### D. Fala andando ou em loja (ex.: Maria Clara no Shopping Eusébio)
- Ruído de fundo, gente passando, música da loja, às vezes o microfone da câmera.
- Antes de transcrever, faça uma **cópia limpa só para o Whisper**:
  música de fundo → Demucs (`vocals.wav`); ruído geral → DeepFilterNet. Transcreva a cópia, mas **os tempos e a
  montagem usam o clipe original** (os tempos não mudam, porque os dois processos mantêm a duração).
- Marque os takes com interrupção: alguém passando na frente, barulho alto sobre uma palavra, a pessoa
  esbarrando em algo, risada. Prefira o take sem interrupção mesmo que a fala esteja um pouco pior, e explique
  no relatório.
- Palavras com confiança baixa (`p` < 0,5) num lugar com ruído entram na lista "conferir no ouvido".

---

## 4. Por cliente

- **Riomar (Ivens):** leia antes `E:\Riomar - Guias\Guia de Decupagem - Riomar.md` e o guia de edição na
  mesma pasta (SSD externo "Sandisk 1Tb"). Se o E: não aparecer, peça ao Pedro para conectar o SSD. Estilo aprovado: emendas de take no meio da frase e ordem das falas pelo argumento.
  O Ivens grava com contagem colada na fala, então confira os inícios com cuidado (seção 7).
- **Diamantes:** tom elegante e calmo; nas locuções vale a precisão do texto acima de tudo. Material anterior em
  `D:\Jobs\Diamantes - Cartas Mágicas\Decupagem` (selects e locuções). Para qualquer coisa visual, use o
  design system Diamantes (CLAUDE.md).
  **Vídeos falados (apresentadora explicando produto):** leia antes
  `E:\Diamantes\Diamantes - Guias\Guia de Edição - Vídeos Falados Diamantes.md` (aprovado em 24/11/2026, vídeo do
  acabamento bonder). Pontos que mudam esta skill para a Diamantes:
  - **Uma sequência só**, já quase finalizada: não monte "Alternativas"; as segundas opções vão só no relatório.
  - Escolha o take também pela **expressão do rosto** (olhe quadros de cada take), além do texto e das pausas.
  - **Frases fora do roteiro saem** (o Pedro cortou a pergunta improvisada "E o que isso quer dizer?").
  - A apresentadora grava com **teleprompter** (névoa nos 15% de baixo) e a câmera pode estar girada ~2°: veja a
    seção 4 do guia antes de enquadrar.
- **Maria Clara (Shopping Eusébio):** gravação em loja/shopping, tipo D. Ruído alto é o normal. A narração costuma
  ser gravada com a câmera ligada e virada para o chão (9287 no Natal; 9243 a 9246 na Empresarial): é só áudio e
  precisa de imagem de apoio. O diretor conta "um, dois, três" colado na fala; confira os inícios. Montagens
  anteriores e relatórios em `D:\Jobs\Maria Clara - Shopping Eusébio - Nov26\Claude - Natal` e `Claude - Empresarial`.
- **Cliente novo:** use as regras gerais e anote no relatório o que foi decidido, para virar seção aqui depois.

---

## 5. Pasta de trabalho

Use uma pasta no scratchpad, `<work>`, com esta estrutura (os scripts leem e escrevem nela):

```
<work>/
  ids.json            {"<nome do clipe sem extensão>": "<projectItemId>"}
  wav/*.wav           áudio original extraído (16 kHz mono)
  clean/  demucs/     cópias limpas só para transcrever (tipo D)
  wx/*.json           saída do WhisperX
  tr/*.json           transcrição no formato dos scripts
  all.txt             transcrição legível de tudo
  gaps.json           trechos recuperados pelo find_gaps
  selection.json      escolha final, em ordem de timeline
  selection_alt.json  2º melhor take de cada fala, mesma ordem
  cuts.json batch.json  cuts_alt.json batch_alt.json
  roteiro-decupado.md
```

Scripts em `scripts/` (ao lado deste arquivo). Rode com **`python -P`** (não `-I`, que esconde o faster_whisper).
No PowerShell: `$env:PYTHONIOENCODING="utf-8"`.

---

## 6. Passo a passo

1. **Conectar:** `verify_premiere_connection` (launchIfNeeded false). Se o MCP `premiere-pro` não subir, confira os
   caminhos em `~/.claude.json` → `mcpServers.premiere-pro` (use barras normais `C:/...`).
2. **Inspecionar:** `list_sequences`, `list_sequence_tracks` e `list_project_items`. Anote o fps da sequência
   (fps = 254016000000 / timebase) e grave `<work>/ids.json`. Se houver mais de uma câmera ou áudio separado, pare
   e pergunte.
3. **Extrair áudio:** `python -P scripts/extract_audio.py <work> <caminhos dos clipes...>`
4. **Cópia limpa (só tipo D, ou se a transcrição sair ruim):** Demucs e/ou DeepFilterNet em cada wav. Transcreva a
   cópia, dando a ela **o mesmo nome do wav original** dentro da pasta que vai para o WhisperX, para os nomes
   continuarem batendo com `ids.json`. O `wav/` continua com o áudio original, que é o que o `build_cuts.py` usa
   para medir os silêncios.
5. **Transcrever:** WhisperX em segundo plano (comando na seção 2), depois
   `python -P scripts/whisperx_to_tr.py <work>` → gera `tr/*.json` e `all.txt`.
   Se o WhisperX falhar, use `python -P scripts/transcribe.py <work>` (faster-whisper).
6. **Falas puladas:** `python -P scripts/find_gaps.py <work>`. O Whisper às vezes pula respostas inteiras; isto
   retranscreve trechos com som e sem texto. Quase tudo é equipe ou ruído, mas já recuperou takes de verdade.
7. **Ler e decidir:** leia `all.txt` e a saída do passo 6 **inteiros**. Para cada fala ou frase:
   - liste todos os takes, com arquivo, tempos e o que está errado em cada um;
   - compare com o roteiro, se houver (palavra trocada, palavra faltando);
   - escolha o melhor (seção 3) e o 2º melhor;
   - decida a ordem pela lógica do roteiro.
   Escreva `selection.json` (e `selection_alt.json`) em ordem de timeline. Uma emenda vira **duas entradas
   seguidas com o mesmo `block`**:
   `[{"block": "Abertura", "file": "TOFO8882", "start": 1.38, "end": 12.10}, {"block": "Abertura", "file": "TOFO8885", "start": 14.02, "end": 22.40}, ...]`
   `start` = início da 1ª palavra; `end` = fim (`e`) da última palavra, como veio da transcrição. **Não ajuste o
   `end` à mão:** o `build_cuts.py` acha o fim real pelo som. Só garanta que nenhuma palavra de outra frase (ou do
   diretor) caia antes do `end`.
   **Duas falas seguidas no mesmo take bom:** junte num pedaço só (um `selection` com o `start` da 1ª e o `end`
   da 2ª). Separadas, o fim de uma encosta no começo da outra.
   **Olhe uma foto de cada take antes de escolher:** em alguns clientes (Maria Clara) a narração é gravada com a
   câmera ligada, mas apontada para o chão. O "take com ela falando" pode ser só áudio.
8. **Pré-visualizar os cortes:** `python -P scripts/build_cuts.py <work> <fps>` e
   `python -P scripts/build_cuts.py <work> <fps> --sel selection_alt.json` (este gera `cuts_alt.json` e
   `batch_alt.json`). Eles imprimem o texto final de cada fala; confira se não sobrou palavra de outra frase nem
   faltou o começo.
9. **Aprovação (obrigatória):** escreva `<work>/roteiro-decupado.md`, copie para a pasta da sessão e mostre ao
   Pedro. Formato:

   | # | Bloco | Texto final (como vai ficar) | Take | Emenda? | Alternativa | Observação |
   |---|---|---|---|---|---|---|

   Depois da tabela: falas que ficaram de fora e por quê, inícios para conferir no ouvido (seção 7) e
   duração total. **Espere o ok.** Se ele pedir troca, edite `selection*.json`, rode o passo 8 de novo e mostre só o
   que mudou.
10. **Montar a Limpa:** `duplicate_sequence` (clearContents: true, newName `"<nome> - Limpa"`) e
    `add_to_timeline_batch` com `batch.json` (V1 com o áudio linkado no A1).
11. **Montar as Alternativas:** `duplicate_sequence` (clearContents: true, newName `"<nome> - Alternativas"`) e
    `add_to_timeline_batch` com `batch_alt.json`.
12. **Marcar as emendas:** se existir ferramenta de marcador (`search_tools` "marker"), ponha um marcador em cada
    emenda da Limpa, com o nome do bloco. Se não existir, as emendas ficam só no relatório.
13. **Conferir:** `get_timeline_gaps` deve dar 0 nas duas sequências. Depois `execute_extendscript` com
    `scripts/verify_timeline.jsx` (troque SEQ_ID) e compare com `cuts.json`/`cuts_alt.json`. Um desvio de até
    1 quadro para trás é normal. Confira também **o volume em cada emenda** (últimos e primeiros 60 ms de cada
    pedaço, nos WAVs): tem que estar no nível do ambiente, bem abaixo da fala. Se estiver alto, a palavra foi
    cortada no meio.
    **Não gere prévia em MP4 nem mosaico da montagem:** o Pedro assiste no Premiere (gasta muitos tokens).
14. **Relatório** `.md` na pasta da sessão (seção 8) e lembrar o Pedro de salvar o projeto (Ctrl+S).
15. **Arquivos para as outras skills** (sempre, leva segundos): na pasta do projeto, `decup/` ao lado do bruto,
    nunca dentro de um repositório:
    `python -P scripts/para_estudio.py <work> <fps> "<projeto>/decup" --cliente "<cliente>"`
    Gera `transcricao.json` e `legenda.srt` **no tempo da sequência Limpa** (só as palavras que ficaram) e o
    esqueleto de `decupagem.json` (`references/formato.md`). A legenda já sai em blocos de uma linha.
16. **O que ilustrar e roteiro de motions** (só se o Pedro marcou "motions" na pergunta 5 ou pedir depois):
    - Leia a Limpa inteira e liste cada momento que pede ilustração, escolhendo o tipo pela fala:
      lugar/região/rota → mapa; número ou crescimento → contador ou gráfico; datas → linha do tempo;
      "três coisas", passos → lista item a item; frase forte → citação ou palavra-chave; produto, marca, site →
      imagem real; abstrato → ícone simples, pouco. Ache o tempo das palavras-gatilho com
      `/ilustrar-fala` › `scripts/achar_palavras.py decup/transcricao.json <palavras>`.
    - Preencha `ilustracoes` (com `gatilhos` e `posicao`) e `conferir` no `decupagem.json`.
    - Escreva `roteiro-motion/ROTEIRO DE MOTIONS.md`: tempo, fala com a palavra-gatilho em negrito, o motion, onde
      fica no quadro e o som do Artlist. Regras de bom gosto (guias aprovados do Riomar e da Diamantes): cada motion
      entra na palavra exata e sai antes do próximo, uns 6 a 8 por 40 s; respiros sem nada; nunca em cima do rosto;
      margem de 100 px nas laterais, 180 px em cima e 380 px embaixo no vertical; sem caixa grande atrás do texto;
      formatos variados; os PNGs/KV do cliente são a matéria-prima; um som por motion, ~15 dB abaixo da voz.
    - Peça a identidade mínima do cliente se ainda não tiver (logo PNG, 2 a 4 cores ou o KV, a fonte). Para
      Diamantes e Riomar, use o design system e os guias deles. Nunca invente paleta.
    - Faça 4 a 6 prévias no HyperFrames sobre o quadro real da Limpa (`roteiro-motion/previas.jpg`), **mostre e
      espere o ok**. Só então produza com `/ilustrar-fala`.

**Só mapear o material** (o Pedro pede "só decupa", "o que tem nesse bruto", sem montar nada): faça os passos 1 a 7
sobre os takes escolhidos, sem os passos 10 a 13. Entregue o roteiro decupado com as melhores falas marcadas
(★★★ usaria com certeza, ★★ boa, ★ só se faltar material) e, se ele quiser motions, a lista do que ilustrar.

**Depois da Limpa aprovada e montada**, siga o que ele marcou na pergunta 5: `/balance-de-cor`, `/zooms-premiere` no
estilo escolhido, passo 16 + `/ilustrar-fala`, sons do Artlist. Cada uma tem a própria aprovação.

**Os motions vão para o Premiere** pelo próprio MCP: importe os `.mov` da `/ilustrar-fala` num bin "Motions" e
ponha cada um numa faixa própria acima da fala (V3 em diante), no tempo do `insertos.json` (já no tempo da Limpa).

**Sem Premiere aberto ou na nuvem** (sem o MCP): só dá para levar ao Premiere um **arquivo único** (uma entrevista,
um take só), com `/premiere-xml`. Nesse caso rode o `transcribe.py` sobre o arquivo, escreva `decupagem.json` com os
tempos **do arquivo original** e um `cortes.json` (`[[inicio, fim], ...]`) com os trechos mantidos. Com vários takes,
espere o Premiere aberto.

---

## 7. Armadilhas já resolvidas (leia antes de decidir os cortes)

- **O Whisper esconde a contagem dentro da primeira palavra.** O diretor diz "um, dois, três, gravando" e o
  Whisper não escreve isso: ele estica a primeira palavra para trás, por cima da contagem. O `build_cuts.py`
  começa no **último ataque de voz depois de uma pausa (≥ 0,25 s) antes da 2ª palavra**, com só 0,02 s antes.
  No vídeo do luxo, 10 de 13 inícios ficaram a até 0,13 s do corte manual do Pedro.
  **Ponto fraco:** quando a contagem emenda na fala sem pausa (luxo: TOFO9172 e 9185) ou quando sobra um "E" no
  começo (TOFO9199). O WhisperX alinha melhor a primeira palavra, mas **não confie só nele**: no roteiro decupado e
  no relatório, liste todo início em que o som começa menos de 0,3 s antes da 1ª palavra esperada, para o Pedro
  conferir no ouvido.
- **Fim da fala cortado (corrigido em 17/11/2026, vídeo Empresarial da Maria Clara).** O Pedro reclamou de falas
  "cortadas e sobrepostas". Causas: (1) o fim (`e`) da última palavra do WhisperX não serve: às vezes vem cedo
  demais, e às vezes é esticado por segundos sobre o silêncio; (2) o limite de volume do clipe inteiro (p10 + 10 dB)
  fica acima dos finais fracos ("-sarial", "-ócios", "-ping") quando há som ambiente. Cortou "Empresarial" no meio.
  Agora o `build_cuts.py` acha o fim pelo som: envelope de 10 ms, piso **local** (p20 dos 2 s depois do início da
  última palavra), suavizado em 50 ms, voz = piso + 12 dB, fim = 0,2 s de silêncio, saída = fim + 0,25 s. Testado
  nos 6 takes da Empresarial: todos terminam exatamente 0,25 s depois da voz.
- **As duas pontas de cada emenda (24/11/2026, Treinamento Nov26 da Diamantes).** Na decupagem de 30/10 (antes da
  correção acima) várias falas terminaram cortadas e o take seguinte começou com silêncio até a pessoa falar. O Pedro
  teve de ajustar clipe por clipe: encurtar o começo do take seguinte e esticar o fim do anterior. Regra: depois de
  montar, confira **todas** as emendas pelo som, nas duas pontas: o fim do clipe A termina ~0,25 s depois da voz (nunca
  no meio dela) e o clipe B começa no ataque da voz, com no máximo ~0,05 s de silêncio antes. Corrija antes de entregar
  e diga no relatório quantas emendas foram ajustadas.
- **Transições com som** (ex.: FILMBURNS) tocam por cima da fala: coloque-as com `linkAudio: false`.
- **Premiere puxa o in 1 quadro para trás** ao colocar um clipe. Se precisar estender o out de um clipe já
  colocado (para tapar um buraco de 1 quadro), ele invade o começo do seguinte: recoloque o seguinte depois.
- **faster-whisper + PyAV ≥ 19** quebra (`metadata_errors`). Os scripts passam o áudio como numpy; não passe
  caminho de arquivo para `model.transcribe`.
- **Tempos de palavra esticam sobre as pausas.** Os silêncios são medidos pela energia do áudio (piso de ruído
  p10 + 10 dB), não pelos espaços entre palavras. Em loja com ruído alto esse piso sobe; se o corte comer o fim
  das palavras, rode `build_cuts.py` com respiro maior (`<fps> 0.25`) e avise.
- **WhisperX e números:** palavras como "2026" ou "R$" às vezes vêm sem tempo. O `whisperx_to_tr.py` estima o tempo
  pelas palavras vizinhas e marca confiança 0; elas entram em "conferir no ouvido".
- **Buracos de 1 quadro** entre clipes (fonte 59,94 em sequência 23,976): o `build_cuts.py` já estende cada saída
  em 1 quadro.
- **NÃO use `export_as_fcp_xml`** para conferir: abre um aviso no Premiere que trava a ponte do MCP. Use o
  `verify_timeline.jsx`.
- Se qualquer ferramenta devolver `userActionRequired`, pare e peça ao Pedro para fechar avisos no Premiere e
  conferir o painel MCP Bridge ("Connected").
- `execute_extendscript`: envolva o código numa função que se executa sozinha, com `return`, senão volta
  "undefined".

---

## 8. Relatório final (`Decupagem - <nome>.md`, na pasta da sessão)

1. Resumo: duração do bruto → duração da Limpa, número de falas, de emendas e de cortes.
2. Tabela de falas da Limpa: ordem, bloco, texto, arquivo e tempos, emenda (sim/não).
3. Alternativas: o que está na sequência de Alternativas e as outras leituras descartadas, com tempos.
4. Divergências do roteiro: frases em que nenhum take falou exatamente o texto.
5. **Conferir no ouvido:** inícios suspeitos de contagem, palavras com confiança baixa, takes com ruído ou
   interrupção.
6. O que ficou de fora (equipe, perguntas, falas incompletas) e por quê.
7. Aprendizados deste vídeo que devem virar regra nesta skill. Pergunte ao Pedro se pode atualizá-la.
