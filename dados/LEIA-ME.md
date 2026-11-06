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
