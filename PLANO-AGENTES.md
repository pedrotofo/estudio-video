# Plano: o time de agentes do Estúdio de Vídeo

Rascunho para o Pedro aprovar, 28/11/2026. Nada foi construído ainda.

Nove agentes: **um diretor e oito especialistas**. O desenho saiu de três edições que já
fizemos — Riomar (Ivens), Diamantes (bonder) e Novais Arquitetura — e não de um esquema pronto
da internet.

---

## 1. Por que um time, e não mais uma skill

O que custou caro nas três edições não foi falta de método. O método estava escrito e certo:

| Reclamação | Quando | O que falhou |
|---|---|---|
| Falas "cortadas e sobrepostas" | 17/11, Empresarial da Maria Clara | o fim da fala, medido pela transcrição e não pelo som |
| Emendas nas duas pontas, clipe por clipe à mão | 24/11, Treinamento da Diamantes | ninguém conferiu as duas pontas depois de montar |
| Resposta curta comida no começo ("Dá sim.") | 27/11, Black Friday da Maria Clara | a 1ª palavra tomada por contagem |
| Fala inventada | antes da trava | texto do trecho não batia com a transcrição |

Os quatro são erros de **atenção dividida**. Hoje uma sessão só carrega, ao mesmo tempo: 352
linhas da `/decupagem-falas-premiere`, o guia do cliente no SSD, a transcrição inteira, os quadros
dos takes candidatos e o estado do Premiere aberto. Cabe tudo, mas não cabe com cuidado.

**Dividir não é para ir mais rápido. É para cada decisão ter alguém com a cabeça livre nela.**

## 2. A restrição que manda no desenho

O MCP `premiere-pro` é **uma conexão só**. Dois agentes montando a mesma timeline se atropelam:
clipe no lugar errado, `get_timeline_gaps` diferente de 0, backup inútil.

Então a regra do time é:

> Todos analisam **arquivos** em paralelo. **Um só** põe a mão no Premiere.

## 3. Os contratos

Cada agente lê e escreve arquivo, nunca o Premiere nem a cabeça do outro. Quase todos já
existem; o plano só formaliza que são contrato, com o estágio podendo ser retomado de onde parou.

```
<job>/
  BRIEFING.md          a /caravela-edicao escreve. Entrada do diretor
  cliente.md           NOVO. As regras do cliente, fora da skill (seção 6)
  decup/
    transcricao.json   WhisperX, tempo de cada palavra
    all.txt            a transcrição corrida, para ler
    selection.json     o take escolhido de cada fala  <- decupador
    selection_alt.json a segunda opção
    rostos.json        NOVO. O voto de expressão por take  <- olheiro-de-rosto
    cuts.json          os cortes medidos pelo som
    laudo.md           NOVO. O que o conferidor achou, e o que falta corrigir
    estrutura.md       NOVO. A ordem do argumento quando não há roteiro
    roteiro-decupado.md o que vai para a aprovação do Pedro
    decupagem.json     o que ilustrar, com o tempo de cada palavra-gatilho
  motions/             um projeto HyperFrames por ilustração
  premiere/            XML, quando não há Premiere aberto
```

Regra dura, herdada do `documentary-agent-kit`: **um estágio só começa quando o artefato do
anterior existe e passou no portão.** E o portão de licença: todo som e toda footage que entra na
timeline tem a origem registrada (Artlist, arte do cliente, bruto).

## 4. Os nove

| # | Agente | Lê | Entrega | Roda |
|---|---|---|---|---|
| 1 | **`diretor-edicao`** | `BRIEFING.md`, `cliente.md` | despacha, confere cada portão, junta tudo no fim | sozinho, do começo ao fim |
| 2 | **`decupador`** | `transcricao.json`, `all.txt`, `find_gaps`, `rostos.json` | `selection.json`, `selection_alt.json` | **em paralelo por bloco de falas** |
| 3 | **`olheiro-de-rosto`** | quadros de cada take candidato | `rostos.json` | em paralelo com o 2 |
| 4 | **`conferidor-de-fala`** | `selection.json`, `cuts.json`, o som | `laudo.md` | depois do 2, **nunca é o 2** |
| 5 | **`estruturador`** | a decupagem, sem roteiro | `estrutura.md` | antes de montar |
| 6 | **`colorista`** | quadros exportados do Premiere | plano de LUT por corte, antes/depois | em paralelo |
| 7 | **`motionista`** | `decupagem.json` | **um subagente por ilustração**, cada um na sua pasta | paralelo de verdade |
| 8 | **`operador-premiere`** | `cuts.json`, zooms, os `.mov` | Limpa, Alternativas, zooms, V2, marcadores | **serial, sozinho** |
| 9 | **`revisor-final`** | o render | timecode, safe zone 9:16, −14 LUFS, relatório | no fim |

### Os três que hoje não existem

**3. `olheiro-de-rosto`.** O guia da Diamantes manda escolher o take *também* pela expressão do
rosto. Está escrito na skill e na prática ninguém olha quadro de todos os takes — não dá, junto com
o resto. Um agente que só faz isso, faz. Ele também marca o que o guia pede: a névoa do
teleprompter nos 15% de baixo e a câmera girada ~2°.

**4. `conferidor-de-fala`.** A correção estrutural dos quatro erros da seção 1. Roda
`checar_selecao.py` (trava contra fala inventada), `conferir_corte.py`, confere **as duas pontas de
toda emenda** pelo som e todo início suspeito de contagem. **Não pode ser quem escolheu os takes:**
auto-revisão não pega fim de fala comido; revisor independente pega.

**5. `estruturador`.** A decupagem ordena "pela lógica do roteiro". No Novais não havia roteiro: 36
min de bruto viraram 8 min 25 s, 21 falas e 57 cortes, e a estrutura nasceu do que ele falou. Isso
hoje é intuição do Pedro, não skill. É o que falta para mini-documentário.

## 5. Quem faz o quê nos três clientes

| | Riomar (Ivens) | Diamantes | Novais |
|---|---|---|---|
| `decupador` | emenda no meio da frase, ordem pelo argumento | frase fora do roteiro **sai**; uma sequência só, sem Alternativas | ordem pelo argumento |
| `olheiro-de-rosto` | take completo, entonação firme | **manda aqui**: expressão, olhar, teleprompter, giro de 2° | enquadramento |
| `conferidor-de-fala` | contagem colada na fala: todo início é suspeito | as duas pontas das emendas | 57 cortes para conferir |
| `operador-premiere` | zoom **dinâmico**: punch a 1,30–1,60× em 0,12 s na palavra forte; 1,08–1,25× em 2–3 s entre elas; volta a 1,0× na troca de ideia; rosto parado entre os olhos | zoom **calmo**: um por trecho no máximo, 3 de 8; clipe inteiro 100%→130% em 5–7 s, no Transform; nunca punch | calmo |
| `estruturador` | roteiro existe | roteiro existe | **manda aqui** |

## 6. `cliente.md`

As regras do Riomar, da Diamantes e do Novais estão hoje espalhadas na seção 4 da decupagem, na
seção 1 da `/zooms-premiere` e em guias no SSD `E:`. Viram um arquivo por cliente, na pasta do job,
que todo especialista lê antes de começar — como o `brand.md` da `/brand-intake`, mas de edição.

Assim o `olheiro-de-rosto` sabe da névoa do teleprompter sem carregar as 352 linhas da decupagem.
Quando o guia do cliente no `E:` mudar, muda num lugar.

## 7. O que vem emprestado, e de onde

Nada exige copiar código de licença fechada.

| Peça | De onde | Licença |
|---|---|---|
| Diretor, portões por estágio, revisor de olhos frescos | [thenguyentrong/pro-video-editing](https://github.com/thenguyentrong/pro-video-editing) | MIT |
| Contrato por estágio, retomável; portão de licença dos assets | [superz1402/documentary-agent-kit](https://github.com/superz1402/documentary-agent-kit) | MIT |
| Conhecimento separado do executor, com o NLE como rota | [appergb/ClipSkills](https://github.com/appergb/ClipSkills) | MIT |
| Mapas editoriais para a `/ilustrar-fala` | [iart-ai/map-animation-skills](https://github.com/kevinbadi/claude-motion-skills) | MIT |

## 8. A ordem de construção

1. **`conferidor-de-fala`** — o menor, usa scripts que já existem, paga na primeira edição.
2. **`diretor-edicao`** + os contratos — sem ele os outros não se coordenam.
3. **`olheiro-de-rosto`** — junto com o `cliente.md` da Diamantes.
4. **`operador-premiere`** — tira a mão de todos os outros do Premiere.
5. **`estruturador`** — quando entrar o próximo mini-doc.
6. **`colorista`**, **`motionista`**, **`decupador`**, **`revisor-final`** — são skills que já
   existem ganhando casca de agente.

Cada um entra com um teste numa edição de verdade antes do próximo.

## 9. A tela do escritório

O Pedro quer, no fim, a tela pixel com os agentes trabalhando. Isso tem uma consequência de
desenho que precisa valer desde o primeiro agente:

> **Essas telas mostram subagentes, não skills.** Uma skill é invisível para elas. Os nove têm de
> ser agentes de verdade, em `.claude/agents/`, despachados pelo diretor — não nove seções de uma
> skill grande.

É mais uma razão para o desenho acima, além da cabeça livre: o trabalho fica visível.

Opções, todas de graça e locais:

| Projeto | Como mostra | Vale notar |
|---|---|---|
| [orseni/agents-office-mod](https://github.com/orseni/agents-office-mod) | escritório pixel **acima do prompt**, no próprio terminal | mod de hooks, sem servidor e sem dependência; anima pelo que cada um está fazendo. Pede Claude Code 2.1.294+ e terminal truecolor. **A mais simples** |
| [mathiasolofsson87/Claude-agents-office](https://github.com/mathiasolofsson87/Claude-agents-office) | painel ao lado do chat, com `/office` | um retrato por agente na mesa, com a tarefa ao vivo. Pede terminal com imagem (Kitty, Ghostty) |
| [ailtonloures/agents-office](https://github.com/ailtonloures/agents-office) | aplicativo à parte (Electron + Phaser 3) | uma sala por projeto, sem telemetria. Mais bonito, mais peça para manter |
| [paulrobello/claude-office](https://github.com/paulrobello/claude-office) | navegador (Next.js + PixiJS + FastAPI) | tem central entre sessões. O mais pesado |

Começar pelo `agents-office-mod` e trocar depois, se quiser mais. O ganho de verdade vem de ver
**qual portão travou** sem ler log: o `conferidor-de-fala` parado com o laudo aberto diz mais que
qualquer mensagem.

## 10. O que este plano não faz

- Não mexe no bruto nem na sequência original. Nunca.
- Não automatiza aprovação: o roteiro decupado continua esperando o ok do Pedro antes de montar.
- Não manda material de cliente para fora. Transcrição local, como hoje.
- Não resolve o passo que só o Pedro faz: limpar o áudio e a microedição dentro do take.
