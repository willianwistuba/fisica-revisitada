# Pré-registro E61: o regime de Dandekar et al. (escrito em 6 nov. 2026, 04h15, antes da rodada completa)

## Pergunta principal
No regime L ≥ L0 estudado por Dandekar et al. (2026), a teoria de fluxo com a absortividade medida por sentido explica as duas discrepâncias que a aproximação cega à emissividade deixou: as frações de escape de cada corpo e a razão entre pares finais prógrados e retrógrados?

## Desenho
- Conjuntos e rotação de Dandekar et al. (Tabela 1): 10-15-20 com L/L0 = 712,45/674,20 = 1,0567 e 5-15-25 com L/L0 = 833,04/811,68 = 1,0263 (L0 do par mais pesado).
- Quedas livres do repouso com rotação rígida (mesmo gerador da FR-TC-16): 12.000 por conjunto; sementes 500.000.000 + 1.000.000 · iconj + i.
- Absortividade dos 3 canais de cada conjunto nos dois sentidos, grade principal 11 × 12 e borda 11 × 7, 200 corridas por célula; sementes com deslocamento de 5 · 10¹¹.
- Critério de caos: k = 3 e 4 embaralhamentos (absorção até a primeira excursão; emissão no último episódio).
- Rodada de teste de custo (bench_dandekar.py, 600 quedas livres e 960 corridas de absortividade por conjunto, sementes diferentes) não entra em nenhum teste.

## Família 1: previsão contra as nossas quedas livres (Holm sobre 8, α = 0,05)
- Fração prógrada medida contra prevista: 2 conjuntos × 2 k. Teste exato: p bicaudal da contagem de pares retrógrados sob uma binomial com probabilidade sorteada da distribuição bootstrap da previsão (500 reamostragens da absortividade).
- Frações de escape por corpo (χ², 2 graus de liberdade): 2 conjuntos × 2 k.

## Família 2: previsão contra os números publicados por Dandekar et al. (Holm sobre 8, α = 0,05)
- Fração prógrada publicada (razão 2,08 e 144, Tabela B.3) contra a prevista: 2 conjuntos × 2 k. z com a variância bootstrap da previsão mais a binomial deles, com N = fração do corte ergódico × 10⁶ (13% e 6%, Tabela B.1).
- Fração de escape do corpo mais leve publicada (Tabela B.1, P(2d)) contra a prevista: 2 conjuntos × 2 k, com o erro-padrão publicado.
- Ressalva fixada agora: o corte ergódico deles é por tempo (τ_D ≥ 80 anos e τ_gap ≥ 10 anos), e a condição inicial é diferente. Se a teoria valer, o desfecho caótico depende só das massas, de E e de L, e as duas comparações devem passar; uma reprovação só na família 2 indicaria diferença de critério ou de ensemble, não da teoria.

## Leitura
- "A absortividade explica as discrepâncias no regime deles" se as famílias 1 e 2 passarem.
- Se a família 1 passar e a 2 não, a explicação vale para o nosso ensemble, e a diferença com os números deles fica em aberto.
- Se a família 1 reprovar, a absortividade medida não basta no regime L ≥ L0 (compatível com a mistura incompleta suspeitada por eles).

## Exploratório
- Formato da excentricidade final (KS, como na FR-TC-16); previsão cega à emissividade (Kol 2D) para comparação.
