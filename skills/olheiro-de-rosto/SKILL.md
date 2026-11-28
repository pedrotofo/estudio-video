---
name: olheiro-de-rosto
description: >-
  Olha o rosto em cada take candidato e devolve um voto, para a escolha do take não sair só do
  texto. Mede enquadramento, mira, giro da câmera, nitidez e luz no rosto, acha a névoa do
  teleprompter, e monta uma tira de quadros para a expressão ser julgada olhando. Use quando
  pedirem "olha a cara dela nos takes", "qual take tem a melhor expressão", "esse take está
  desfocado?", "a câmera está torta?", nos vídeos da Diamantes (o guia manda escolher pela
  expressão) e sempre que a decupagem tiver mais de um take da mesma fala.
---

# Olheiro de rosto

O guia da Diamantes manda escolher o take **também pela expressão do rosto**. Está escrito desde
sempre e na prática ninguém olha quadro a quadro de todos os takes — não dá, junto com o resto do
trabalho. Esta skill faz só isso, então consegue.

Responda em português simples, sem termos técnicos.

## As duas regras que mandam aqui

1. **Você vota, não decide.** Quando o rosto e o texto discordarem, **o texto ganha** (decisão do
   Pedro, 28/11/2026). O rosto entra no relatório. Em cliente nenhum isso muda.
2. **Expressão não sai de número.** O script mede geometria, foco e luz. Para dizer se o olhar está
   presente, se o sorriso ficou forçado, se ela piscou na palavra importante, **abra as tiras de
   quadros e olhe**.

Você não abre o Premiere e não mexe em corte nenhum.

## Rodar

```
python -P <skills>/olheiro-de-rosto/scripts/rostos.py <work> --videos "<pasta dos brutos>"
```

Entrada: `<work>/candidatos.json` com os takes a comparar —

```json
[{"fala": "abertura", "takes": [{"file": "TOFO9199", "start": 12.3, "end": 18.0},
                                {"file": "TOFO9200", "start": 4.1,  "end": 9.8}]}]
```

Sem esse arquivo, ele mede os trechos do `selection.json` (os já escolhidos). Se o nome do arquivo
não casar com o bruto, escreva `<work>/videos.json`: `{"TOFO9199": "D:\\Jobs\\...\\TOFO9199.MP4"}`.

Sai: `<work>/rostos.json` e as tiras em `<work>/rostos/`.

## O que cada número quer dizer

| Medida | Lê assim |
|---|---|
| `quadros_com_rosto` | **0 de 3 é a pista mais importante.** Na Maria Clara a narração é gravada com a câmera ligada e virada para o chão: o "take com ela falando" pode ser só áudio, e precisa de imagem de apoio |
| `altura_rosto_pct` | o tamanho do rosto na tela. Muda entre takes = enquadramento mudou; conte isso a quem vai montar |
| `centro_x_pct`, `centro_y_pct` | onde o rosto está. Serve de mira para os zooms da `/zooms-premiere` (a regra é o rosto ficar parado na tela) |
| `inclinacao_graus` | a linha dos olhos. **Mesmo valor pequeno em todos os quadros e todos os takes = a câmera está girada, não a pessoa.** O guia da Diamantes fala em ~2° |
| `nitidez` | variância do laplaciano no recorte do rosto. Só vale comparada **entre takes do mesmo vídeo**: o que despenca está fora de foco |
| `luz_rosto` | brilho médio do rosto, 0 a 255. Diferença grande entre takes vira trabalho para o `/balance-de-cor` |
| `nevoa_baixo` | a faixa de baixo contra o meio. `razao` bem abaixo de 1 com `piso_subiu` alto é a **névoa do teleprompter** (os 15% de baixo, no guia da Diamantes) |

## O voto

Para cada fala, uma linha por take, nesta forma:

> `abertura · TOFO9200 4.1` — rosto em 3/3, enquadramento igual ao do 9199, foco bom, olhar
> presente no final da frase. **Voto: este**, se o texto permitir.

Nunca dê nota ("8 de 10"). Quando comparar dois takes, **compare os dois de uma vez e nas duas
ordens** (A contra B e B contra A); só diga que um ganhou se ele vencer das duas vezes. Se cada
ordem der um vencedor diferente, escreva "empate, decide o Pedro".

Termine com uma linha para quem vai montar: o que o rosto pediria, e o que muda se o texto mandar
o contrário.

## Por cliente

- **Diamantes:** é aqui que esta skill mais vale. Expressão, olhar, névoa do teleprompter e o giro
  da câmera. Lembre que frase fora do roteiro sai, por mais bonita que esteja a cara.
- **Riomar (Ivens):** muitos takes da mesma fala. Olhe se o enquadramento mudou entre eles, porque
  isso aparece na emenda.
- **Maria Clara:** loja e shopping. Gente passando na frente, e a narração que é só áudio (câmera
  no chão). `quadros_com_rosto` igual a 0 é informação, não erro.
- **Novais:** calmo e documental; enquadramento e foco bastam.

## Limites desta versão

- As contas foram testadas com valores conhecidos (0°, 2°, 10° de inclinação; névoa simulada
  acusada com razão 0,29) e o caminho inteiro rodou num vídeo sintético: quadros extraídos, tiras
  montadas, arquivo sem vídeo avisado, erro claro quando falta o `candidatos.json`.
- **A detecção do rosto não foi testada em rosto de verdade.** No primeiro uso, abra as tiras e
  confira se a caixa verde caiu no rosto antes de confiar nos números.
- Sem o modelo YuNet (o `instalar.sh` baixa, 232 KB, MIT), ele avisa e segue medindo luz, nitidez
  e névoa — só não mede rosto.
- Três quadros por take é o padrão. Em take longo, use `--quadros 5`.
- Aprendeu algo num vídeo? Anote aqui, no repositório `pedrotofo/estudio-video`, e peça ao Pedro
  para aprovar.
