---
name: caravela-edicao
description: >-
  Começa um projeto novo de edição de vídeo do Pedro a partir de um briefing por áudio. Manda o roteiro do que
  falar no áudio, recebe o áudio (gravado pelo microfone do app ou como arquivo do WhatsApp/celular), transcreve
  no computador, monta o briefing, pergunta só o que faltou, guarda o briefing na pasta do job e dá a largada na
  edição pelo fluxo do Estúdio de Vídeo. Use quando o Pedro chamar /caravela-edicao ou disser "nova edição",
  "projeto novo de vídeo", "vou te mandar um áudio explicando o vídeo", "briefing de edição", "começar a editar um
  vídeo novo".
---

# Caravela Edição

A porta de entrada de toda edição nova. O Pedro gosta de briefar falando: um áudio longo explicando o trabalho.
Esta skill guia o que ele deve falar, entende o áudio, confirma o que faltou e começa a edição.

Fale com ele em português simples, sem termos técnicos.

## 1. Primeira resposta: o roteiro do áudio

Assim que a skill for chamada, responda só com isto (pode ajustar o tom, não a lista):

> Pode mandar o áudio. Fala à vontade, na ordem que vier, mas tenta passar por estes pontos:
>
> 1. **Cliente e vídeo:** de quem é e que vídeo é esse.
> 2. **Para que serve:** onde vai ser postado, para quem, formato (vertical, horizontal) e mais ou menos quanto tempo.
> 3. **O material:** a pasta do job e como foi gravado: fala para a câmera com vários takes, entrevista, locução ou
>    gravação andando ou em loja. Quem fala.
> 4. **Roteiro:** se tem. Se tiver, cola aqui depois do áudio ou diz onde está.
> 5. **O que entra na edição:**
>    - zooms: nenhum, dinâmico (vídeo animado) ou calmo (institucional)
>    - balanço de cor: sim ou não
>    - motions ilustrando a fala: sim ou não
>    - sons do Artlist: sim ou não, e se quer trilha
> 6. **O resto:** tom, referências, pedidos do cliente, o que evitar, prazo.
>
> Para mandar: grave pelo **microfone do app** (vira texto na hora) ou me mande o **arquivo de áudio** (arraste para
> cá ou diga onde está; se for áudio do WhatsApp salvo nos Downloads, é só dizer "tá nos Downloads").
> Esqueceu algum ponto? Sem problema: eu pergunto só o que faltar.

Se ele já mandou o áudio junto com o comando, pule direto para o passo 2.

## 2. Receber o áudio

- **Texto ditado** (microfone do app): já é a transcrição. Siga.
- **Arquivo** (.ogg, .opus, .m4a, .mp3, .wav, .mp4): transcreva **no computador**, nunca num serviço de fora:
  ```bash
  export PATH="$PATH:/c/Program Files/Python312:/c/Users/pedro/AppData/Local/Microsoft/WinGet/Links"
  python -P <esta-skill>/scripts/transcrever_audio.py "<arquivo>" --saida "<scratchpad>/briefing-audio.txt"
  ```
  Usa a placa de vídeo (um áudio de 5 min leva menos de 1 min). Rode em segundo plano se passar de 10 min.
- **"Tá nos Downloads":** pegue o áudio mais recente de `C:\Users\pedro\Downloads` (extensões acima) e confirme o
  nome do arquivo e a hora na sua resposta.
- Leia a transcrição **inteira** antes de montar qualquer coisa. Nome que a transcrição pode ter errado (cliente,
  loja, produto): confira com a pasta do job e com os clientes conhecidos (CLAUDE.md).

## 3. Montar o briefing

Tire do áudio:
- **cliente** (Riomar, Diamantes, Maria Clara, Novais Arquitetura ou outro) e **nome do vídeo**;
- **para que é**, **formato** (vertical 9:16, horizontal 16:9, quadrado) e **duração** aproximada; **prazo**, se disse;
- **pasta do job**, conferida no disco, e a **sequência** do Premiere, se citou uma;
- **como foi gravado**: fala para a câmera com vários takes, entrevista com perguntas, locução ou narração, ou fala
  andando ou em loja (os quatro tipos da `/decupagem-falas-premiere`); **quem fala**;
- **nomes** que vão aparecer na fala (lojas, produtos, lugares, pessoas): ajudam a transcrição da decupagem;
- **roteiro**: se tem e onde está;
- as **quatro escolhas da edição**: zooms (nenhum, dinâmico ou calmo), balanço de cor, motions, sons do Artlist
  (e trilha);
- **notas**: tom, referências, pedidos do cliente, o que evitar, e tudo do áudio que não coube acima.

**Confira a pasta no disco:** que ela existe, onde está o `.prproj`, quantos vídeos brutos e onde, se há pasta de
artes/PNGs (a identidade para os motions). Se ele não disse a pasta, mostre as pastas de `D:\Jobs` mais recentes e
pergunte. Para Riomar e Diamantes, lembre que os guias deles valem (CLAUDE.md).

Não invente: o que ele não disse e não dá para ver na pasta fica vazio e vira pergunta.

## 4. Mostrar o que entendeu e perguntar só o que falta

Uma mensagem curta: **"Entendi assim:"** e uma tabela de 6 a 10 linhas com o essencial (cliente e vídeo, formato e
duração, pasta e o que achei nela, gravação, roteiro, e as quatro escolhas da edição).

Depois, **uma janela só** do AskUserQuestion com o que faltou, no máximo 4 perguntas. Prioridade: as quatro escolhas
da edição e a pasta; o resto pode ficar vazio. Se nada faltar, só peça o ok.

## 5. Guardar o briefing

Depois do ok, grave `BRIEFING.md` na pasta do job (ao lado do `.prproj`): a tabela aprovada, as notas e, no fim, a
transcrição do áudio. Se já existir um, guarde o anterior como `BRIEFING (anterior).md`. É o que as outras skills e
uma conversa futura leem para continuar o trabalho sem perguntar de novo.

## 6. Dar a largada

- Se esta conversa não estiver aberta na pasta do job, ofereça mudar para ela (ferramenta de mudar de pasta) antes
  de começar: os arquivos de trabalho (`decup/`, `cor/`, `motions/`) ficam lá.
- Siga o fluxo do `/estudio-video`, só com o que ele escolheu, nesta ordem: `/decupagem-falas-premiere` →
  `/balance-de-cor` → `/zooms-premiere` → motions (`/ilustrar-fala`) → sons do Artlist. Cada etapa tem a própria
  aprovação. A pergunta de abertura da decupagem já está respondida pelo briefing: não repita.
- A versão vertical não entra: ele pede no fim, se quiser.

**Briefing escrito em vez de áudio:** trate o texto como a transcrição e siga do passo 3.
