# Dados brutos do regime L = 0 (notas 13 a 15)

`dados_l0.tar.xz` (extrair com `tar xJf dados_l0.tar.xz`):

- `pacote_v2/`: absortividade medida (grade principal `abs4_r20_*.csv` e borda em j `abs5_cauda_*.csv`) para os canais dos conjuntos 3-3-1, 1-2-3 e 1-1-3; quedas livres originais (`age.csv`) e réplica do 1-1-3 (`age_113_rep.csv`); resultados em JSON.
- `escada/`: escada de massas 1-1-M (M = 2; 2,5; 2,75; 3,25; 3,5; 4; 5), com quedas livres (`age_1-1-M.csv`), absortividade dos dois canais e resultados (`escada_aqui.json`, `geo_escada.json`).

Os scripts que geraram e analisaram esses arquivos estão em `codigo_src/ergo/`.

# Dados brutos do estudo de rotação no plano (E59, 5 nov. 2026)

`dados_rotacao.tar.xz` (extrair com `tar xJf dados_rotacao.tar.xz`), pasta `pacote_rot/`:

- `age_<conjunto>_lam<λ>.csv`: quedas livres com rotação rígida, 12.000 por conjunto (1-1-3, 1-2-3) e λ = L/L0 (0,3 e 0,7); coluna `sentido` = sentido do par final em relação a L.
- `abs4_r20_<canal>_lam<λ>.csv` e `abs5_cauda_<canal>_lam<λ>.csv`: absortividade dos 5 canais nos dois sentidos (coluna `s`), 200 corridas por célula.
- `resultado_rotacao.json`, `PREREGISTRO.md` e `bench.json` (custo medido).

Scripts em `codigo_src/ergo/rotacao/` (`rot.py`, `sim2r.py`, `rodar.py`, `analise_rot.py`, `fluxo_plano_L.py`, `confere_L0.py`, `checa_L.py`, `bench.py`).

# Dados brutos da confirmação prógrado/retrógrado (E60, 6 nov. 2026)

`dados_rotacao_conf.tar.xz`, pasta `pacote_conf/`: mesmo formato da E59, com sementes novas e λ = 0,1; 0,3 e 0,7 (72.000 quedas livres e 1.254.000 corridas de absortividade), mais `resultado_conf.json` e `PREREGISTRO_CONF.md`. Análise: `codigo_src/ergo/rotacao/analise_conf.py`.

# Dados brutos do regime de Dandekar et al. (E61, 6 nov. 2026)

`dados_dandekar.tar.xz`, pasta `pacote_dk/`: quedas livres com rotação rígida (12.000 por conjunto) e absortividade dos 3 canais nos dois sentidos para 10-15-20 (L/L0 = 1,0567) e 5-15-25 (L/L0 = 1,0263); `ci_<conjunto>.csv` com 12.000 corridas por conjunto na condição inicial de Dandekar et al. (exploratório); `resultado_dandekar.json`, `PREREGISTRO_DANDEKAR.md` e `bench_dandekar.json`. Scripts: `rodar_dandekar.py`, `analise_dandekar.py`, `ci_dandekar.py`, `bench_dandekar.py`.

# E65 (6 nov. 2026)

`dados_quente.tar.xz`: 12.000 corridas do 1-1-3 e 12.000 do 1-2-3 (controle) com L = 0 e velocidades sorteadas (K/|W| = 0,5), 12.000 do 1-1-3 com velocidades sorteadas e L/L0 = 0,3 (`age_1-1-3-rot_lam0.0.csv`, E65c), 12.000 com L/L0 = 0,7 (`age_1-1-3-rot07_lam0.0.csv`, E65e), `resultado_quente.json`, `resultado_quente_123.json` , `resultado_quente_rot.json` e `resultado_quente_rot07.json`. Análise por faixas: `onde_e.py`. Script `codigo_src/ergo/rotacao/quente.py`; pré-registro `PREREGISTRO_QUENTE.md`.
