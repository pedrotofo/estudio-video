# Como coloristas experientes fazem o balance e o match de cena

Resumo próprio, com base no que é ensinado em livros e materiais públicos de coloristas (lista no fim). Onde não deu para conferir o detalhe de um autor, a ideia aparece como prática geral do ofício, e não como citação dele.

## 1. Ordem das operações
- **Primeiro luz, depois cor.** O livro do Alexis Van Hurkman (Color Correction Handbook) organiza a correção primária assim: contraste e exposição antes, cor depois, e só então o casamento entre planos. O guia de fluxo da Frame.io segue a mesma ordem: luminância, cor, saturação. O motivo é prático: mexer no contraste muda a percepção da cor, então acertar a cor antes obriga a refazer.
- **Balance no espaço da câmera (log) ou em linear de cena, antes da transformação de saída.** Em fluxo com gerenciamento de cor, o ajuste de base é feito com a imagem ainda em log, e a conversão para Rec.709 vem depois, no fim da cadeia. Em log, cada passo de exposição ocupa um espaço parecido na curva, então um único ajuste de "offset" mexe na imagem inteira de um jeito parecido com abrir ou fechar o diafragma. Esse é um ponto que o Cullen Kelly repete muito no material público dele sobre color management e sobre o controle Offset.
- **Offset e printer lights.** O printer light vem da copiagem de filme: subir ou descer luz vermelha, verde e azul em "pontos". No digital, o equivalente é o Offset (ou os printer points do Resolve). Funciona bem em log porque desloca os três canais por igual em todas as faixas. Em material que não é log de verdade nas sombras, empurrar muito pode tingir os pretos, então o ajuste deve ser moderado.

## 2. Plano herói e casamento
- Escolha um **plano de referência (herói)** por cena: tecnicamente bom (sem estouro, sem dominante forte), parecido com a maioria dos outros, de preferência com rosto e ambiente visíveis. Muitas vezes é o plano aberto.
- Acerte o herói primeiro. Depois traga os outros para ele, comparando lado a lado imagem e scopes.
- Termine uma cena antes de ir para a próxima. Diferença de cor ou exposição entre dois planos seguidos chama atenção para o corte; é isso que o casamento evita.
- Quando a cena já está uniforme, mudanças gerais vão numa camada por cima (ajuste, grupo, nó de grupo), e não plano a plano.

## 3. Scopes
- **Waveform:** onde estão pretos, meios-tons e altas. Use para igualar a exposição e o contraste entre planos, olhando a mesma região (rosto, parede, céu).
- **Parade RGB:** os três canais lado a lado. Num objeto neutro (parede branca, camiseta cinza), as três colunas devem ficar na mesma altura. Diferença só nas sombras ou só nas altas indica dominante por faixa.
- **Vectorscope:** direção e força da cor. Áreas neutras ficam no centro.
- **Linha de pele:** pele humana de qualquer tom cai perto de uma mesma diagonal entre o vermelho e o amarelo. É uma referência, não uma lei: pele sob luz de vela ou de neon pode e deve sair dela.

## 4. O que deixar quieto
- **Intenção do fotógrafo.** Um quente de pôr do sol ou um azul de noite não é erro de balance. Primeiro entender o que foi pedido, depois corrigir.
- **Silhuetas e contraluz.** Não "abrir" uma silhueta para mostrar o rosto se ela foi feita para ser escura.
- **Luz motivada.** Abajur, janela, tela de celular: a cor da fonte faz parte da cena.
- Corrigir não é neutralizar tudo. O alvo é coerência entre planos e fidelidade ao que o diretor queria.

## 5. Luz mista
- Decida qual luz é a "principal" (quase sempre a que ilumina o rosto) e equilibre por ela.
- Aceite que a outra luz fica colorida: janela azulada com interior quente é normal.
- Se a diferença incomoda, trate depois, com correção secundária (máscara ou seleção de cor), nunca forçando o primário até a pele ficar estranha.

## 6. Erros comuns
- Mexer na cor antes de acertar exposição e contraste.
- Corrigir depois da LUT de saída, onde altas e sombras já estão comprimidas e os controles reagem mal.
- Usar a LUT ou a transformação do gamut errado (por exemplo S-Gamut3.Cine num clipe S-Gamut3).
- Neutralizar cenas que eram quentes ou frias de propósito.
- Igualar planos pela média da imagem inteira, em vez de pela mesma área de interesse.
- Confiar só no olho num monitor sem calibração, ou só no scope sem olhar a imagem.
- Saturar antes de casar os planos.

## Como isso vira regra na skill
| Ideia | Regra concreta |
|---|---|
| Luz antes de cor | Calcular e aplicar exposição/contraste primeiro; o balance de cor é medido só depois disso. |
| Balance em log/linear | Toda conta de balance é feita na imagem linearizada (inversa S-Log3 → linear de cena) ou em log; a conversão para Rec.709 é sempre o último passo. |
| Offset / printer lights | Correção de dominante = ganho por canal em linear (equivale a offset em log). Limitar a ±1 stop por canal e avisar se passar. |
| Plano herói | Pedir ao usuário o herói da cena ou sugerir o plano com exposição mais próxima da média e sem dominante forte. Os outros planos são casados com ele. |
| Mesma área de interesse | Medir a mesma região (rosto ou neutro) nos dois planos, nunca a média do quadro inteiro. |
| Scopes | Relatório de cada plano com níveis de preto/cinza/alto (waveform), diferença entre canais num neutro (parade) e ângulo da pele (vectorscope). |
| Linha de pele | Usar o ângulo da pele só como alerta (fora da linha → avisar), sem forçar a correção. |
| Intenção e luz motivada | Antes de neutralizar, perguntar se a dominante é proposital. Se a cena tiver fonte de luz visível, não neutralizar por padrão. |
| Silhuetas | Não subir exposição em plano com sujeito em contraluz sem confirmação. |
| Luz mista | Balancear pela luz do rosto; o resto fica como está e é anotado como candidato a secundária. |
| Gamut certo | Ler o gamut do XML da câmera; recusar seguir se o gamut não for conhecido. |
| Camada por cima | Saída como ajuste separado e reversível por plano, mais um ajuste geral opcional da cena. |

## Fontes
Obs.: as páginas dos livros (Van Hurkman, Hullfish) e de alguns autores não abriram na pesquisa (bloqueio de acesso); as ideias atribuídas a eles aqui são as gerais e conhecidas desses trabalhos, sem citação de trechos. Ler os originais antes de detalhar regras com base neles.
- Alexis Van Hurkman, Color Correction Handbook (descrição e sumário): https://www.oreilly.com/library/view/color-correction-handbook/9780321719720/ e https://www.peachpit.com/store/color-correction-handbook-professional-techniques-for-9780321929662
- Steve Hullfish, The Art and Technique of Digital Color Correction: https://www.routledge.com/The-Art-and-Technique-of-Digital-Color-Correction/Hullfish/p/book/9780240817156
- Frame.io Workflow Guide, Primary Color Correction: https://workflow.frame.io/guide/primary-color-correction
- Mixing Light (Cullen Kelly), Flexing Fundamentals part 1, Offset Wheel: https://mixinglight.com/color-grading-tutorials/flexing-fundamentals-part-1-offset-wheel/
- Lowepost, discussão sobre printer lights para balance primário: https://lowepost.com/forums/topic/758-printer-lights-for-primary-balance/
- Autodesk Flame, Working with Printer Lights: https://help.autodesk.com/cloudhelp/2019/ENU/Flame-EffectsandToolsReference/files/GUID-A992A5B0-9106-4653-9CED-B2813EC25D90.htm
- Adobe, correção de tons de pele (linha de pele no vectorscope): https://www.adobe.com/learn/premiere-pro/web/correct-skin-tones
- Juan Melara, blog: https://juan-melara.squarespace.com/blog/necrophilia-a-love-story-short-film (consultado só como referência geral; não encontrei texto dele sobre balance ou match)
