# Pré-registro E63: mais três conjuntos de Dandekar et al. (escrito em 6 nov. 2026, 12h55, antes de qualquer dado novo)

## Pergunta
A teoria de fluxo com a absortividade medida por sentido, que passou no 10-15-20 e no 5-15-25 (E61), explica também a razão prógrado/retrógrado e as frações de escape nos conjuntos 8-21-21, 10-20-20 e 15-15-15 de Dandekar et al. (2026), com a rotação das condições iniciais deles?

## Desenho
- Rotação (Tabela 1 de Dandekar et al., L0 do par mais pesado): 8-21-21 com L/L0 = 956,05/921,58 = 1,0374; 10-20-20 com 888,58/847,22 = 1,0488; 15-15-15 com 577,15/526,86 = 1,0955.
- Canais distintos: 8-21-21: par 21-21 com fuga do 8, e par 8-21 com fuga de um 21 (multiplicidade 2); 10-20-20: par 20-20 com fuga do 10, e par 10-20 com fuga de um 20 (multiplicidade 2); 15-15-15: um canal (multiplicidade 3).
- Quedas livres com rotação rígida: 12.000 por conjunto; sementes 900.000.000 + 1.000.000 · iconj + i.
- Absortividade de cada canal nos dois sentidos, grade principal 11 × 12 e borda 11 × 7, 200 corridas por célula; sementes com deslocamento de 7 · 10¹¹.
- Caos: k = 3 e 4 embaralhamentos, como na E61.
- Rodado no computador do autor (rodar_tres.py), com os mesmos scripts da E61.

## Família 1: contra as nossas quedas livres (Holm sobre 10, α = 0,05)
- Fração prógrada (teste exato com mistura bootstrap, 500 reamostragens): 3 conjuntos × 2 k = 6 testes.
- Frações de escape (χ²): 8-21-21 e 10-20-20 × 2 k = 4 testes (no 15-15-15 as frações são iguais por simetria e não há teste).

## Família 2: contra os números publicados (Holm sobre 10, α = 0,05)
- Fração prógrada publicada (Tabela B.3: razões 12,35; 3,85; 0,90; N = fração do corte ergódico × 10⁶, com 9%, 13% e 12%): 6 testes.
- Fração do corpo mais leve publicada (Tabela B.1: 0,9428 ± 0,0008 e 0,8735 ± 0,0009): 4 testes.
- Mesma ressalva da E61: critério de seleção e condição inicial diferentes; reprovação só na família 2 indica diferença de critério ou de ensemble.

## Leitura
- "A absortividade explica" nos três conjuntos se a família 1 passar; a família 2 é lida como na E61.
- Exploratório: formato da excentricidade (KS); previsão cega à emissividade.
