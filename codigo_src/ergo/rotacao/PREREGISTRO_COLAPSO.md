# Pré-registro E64: uma curva de rotação por canal (6 nov. 2026, 14h25, antes da análise)
Hipótese: logit A_3(x,e,s;λ) = logit A_0(x,e) + g_canal(ρ), com ρ = L_F/L_B e g(−1) = 0 (L = 0). Uma curva por canal, igual para todos os x e e.
Ajuste: g linear por partes em ρ (8 nós nos quantis), máxima verossimilhança binomial, só com a rodada 1 (E59, λ = 0,3 e 0,7). A_0 das tabelas de L = 0 (FR-TC-15).
Teste (rodada 2, E60, sementes independentes):
- C1: em λ = 0,3 e 0,7, desvio binomial do modelo ≤ desvio da tabela crua da rodada 1 (o modelo comprime sem perder).
- C2: em λ = 0,1 (sem dados de treino), desvio do modelo < desvio de "sem efeito de rotação" (A = A_0), e fração prógrada prevista compatível com a medida nas quedas livres (1-1-3 e 1-2-3, k = 3; teste binomial exato, Holm sobre 2, 95%).
Passa se C1 e C2 passarem.
