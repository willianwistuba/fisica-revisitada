# Física Revisitada: geradores

Geradores do site https://fisica-revisitada.vercel.app e dos PDFs das notas técnicas (REVTeX). Este repositório é a fonte de verdade da identidade visual e do formato de produção. As regras completas estão no documento `INSTRUCOES-fisica-revisitada.md` do projeto.

## Conteúdo

| Caminho | O que é |
|---|---|
| `meta.py` | Constantes do site, rotas por idioma e lista `ARTS` das notas |
| `body.py` | Conversão do corpo das notas para HTML e LaTeX; figuras SVG e pgfplots |
| `site.py` | Gera o site estático inteiro em `public/` |
| `tex.py` | Gera os PDFs de uma nota nos quatro idiomas (`python3 tex.py FR-TC-NN`) |
| `estilo.css` | Folha de estilo do site |
| `i18n/*.json` | Textos de interface e metadados das notas em pt, en, de e fr |
| `src/<idioma>/aNN.html` | Corpo de cada nota |
| `codigo_src/` | Scripts publicados em /codigo/ |
| `pdf/` | PDFs publicados |
| `a10_grids.npz`, `a12_points.json`, `a13_points.json` | Dados das figuras |

## Preparar o ambiente

```sh
apt-get update && apt-get install -y texlive-publishers texlive-lang-german texlive-lang-french texlive-lang-portuguese
mkdir -p texbuild
python3 site.py              # site em public/
python3 tex.py FR-TC-13      # deve informar overfull 0 nos quatro idiomas
```

A pasta `texbuild/` precisa existir antes de rodar `site.py`. As pastas `public/` e `texbuild/` não são versionadas.

## Publicar

Deploy por relay de sandbox da Vercel no projeto `fisica-revisitada`, conforme a seção 2.2 das instruções. Depois de cada nota publicada, fazer commit e push aqui.
