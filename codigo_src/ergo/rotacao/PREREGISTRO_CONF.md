# Pré-registro E60: confirmação da razão prógrado/retrógrado (escrito em 5 nov. 2026, 23h55, antes de qualquer dado novo)

## Pergunta principal
A fração de fugas com par final prógrado (girando no mesmo sentido da rotação total), prevista pela teoria de fluxo com a absortividade medida por sentido, bate com a fração medida?

Origem: na E59 (exploratório) a previsão acertou nos 8 casos, com p de 0,51 a 0,94. A teoria sem absortividade prevê fração 1/2 (razão 1); Dandekar et al. (2026) mediram razões de 0,90 a 144 com L ≥ L0.

## Dados novos e independentes
- Mesmo desenho da E59 (PREREGISTRO.md): 1-1-3 e 1-2-3; λ = L/L0 = 0,3 e 0,7 (L0 do par mais pesado); 12.000 quedas livres por conjunto e λ; absortividade dos 5 canais nos dois sentidos, grade principal mais borda, 200 corridas por célula; k = 3 e 4.
- Sementes: quedas livres 200.000.000 + 10.000.000 · iλ + 1.000.000 · iconj + i (iλ = 0, 1, 2 para λ = 0,3; 0,7; 0,1); absortividade com o deslocamento da E59 mais 100.000.000.000. Nenhuma coincide com a E59 nem com as rodadas de L = 0.
- Comando: `python rodar.py <pasta> 2 0.3,0.7,0.1 200000000 100000000000`.

## Família principal (8 testes)
- Para cada conjunto × λ (0,3 e 0,7) × k: fração prógrada medida contra prevista, teste z bicaudal com variância binomial da amostra mais variância da previsão (500 reamostragens binomiais da absortividade).
- Holm sobre os 8, α = 0,05.
- Leitura: "a absortividade explica a assimetria" se os 8 passarem; se algum reprovar, descrever onde e com que sinal.
- Poder estimado com os erros da E59: com cerca de 1.100 fugas, desvios de cerca de 5 pontos percentuais na fração prógrada são detectados com 80% de chance.

## Família secundária (2 testes)
- KS do formato da excentricidade do 1-1-3 com λ = 0,7, k = 3 e 4 (método da E59), Holm sobre os 2. Pergunta: a reprovação marginal da E59 (k = 3, p = 0,006) se repete?

## Exploratório (sem valor de confirmação)
- λ = 0,1 nos dois conjuntos: formato, escapes e fração prógrada.
- Formato do 1-2-3 e do 1-1-3 com λ = 0,3, escapes por corpo, Δe.
