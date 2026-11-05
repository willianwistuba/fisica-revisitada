# Física Revisitada: instruções permanentes do projeto

> **Fonte de verdade.** Este documento foi escrito a partir dos geradores originais que produziram o site e os PDFs (`meta.py`, `body.py`, `tex.py`, `site.py`, `estilo.css`, `i18n/*.json`), e não de uma reconstrução. Ele prevalece sobre a SPEC quando houver conflito (a SPEC tem trechos antigos de identidade visual).
>
> **Regra zero.** Nunca reescreva os geradores de memória. Comece sempre pelo repositório privado **https://github.com/willianwistuba/fisica-revisitada** (branch `main`), que é a fonte de verdade dos geradores. O `fisica-revisitada-geradores.zip` do projeto é só cópia de reserva. Se o repositório não estiver acessível na sessão, peça ao autor para conectá-lo (ou use o zip) antes de produzir qualquer nota, página ou PDF.
>
> **Verificação de 4 de novembro de 2026.** O pacote foi testado numa sessão limpa: `site.py` reproduziu a página inicial e a página da FR-TC-13 idênticas, byte a byte, ao site publicado, e `tex.py FR-TC-13` gerou os quatro PDFs com `overfull 0` e texto idêntico ao PDF publicado. O `estilo.css` do pacote é idêntico ao publicado.

---

## 1. O projeto em uma frase

Série de notas técnicas em física (atualmente sobre o problema dos três corpos), publicadas em <https://fisica-revisitada.vercel.app> em quatro idiomas (pt, en, de, fr), cada nota com página HTML e PDF em formato de artigo científico (REVTeX), código aberto e depósito no Zenodo.

## 2. Conexões e infraestrutura

| Item | Valor |
|---|---|
| Site | `https://fisica-revisitada.vercel.app` (constante `SITE` em `meta.py`) |
| Repositório dos geradores | `https://github.com/willianwistuba/fisica-revisitada` (privado, branch `main`; primeiro commit `b0c4043`, estado da FR-TC-13) |
| Vercel: time | `willianwistubas-projects` |
| Vercel: projeto | `fisica-revisitada` (id `prj_I9zCrbrxL7azUWYENzdkvoxBYSg3`) |
| SPEC (Claude Docs) | https://claude.ai/artifact/Tv6uowaJjGUr3KiUrPpMW3 (projeto `d9f7aadd-e302-447b-93ec-401ec91b46fc`, nó `745fc4e7-8e85`) |
| Zenodo | conta do autor; registros das notas 1 a 13 já publicados; FR-TC-14 e FR-TC-15 publicadas no site em 5 nov. 2026, ainda sem depósito (FR-TC-13 v1: 10.5281/zenodo.23964751) |
| ORCID | 0009-0008-2875-6607 |
| Endereço antigo | `caderno-tres-corpos.vercel.app` redireciona (308) para o novo, mantendo os caminhos |

### 2.1 Preparar o ambiente (sessão nova)

1. Conectar o repositório à sessão e cloná-lo (`git clone --depth 1 https://github.com/willianwistuba/fisica-revisitada`); os geradores ficam na raiz. Na falta dele, extrair o zip do projeto (os geradores ficam em `fr/`).
2. Criar a pasta `texbuild/` na pasta dos geradores antes de rodar qualquer gerador (`mkdir -p texbuild`). Sem ela, `site.py` falha com `FileNotFoundError: texbuild/a10_pt.png`.
3. Instalar o que falta no LaTeX: `apt-get update && apt-get install -y texlive-publishers texlive-lang-german texlive-lang-french texlive-lang-portuguese` (traz `revtex4-2.cls` e os arquivos do babel para `ngerman`, `french` e `brazilian`). Sem eles, `tex.py` para com "Unknown option 'ngerman'" ou sem a classe REVTeX.
4. Teste de sanidade antes de mexer em qualquer coisa: `python3 site.py` e comparar `public/index.html` com a página inicial publicada (devem ser idênticos); `python3 tex.py FR-TC-13` deve informar `overfull 0` nos quatro idiomas.

### 2.2 Como publicar (deploy por relay)

O site é estático (pasta `public/`). O método que funciona é o relay por sandbox da Vercel:

1. Gerar tudo: `python tex.py FR-TC-NN` (PDFs dos 4 idiomas da nota) e `python site.py` (site inteiro em `public/`).
2. Empacotar: `(cd public && tar czf ../site.tgz .)` e anotar o `sha1sum`.
3. Criar sandbox: `create_sandboxes_v4` com `name: fr-relay-NN`, `projectId` acima, `ports: [3000]`, `persistent: false`, `timeout: 1800000`.
4. Subir um servidor Node de PUT/GET no caminho secreto `/07e369a56936816fb5878d89/site.tgz` (porta 3000).
5. `curl -X PUT --data-binary @site.tgz <url>/07e369a56936816fb5878d89/site.tgz` e conferir que o sha1 baixado bate.
6. `create_deployment`: `name: fisica-revisitada`, `target: production`, `files: [README.md]`, `projectSettings`: `framework: null`, `installCommand: "true"`, `outputDirectory: "public"`, `buildCommand: "mkdir -p public && curl -sSf <url> -o /tmp/s.tgz && tar xzf /tmp/s.tgz -C public"`; `forceNew: 1`, `skipAutoDetectionConfirmation: 1`.
7. Esperar cerca de 45 s e conferir HTTP 200 nas 4 páginas da nota e nos 4 PDFs.
8. **Sempre** encerrar o sandbox (`stop_session`).
9. Fazer commit e push no repositório (geradores, fontes, i18n, scripts e PDFs da nova nota). As pastas `public/` e `texbuild/` não são versionadas. Opcionalmente, atualizar também o zip de reserva no projeto.

#### 2.2.1 Detalhes que já funcionaram (5 nov. 2026, deploy dpl_ESLJne7sriYcKfR9DRR3i6MXwS1L)

- O sandbox não precisa de rede de saída especial: o servidor só recebe o PUT da sessão de trabalho e entrega o GET para o build da Vercel.
- Servidor `srv.js` (copiar exatamente):

```js
const http=require('http'),fs=require('fs');const P='/07e369a56936816fb5878d89/site.tgz',F='/tmp/site.tgz';
http.createServer((q,r)=>{if(q.url!==P){r.writeHead(404);return r.end();}
if(q.method==='PUT'){const w=fs.createWriteStream(F);q.pipe(w);w.on('finish',()=>{r.writeHead(200);r.end('ok')});}
else if(q.method==='GET'){if(!fs.existsSync(F)){r.writeHead(404);return r.end();}r.writeHead(200,{'Content-Type':'application/gzip'});fs.createReadStream(F).pipe(r);}
else{r.writeHead(405);r.end();}}).listen(3000);
```

- Passos com as ferramentas MCP da Vercel (time `willianwistubas-projects`):
  1. `create_sandboxes_v4` com `{"name":"fr-relay-NN","projectId":"prj_I9zCrbrxL7azUWYENzdkvoxBYSg3","ports":[3000],"persistent":false,"timeout":1800000}`. Guardar o `currentSessionId` (sbx_...) e a URL da rota da porta 3000 (`https://sb-....vercel.run`). Usar um NN novo a cada deploy (o último foi fr-relay-30).
  2. Empacotar o `srv.js` num tar.gz, codificar em base64 (`tar czf srv.tgz srv.js && base64 -w0 srv.tgz`) e enviar com `write_session_files` (`xCwd: "/tmp"`).
  3. `run_session_command` com `{"command":"node","args":["/tmp/srv.js"]}` (sem esperar o fim).
  4. Na sessão de trabalho: `curl -sS -X PUT --data-binary @/tmp/site.tgz <url>/07e369a56936816fb5878d89/site.tgz` (resposta `ok`) e `curl -sS <url>/07e369a56936816fb5878d89/site.tgz | sha1sum`, que deve bater com o `sha1sum` local.
  5. `create_deployment` com `forceNew: "1"`, `skipAutoDetectionConfirmation: "1"` e `requestBody`: `{"name":"fisica-revisitada","target":"production","files":[{"file":"README.md","data":"Física Revisitada","encoding":"utf-8"}],"projectSettings":{"framework":null,"installCommand":"true","outputDirectory":"public","buildCommand":"mkdir -p public && curl -sSf <url>/07e369a56936816fb5878d89/site.tgz -o /tmp/s.tgz && tar xzf /tmp/s.tgz -C public"}}`.
  6. Esperar cerca de 40 a 50 s e conferir HTTP 200 nas 4 páginas e nos 4 PDFs da nota (seção 2.3), mais um arquivo novo da página de código. Conferir também que o sha1 do PDF pt publicado bate com o local.
  7. `stop_session` no sandbox.
- O pacote do site tem cerca de 9 MB; o upload leva poucos segundos.

**Atenção:** nesse método, um `vercel.json` dentro do pacote é ignorado (por isso o redirecionamento `/sobre` → `/metodo/` não está ativo). Arquivos estáticos já saem com `Access-Control-Allow-Origin: *`.

### 2.3 Estrutura de URLs (`meta.py`: `ROUTES`, `PREFIX`)

| | pt (sem prefixo) | en (`/en`) | de (`/de`) | fr (`/fr`) |
|---|---|---|---|---|
| nota | `/artigos/<slug>/` | `/en/articles/<slug>/` | `/de/artikel/<slug>/` | `/fr/articles/<slug>/` |
| lista | `/notas/` | `/en/notes/` | `/de/notizen/` | `/fr/notes/` |
| método | `/metodo/` | `/en/method/` | `/de/methode/` | `/fr/methode/` |
| código | `/codigo/` | `/en/code/` | `/de/code/` | `/fr/code/` |
| PDF | `/pdf/<slug>.pdf` | `/pdf/en/<slug>.pdf` | `/pdf/de/<slug>.pdf` | `/pdf/fr/<slug>.pdf` |

Outros arquivos gerados: `sitemap.xml` (com `hreflang`), `robots.txt`, `rss.xml` por idioma e `zenodo.json` (índice das notas para o script de envio ao Zenodo; gerado no fim de `site.py`).

### 2.4 Git (commit e push)

- Identidade dos commits: `git -c user.name=Claude -c user.email=noreply@anthropic.com commit`. A mensagem termina com as linhas de atribuição que a sessão indicar (Co-Authored-By e Claude-Session).
- Sequência: `git add` só do que mudou (geradores, `src/`, `i18n/`, `pdf/`, `codigo_src/`, `dados/`), commit, `git fetch origin main && git rebase origin/main && git push origin HEAD:main`.
- Para ter permissão de push, o repositório precisa ser anexado à sessão com acesso de escrita. O classificador da plataforma pode recusar o push até o autor autorizar explicitamente no chat ("pode fazer o push").
- `public/` e `texbuild/` não são versionados.

## 3. Identidade visual do site (valores do `estilo.css` publicado)

### 3.1 Cores

| Variável | Claro | Escuro (`prefers-color-scheme: dark`) |
|---|---|---|
| `--bg` | `#FFFFFF` | `#0C0E12` |
| `--soft` | `#F5F6F8` | `#13161B` |
| `--panel` | `#FFFFFF` | `#13161B` |
| `--ink` (tinta) | `#0F1217` | `#F2F3F5` |
| `--muted` | `#5A5F69` | `#A0A5AF` |
| `--line` | `#E3E5E9` | `#262A31` |
| `--accent` (azul) | `#1D3FD8` | `#7090FF` |
| `--hot` (laranja) | `#E8480C` | `#FF6A33` |
| `--warnbg` | `#FFF4EE` | `#1C1410` |

Sem tons pastéis nem degradês. Identidade moderna, conceitual e ousada: fundo neutro, tinta quase preta, um azul forte e um laranja de destaque.

### 3.2 Tipografia (Google Fonts)

| Papel | Fonte | Pesos |
|---|---|---|
| Títulos (`--fd`) | Inter Tight | 600, 700, 800 |
| Texto de interface (`--fb`) | Inter | 400, 500, 600 |
| Rótulos, códigos (`--fm`) | JetBrains Mono | 500, 600 |
| Corpo dos artigos (`--fs`) | Source Serif 4 | 400, 600, 700 e itálico 400 |

Linha de carregamento (`site.py`): `https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Inter+Tight:wght@600;700;800&family=JetBrains+Mono:wght@500;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&display=swap`

### 3.3 Elementos que não podem sumir

- Logotipo em texto "Física **Revisitada**", com "Revisitada" em azul.
- Cabeçalho do artigo ("masthead"): "Física Revisitada", subtítulo "Notas técnicas em física" e o código `FR-TC-NN (2026)`.
- Faixa laranja curta (`.hot`) no topo dos cabeçalhos de página.
- Rótulos em fonte mono (`.eyebrow`, tipo do artigo).
- Destaque azul nos links e no título.
- Linha de autoria com o selo verde do ORCID.
- Botões "Baixar PDF · NN KB" e "Como citar"; seletor de idiomas (PT, EN, DE, FR).
- Figuras em SVG desenhadas pelos próprios geradores, com as cores das variáveis (`var(--accent)`, `var(--hot)`, `var(--ink)`) para funcionar nos modos claro e escuro.

## 4. Formato dos PDFs (`tex.py`)

- Classe: `revtex4-2` com `[aps,pre,twocolumn,nofootinbib,floatfix,preprintnumbers,10pt]`, papel carta, compilação `pdflatex` duas vezes.
- Pacotes: `fontenc T1`, `inputenc utf8`, `textcomp`, `babel` (idioma principal mais os outros três: `brazilian`, `english`, `ngerman`, `french`), `mathptmx`, `amsmath`, `amssymb`, `microtype`, `graphicx`, `xcolor`, `pgfplots` (compat 1.16, `\usetikzlibrary{babel}`), `hyperref`, `orcidlink`.
- Cores no PDF: `fraccent #1D3FD8` (links), `frhot #E8480C`, `frink #111318`.
- Cabeçalho: `\preprint{FÍSICA REVISITADA · FR-TC-NN}`, `\preprint{<tipo>}`, título, autor com `\orcidlink`, afiliação.
- Bloco do resumo, nesta ordem: resumo; palavras-chave; ORCID; **Contato (a partir da FR-TC-13)**; data de publicação e versão; série com o link da nota.
- Corpo: seções Introdução, Método, Resultados (com subseções), Discussão, Conclusões. Tabelas com legenda em cima; figuras em pgfplots (ou PNG em `\includegraphics` quando for mapa), legenda embaixo.
- Seções finais fixas: nota de transparência (`ui.backmatter_transparency_*`), disponibilidade de dados e código, conflito de interesses (`ui.backmatter_coi_*`), como citar, referências (`\bibitem` no padrão APS com DOI ou URL).
- Decimais: vírgula em pt, de e fr (`{,}` no modo matemático); ponto em en.
- Controle de qualidade antes do deploy: `overfull 0` em todos os idiomas (o `tex.py` informa a contagem). Tabela larga demais ou equação larga demais deve ser quebrada; é proibido publicar com overfull. Conferir visualmente a primeira e a última página de cada PDF (`pdftoppm`).
- Pendência conhecida: o campo de palavras-chave dos metadados do PDF sai vazio (falta `pdfkeywords` no `\hypersetup`).

## 5. Autoria e textos fixos

- Nome: **Willian Wistuba Melo da Cunha**; ORCID 0009-0008-2875-6607.
- Afiliação no PDF: só "Entusiasta e autodidata em física" (traduzida em cada idioma). No site: "Entusiasta de física".
- E-mail de contato `profwistuba01@gmail.com`: **somente da FR-TC-13 em diante** (PDF, no bloco do resumo; site, na linha de autoria). Notas 1 a 12 ficam sem.
- "Advogado" aparece apenas na nota de transparência e na página Método. Nunca mencionar OSINT, professor ou auditor; nunca escrever "pesquisador independente" como afiliação.
- Publicação apenas no Zenodo e na RNAAS, sem revisão por pares. O token do Zenodo nunca é colado no chat.
- Estilo de escrita: PT-BR; nunca usar travessões no meio de frases; toda frase interrogativa termina com "?"; linguagem simples com exemplos nas explicações ao autor; linguagem técnica nas notas, sem reproduzir a conversa.

## 6. Produção de uma nota nova (passo a passo)

1. Escrever `src/pt/aNN.html` (h2, h3, p, ul, div.eq, div.tblwrap com p.cap e table, figure data-fig="ANN" com figcaption, citações `<cite>n</cite>`). Um "<" colado a letra dentro de fórmulas (por exemplo i<j) deve ser escrito `&lt;`, senão quebra o HTML.
2. Acrescentar a entrada em `meta.py` (`slug`, `src`, `part`, `code`, `refs`) no fim da lista `ARTS`.
3. Em `i18n/pt.json`: `articles["FR-TC-NN"]` (title, short, type, abstract, kw com 6 itens), `fig["ANN"]`, atualizar `series.lead` ("Treze notas" etc.), `ui.series_order_text`, `code_page.lead` e `code_page.files`. Desde a FR-TC-14, cada nota nova leva data e versão próprias: em `meta.py`, `date_iso` (ex.: `2026-11-05`) e `version_num` (ex.: `'1'`); em cada `i18n/*.json`, dentro de `articles["FR-TC-NN"]`, `date_long` e `version_note`. Sem esses campos, a nota herda a data e a versão globais (`ui.date_long`, versão 2), como as notas 1 a 13.
4. Se houver figura: funções `svg_aNN` e `tex_fig_aNN` em `body.py`, registradas em `SVGFIG` e `TEXFIG`.
5. Copiar os scripts usados para `codigo_src/ergo/`.
6. Gerar o PDF em pt e conferir `overfull 0` e o aspecto visual (pdftoppm).
7. Traduzir para en, de e fr (um agente por idioma), mantendo a estrutura HTML idêntica, as citações e as equações. Termos fixos na seção 8.
8. `python tex.py FR-TC-NN`, `python site.py`, deploy (seção 2.2), conferência das 8 URLs.
9. Registrar na SPEC: entrada do experimento e entrada de publicação (com o id do deploy).
10. Commit e push no repositório, com mensagem que cite o código da nota (ex.: "Publica FR-TC-14").

### 6.0 Detalhes de edição que evitam retrabalho

- O resumo de cada nota fica em `i18n/<idioma>.json`, em `articles["FR-TC-NN"]["abstract"]`, e não no HTML.
- Tabelas e figuras: a numeração no texto ("Tabela IV", "Table IV", "Tabelle IV", "Tableau IV") é escrita à mão; a legenda é numerada pelo gerador na ordem em que aparece.
- Números negativos em tabelas e no texto: `\(-0{,}030\)` em pt, de e fr e `\(-0.030\)` em en (o sinal de menos matemático); positivos com `+0,004` em texto simples.
- Em fr, usar o espaço inseparável U+00A0 (e não um espaço comum) nos milhares (`12 000`), antes de `:` `;` `%` `?` e dentro das aspas `« »`. Ao editar por script, substituir esses espaços explicitamente.
- A página de código aceita subpastas: a chave em `code_page.files` é o caminho relativo a `codigo_src/` (ex.: `ergo/escada/run_age.py`), e o arquivo precisa existir nesse caminho. A contagem de scripts na página inicial sai automaticamente do número de entradas.
- Depois de mudar o texto, rodar `python3 tex.py FR-TC-NN` (gera os 4 PDFs e informa overfull) e `python3 site.py` (gera o site inteiro). Conferir com `pdftoppm -r 60` a página onde está a tabela nova em pelo menos pt e de (o alemão é o idioma mais longo).
- Traduções: manter a estrutura HTML idêntica nos 4 idiomas, com as mesmas tabelas, citações e equações; aplicar as convenções numéricas da seção 8.

### 6.1 Correções

**Nota ainda não depositada no Zenodo:** se ela só está no site, a correção substitui o texto direto, sem nota de revisão e sem mudar `version_num` (decisão do autor, 5 nov. 2026; aplicada à FR-TC-15). A data da nota continua a da publicação.

**Nota já depositada no Zenodo:**

Correção de nota já publicada: nova versão, nunca apagar. No site, parágrafo "**Nota de revisão (versão N, data).**" no topo do corpo, explicando o que mudou e o que não mudou, e a frase "Versão N: ..." no fim do resumo. Links dos PDFs com `?v=N` para furar o cache. No Zenodo, botão "Nova versão" do script (cria nova versão do mesmo registro, com novo DOI de versão).

## 7. Rigor científico (regras do autor)

- **95% de confiança** para todo achado publicado; o tamanho da amostra é dimensionado antes de rodar.
  - Proporções: intervalo de Wilson. Zero ocorrências em n corridas: dizer só "abaixo de 3/n".
  - Distribuições: KS; quando a previsão vem de dados medidos ou de uma fórmula ajustada, o valor crítico é obtido por bootstrap, incluindo a incerteza da previsão.
  - Várias comparações no mesmo estudo: correção de Holm.
- Fórmulas e modelos: avaliados só fora dos dados de ajuste. Verificar automaticamente que nenhuma combinação de massas de treino coincide, em razões, com um canal de teste.
- Teste da teoria de fluxo: o mesmo critério de "origem caótica" dos dois lados (limiar k de embaralhamentos antes da primeira excursão na absorção; k embaralhamentos no último episódio na emissão).
- Creditar com honestidade trabalhos anteriores; buscar na literatura antes de afirmar novidade; resultados negativos e hipóteses reprovadas também são registrados.
- Hipóteses pelos três filtros: pequena, testável e corajosa; experimentos com grupo de controle e várias perturbações.
- Cada nota informa o tamanho da amostra por caso medido.

### 7.1 Forma de trabalhar (combinada em 5 nov. 2026)

- Cada sessão começa com uma pergunta só, um critério de sucesso e um limite de tempo de cálculo, combinados com o autor antes de rodar.
- Exploração: rápida e barata (poucas réplicas, aproximações), sempre anunciada como preliminar. Confirmação com os 95% completos só para o que vai ser publicado.
- Metas de fórmula com tolerância fixada antes e teste de equivalência (o erro fica abaixo da tolerância com 95% de confiança), e não "a fórmula é perfeita?".
- Publicação em lote: uma nota por achado relevante e consolidado, não a cada passo.
- Conferir cada afirmação contra as notas anteriores e a literatura antes de escrevê-la.

## 8. Termos fixos de tradução

| pt | en | de | fr |
|---|---|---|---|
| absortividade | absorptivity | Absorptivität | absorptivité |
| embaralhamento | scramble | Durchmischung | brassage |
| excursão | excursion | Exkursion | excursion |
| queda livre | free fall | freier Fall | chute libre |
| passagem (direta) | flyby | Vorbeiflug | survol |
| troca (de parceiro) | exchange | Austausch | échange |
| primeira passagem | first passage | erster Durchgang | premier passage |
| corpo que chega | incoming body | ankommender Körper | corps incident |
| muro de excentricidade | eccentricity wall | Exzentrizitätsmauer | mur d’excentricité |
| distância de passagem | passage distance | Vorbeiflugabstand | distance de passage |
| massa reduzida | reduced mass | reduzierte Masse | masse réduite |
| Tabela / Fig. | Table / Fig. | Tabelle / Abb. | Tableau / Fig. |

Símbolos do número de embaralhamentos: N_scr (en), N_dm (de), N_br (fr).

Convenções numéricas: pt, de e fr com vírgula decimal; de com ponto de milhar (225.000) e espaço antes de %; fr com espaço fino inseparável (U+00A0) nos milhares e antes de ; : % ?, e apóstrofo curvo; en com ponto decimal e vírgula de milhar.

## 9. Zenodo

- Script `zenodo-envio.user.js` (Tampermonkey, v1.1.0): lê `zenodo.json` do site; um toque cria o rascunho com metadados nos 4 idiomas (inglês como principal) e os 4 PDFs; segundo toque publica; botão "Nova versão" para correções. Reconhece cada nota pelo link da página (o título pode mudar).
- Metadados padrão: tipo `publication-technicalnote`, licença CC BY 4.0, criador "Wistuba Melo da Cunha, Willian" com ORCID, afiliação "Autodidata em Física", idiomas eng, por, deu, fra, relação "isvariantformof" com as 4 páginas, "issupplementedby" com `/codigo/` e "continues" com o DOI da nota anterior.
- Script geral `zenodo-geral.user.js` e o guia `zenodo-instrucoes-para-ia.txt` para outros trabalhos.

## 10. Riscos e pendências

1. **Versionamento.** Resolvido com o repositório privado no GitHub; o risco agora é esquecer o commit e push depois de cada nota ou correção. Uma sessão que publicou algo só termina depois do push.
2. A SPEC tem trechos antigos de identidade visual (Unbounded, IBM Plex, vermelho, cobalto, âmbar) e descrições defasadas ("dez scripts", "notas FR-TC-01 a FR-TC-04"): valem as seções 3 e 4 deste documento.
3. `/sobre` dá 404 (redirecionamento não aplicado no método de deploy atual).
4. Palavras-chave vazias nos metadados dos PDFs.
5. Dados brutos das simulações: os do regime L = 0 (notas 13 a 15) estão em `dados/dados_l0.tar.xz` (42 MB; descrição em `dados/LEIA-ME.md`). Novos estudos devem guardar os seus dados brutos comprimidos em `dados/`, um arquivo por estudo, abaixo de 50 MB cada (limite prático do GitHub sem LFS).
