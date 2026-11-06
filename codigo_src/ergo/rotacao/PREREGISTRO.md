# Pré-registro: rotação no plano (escrito em 5 nov. 2026, 20h50, antes de qualquer dado novo)

## Pergunta principal
A falha da teoria de fluxo no formato da excentricidade final do 1-1-3 (L = 0: KS 0,101 com k = 3 e 0,126 com k = 4) continua, diminui ou aumenta quando o sistema tem rotação total 0 < L ≤ L0?

## Desenho
- Conjuntos: 1-1-3 (alvo) e 1-2-3 (controle; passou em L = 0).
- Rotação: λ = L/L0 = 0,3 e 0,7, com L0 = √(k_B/(−2E)) do par mais pesado (1-1-3: par 1-3; 1-2-3: par 2-3).
- Queda livre: posições do ensemble frio, rotação rígida com L/L0 = λ exato; 12.000 corridas por conjunto e λ; até 1.000 t_cr.
- Absortividade: todos os canais do conjunto, os dois sentidos do par (s = ±1), grade principal 11 x × 12 e e borda 11 x × 7 j, 200 corridas por célula, lançamento a 20 a_B; célula sem alcance conta como A = 0.
- Previsão: P(x, e) ∝ Σ_canais Σ_s mult · (m_a m_b)³/(m_a + m_b) · x⁻² e/√(1−e²) · A_k(x, e, s; λ). O peso do fluxo não depende de L (Dandekar et al. 2026, eq. 10; conferido em fluxo_plano_L.py).
- Amostra medida: fugas finais (status 1) com nS ≥ k no último episódio, k = 3 e 4.

## Testes confirmatórios (8)
- KS da excentricidade final, formato completo, para cada conjunto × λ × k.
- Valor crítico e p por bootstrap com 500 reamostragens binomiais da absortividade (mesmo método de analise_escada.py); piso de p = 0,002.
- Correção de Holm sobre os 8 testes, α = 0,05 (95%).

## Regra de leitura (fixada agora)
- Controle: se o 1-2-3 reprovar em algum λ, a leitura do 1-1-3 nesse λ fica suspensa (o problema seria do método em L ≠ 0, não do conjunto).
- 1-1-3, com o controle passando: "a falha continua" se reprovar nos dois λ (em pelo menos um k cada); "a falha some" se passar nos dois λ e nos dois k; caso contrário, "a falha depende da rotação", descrevendo em qual λ.
- O tamanho do efeito (KS e Δe = e médio medido − previsto) é comparado com L = 0 só de forma descritiva.

## Exploratório (relatado, sem valor de confirmação)
- Teste até e ≤ 0,995; frações de escape por corpo; razão prógrado/retrógrado medida contra a prevista com A medida (a teoria cega à emissividade prevê 1); Δe por canal.

## Sementes
- Queda livre: 70.000.000 + 10.000.000 · iλ + 1.000.000 · iconj + i.
- Absortividade: as de run_absorb4.task com deslocamento 1.000.000 · (1 + 10λ) + 500.000 · (s < 0).
