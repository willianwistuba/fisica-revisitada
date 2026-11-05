# Dados brutos do regime L = 0 (notas 13 a 15)

`dados_l0.tar.xz` (extrair com `tar xJf dados_l0.tar.xz`):

- `pacote_v2/`: absortividade medida (grade principal `abs4_r20_*.csv` e borda em j `abs5_cauda_*.csv`) para os canais dos conjuntos 3-3-1, 1-2-3 e 1-1-3; quedas livres originais (`age.csv`) e réplica do 1-1-3 (`age_113_rep.csv`); resultados em JSON.
- `escada/`: escada de massas 1-1-M (M = 2; 2,5; 2,75; 3,25; 3,5; 4; 5), com quedas livres (`age_1-1-M.csv`), absortividade dos dois canais e resultados (`escada_aqui.json`, `geo_escada.json`).

Os scripts que geraram e analisaram esses arquivos estão em `codigo_src/ergo/`.
