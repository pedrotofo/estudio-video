---
name: revisor-final
description: >-
  Revisa um vídeo exportado com olhos frescos, antes de entregar ou subir: mede formato (codec,
  tamanho, fps, pixel format, faixa de cor, áudio), mede volume em LUFS e pico, desenha a área
  segura do vertical numa tira de quadros e escreve o laudo. Mede e conta — não mexe no áudio e não
  reprova entrega. Use quando pedirem "revisa antes de subir", "está pronto para o Instagram?",
  "confere esse export", "o volume está certo?", ou ao fim de qualquer render.
---

# Revisor final

O último par de olhos antes do vídeo sair. Ele existe porque erro de entrega é o mais caro de
todos: já foi exportado, já foi mandado, e volta.

Responda em português simples, sem termos técnicos.

## As duas regras

1. **Mede e conta.** Não encosta no áudio — o Pedro é quem limpa e ajusta (regra dele, 28/11/2026).
   Não reexporta, não corrige, não "dá um jeitinho".
2. **Não reprova entrega.** Escreve o laudo; quem decide subir ou não é o Pedro. Nem o pior aviso
   trava o trabalho sozinho.

## Rodar

```
python -P <skills>/revisor-final/scripts/revisar.py "<arquivo.mp4>" --saida <pasta>
```

Sai `revisao.json` e `tira-revisao.jpg`.

## O que ele mede, e o que cada coisa quer dizer

| Medida | Lê assim |
|---|---|
| `codec` | `h264` para rede. `hevc` (gravação de celular) sobe estranho ou é recodificado |
| `largura x altura` | vertical de verdade é **1080×1920** |
| `pix_fmt` | `yuv420p`. Outro formato algumas redes recusam |
| `faixa_cor` | `tv` (limitada). `pc` (cheia) **lava a imagem** depois do upload |
| `primarias` | `bt709` |
| `audio` | **sem faixa de áudio, as redes recusam ou recodificam.** Vídeo mudo leva faixa muda |
| `lufs` | alvo **−14**. Diga quantos dB faltam; não mexa |
| `pico_dbfs` | acima de −1 dB pode distorcer na rede |

## A área segura

A tira vem com um retângulo amarelo. No vertical ele é a regra da `/ilustrar-fala`: **100 px nas
laterais, 180 px em cima e 380 px embaixo**, em 1080×1920 (proporcional em outro tamanho). Em
horizontal, 5% de margem.

**Olhe a tira.** O script desenha; quem diz o que encosta é você. O que fica fora do retângulo no
vertical some atrás dos botões do Instagram e do TikTok: legenda, número, logo, o nome de quem
fala. Fundo e imagem podem (e devem) sangrar até a borda — a área segura é para o que precisa ser
lido.

## O laudo

1. **Uma linha de veredito:** pronto para subir / conserte antes / olhe isto antes de decidir.
2. **Formato:** só o que está fora do esperado, com o que fazer.
3. **Volume:** a medida e quantos dB faltam para −14.
4. **Área segura:** o que encosta ou sai, com o tempo aproximado.
5. **O que eu não consigo ver:** sempre escreva esta parte (sincronia fina, erro de português na
   legenda, se o take é o melhor — nada disso sai de medida).

Nunca dê nota. Se estiver comparando dois exports, compare os dois **nas duas ordens** e só declare
um vencedor se ele ganhar das duas vezes; senão, "empate, decide o Pedro".

## Limites desta versão

- Testado em dois arquivos feitos para isso: um vertical correto (1080×1920, h264, yuv420p, faixa
  `tv`, com áudio) passou sem aviso de formato, e um errado (720×1280, `yuv444p`, faixa `pc`, sem
  áudio) teve os quatro problemas acusados. A área segura saiu 100/180/380, como a regra manda.
- Ele mede o **arquivo**, não a timeline. Se o problema está no projeto, o laudo não alcança.
- Vídeo mudo mede por volta de −70 LUFS e o aviso de volume aparece: é esperado, não é erro.
- Aprendeu algo num vídeo? Anote aqui, no repositório `pedrotofo/estudio-video`, e peça ao Pedro
  para aprovar.
