# Fluxo do Caravela Color

Ordem fixa, como num colorista de verdade:

1. **Gerenciamento de cor**: descobrir câmera, perfil, gamut, bits e faixa. Converter para o espaço de trabalho certo antes de qualquer ajuste. Sem isso, nenhuma medida faz sentido.
2. **Correção (skill `balance`)**: exposição, balanço de branco, contraste neutro, pele no lugar, saturação natural. Escolher o take de referência (hero shot) e igualar os outros a ele.
3. **Look (skill `grade`)**: só depois da cena equilibrada. Perguntar a intenção, sugerir 3 looks com nota de viabilidade, mostrar antes/depois, aplicar o escolhido.
4. **QC**: níveis legais, pele, banding, consistência entre takes e aviso de gama do monitor.

## Princípios
- **Scopes são medidos por código** (Python + ffmpeg + numpy). A IA interpreta os números; não "lê" imagens de scope.
- **Ler antes de sobrescrever**: ver o que já está aplicado no clipe.
- **Preview antes de aplicar**: frames renderizados de antes/depois; o usuário escolhe.
- **Sempre entregar `.cube`** além dos ajustes no Premiere, para o look ser portátil.
- **Pensar na cena**, não no take isolado: hero shot + match.
- **Ser honesto sobre limites**: 8 bits, ruído, alta luz estourada não se recuperam; dizer o que mudaria na captação.
- **Perguntar câmera/perfil** a qualquer usuário, mas tentar ler metadados antes.
