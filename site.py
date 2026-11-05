import os, re, json, html, shutil
from meta import *
from body import *
AUTHOR='Willian Wistuba Melo da Cunha'
ORCID_ID='0009-0008-2875-6607'; EMAIL='profwistuba01@gmail.com'; ORCID='https://orcid.org/'+ORCID_ID
ORCID_SVG='<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="12" fill="#A6CE39"/><path fill="#fff" d="M7.4 17.6H5.9V6.8h1.5zM6.65 4.4a.95.95 0 1 1 0 1.9.95.95 0 0 1 0-1.9zM9.4 6.8h4c3.8 0 5.5 2.7 5.5 5.4 0 2.9-2.3 5.4-5.5 5.4h-4zm1.5 9.4h2.4c3.4 0 4.2-2.6 4.2-4 0-2.3-1.5-4-4.2-4h-2.4z"/></svg>'
OUT='public'; shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT)
def words(s): return len(re.sub(r'<[^>]+>',' ',s).split())
I={l:load_i18n(l) for l in LANGS}
CSS=open('estilo.css',encoding='utf-8').read()
open(os.path.join(OUT,'estilo.css'),'w',encoding='utf-8').write(CSS)

LOGO='<svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true"><rect width="30" height="30" rx="7" fill="var(--accent)"/><ellipse cx="15" cy="15" rx="10" ry="5.2" fill="none" stroke="#fff" stroke-width="1.6" transform="rotate(-28 15 15)"/><circle cx="15" cy="15" r="3" fill="#fff"/><circle cx="23.4" cy="10.3" r="2.1" fill="var(--hot)"/></svg>'
FAV="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3E%3Crect width='30' height='30' rx='7' fill='%231D3FD8'/%3E%3Cellipse cx='15' cy='15' rx='10' ry='5.2' fill='none' stroke='%23fff' stroke-width='1.6' transform='rotate(-28 15 15)'/%3E%3Ccircle cx='15' cy='15' r='3' fill='%23fff'/%3E%3Ccircle cx='23.4' cy='10.3' r='2.1' fill='%23E8480C'/%3E%3C/svg%3E"
KATEX='''<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body,{delimiters:[{left:'\\\\[',right:'\\\\]',display:true},{left:'\\\\(',right:'\\\\)',display:false}]})"></script>'''
def kurl(lang,key):
    return url(lang,key[0],key[1]) if key[0]=='art' else url(lang,key[0])
def byline(L,big=False):
    return f'<div class="byline{" big" if big else ""}"><span class="av">WC</span><div><b>{AUTHOR}</b><span>{E(L["ui"]["author_role"])} · <a href="{ORCID}">ORCID {ORCID_ID}</a></span></div></div>'

def page(lang,title,desc,body,key,cur=None,math=False,ld=None,ogtype='website'):
    L=I[lang]; ui=L['ui']; path=kurl(lang,key)
    nav=''.join(f'<a href="{url(lang,k)}"{" aria-current=\"page\"" if cur==k else ""}>{t}</a>' for k,t in [('notes',ui['nav_notes']),('series',ui['nav_series']),('method',ui['nav_method']),('code',ui['nav_code'])])
    alts=''.join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{SITE}{kurl(l,key)}">' for l in LANGS)+f'<link rel="alternate" hreflang="x-default" href="{SITE}{kurl("pt",key)}">'
    sw=''.join(f'<a href="{kurl(l,key)}" hreflang="{HREFLANG[l]}" lang="{HREFLANG[l]}"{" aria-current=\"true\"" if l==lang else ""}>{l.upper()}</a>' for l in LANGS)
    return f'''<!DOCTYPE html>
<html lang="{HREFLANG[lang]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{SITE}{path}">{alts}
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="{ogtype}"><meta property="og:url" content="{SITE}{path}"><meta property="og:site_name" content="Física Revisitada"><meta property="og:locale" content="{L['locale'].replace('-','_')}"><meta name="author" content="{AUTHOR}">
<meta name="theme-color" content="#1D3FD8">
<link rel="alternate" type="application/rss+xml" title="Física Revisitada" href="{PREFIX[lang]}/rss.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Inter+Tight:wght@600;700;800&family=JetBrains+Mono:wght@500;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/estilo.css">
<link rel="icon" href="{FAV}">
{extra_meta.get(path,'')}{KATEX if math else ''}{('<script type="application/ld+json">'+json.dumps(ld,ensure_ascii=False)+'</script>') if ld else ''}</head>
<body>
<a class="skip" href="#conteudo">{E(ui['skip'])}</a>
<header class="top"><div class="wrap bar">
<a class="brand" href="{url(lang,'home')}">{LOGO}<span>Física <b>Revisitada</b></span></a>
<nav class="nav" aria-label="Menu">{nav}</nav>
<form class="search" action="{url(lang,'notes')}" role="search"><svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><line x1="16.5" y1="16.5" x2="21" y2="21" stroke="currentColor" stroke-width="2"/></svg><input name="q" type="search" placeholder="{E(ui['search_ph'])}" aria-label="{E(ui['search_ph'])}"></form>
<nav class="lsw" aria-label="{E(ui['language'])}">{sw}</nav>
</div></header>
<main id="conteudo">{body}</main>
<footer class="foot"><div class="wrap fgrid">
<div><a class="brand" href="{url(lang,'home')}">{LOGO}<span>Física <b>Revisitada</b></span></a><p>{E(ui['foot_about'])}</p><p class="disc">{E(ui['foot_disc'])} <a href="{url(lang,'method')}">{E(ui['foot_how'])}</a>.</p></div>
<div><span class="eyebrow">{E(ui['foot_nav'])}</span><a href="{url(lang,'notes')}">{E(ui['all_notes'])}</a><a href="{url(lang,'series')}">{E(ui['foot_series'])}</a><a href="{url(lang,'method')}">{E(ui['foot_method'])}</a><a href="{url(lang,'code')}">{E(ui['foot_code'])}</a><a href="{PREFIX[lang]}/rss.xml">RSS</a></div>
</div></footer>
</body>
</html>'''
extra_meta={}
def wr(path,content):
    p=os.path.join(OUT,path.strip('/'),'index.html'); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'w',encoding='utf-8').write(content)

# ---------- dados por idioma ----------
D={}
for lang in LANGS:
    L=I[lang]; D[lang]=[]
    for a in ARTS:
        m=L['articles'][a['code']]; h,_,toc=render(a,lang,L)
        pdfp=('pdf/' if lang=='pt' else f'pdf/{lang}/')+a['slug']+'.pdf'
        D[lang].append(dict(a, **m, body=h, toc=toc, min=max(3,round(words(h)/200)), url=url(lang,'art',a['slug']), pdf=url(lang,'pdf',a['slug'])+'?v=3', pdfkb=round(os.path.getsize(pdfp)/1024)))

def card(lang,a):
    ui=I[lang]['ui']
    return f'''<a class="card" href="{a['url']}" data-q="{E((a['title']+' '+a['abstract']+' '+' '.join(a['kw'])+' '+a['type']).lower())}"><span class="eyebrow">{E(a['type'])} · {a['code']}</span><h3>{E(a['title'])}</h3><p>{E(a['abstract'][:220].rsplit(' ',1)[0])}…</p><span class="meta">{E(a.get('date_long',ui['date_long']))} · {a['min']} min · <span class="tag">PDF</span></span></a>'''

for lang in LANGS:
    L=I[lang]; ui=L['ui']; hm=L['home']; S=L['series']; A=D[lang]; N=len(A)
    # home
    parts=''.join(f'<li><span class="pn">{a["part"]:02d}</span><a href="{a["url"]}">{E(a["short"])}</a></li>' for a in A)
    steps=''.join(f'<div><span class="n">{i+1:02d}</span><h3>{E(t)}</h3><p>{E(p)}</p></div>' for i,(t,p) in enumerate(hm['steps']))
    home=f'''<section class="hero wrap"><div class="hot"></div><span class="eyebrow">{E(hm['eyebrow'])}</span>
<h1>{hm['h1']}</h1>
<p class="lead">{E(hm['lead'])}</p>
<div class="ctas"><a class="btn pri" href="{url(lang,'notes')}">{E(hm['cta_read'])}</a><a class="btn" href="{url(lang,'method')}">{E(hm['cta_method'])}</a></div>
<div class="stats"><div><b>{N}</b><span>{E(hm['stat_notes'])}</span></div><div><b>1</b><span>{E(hm['stat_series'])}</span></div><div><b>{len(LANGS)}</b><span>{E(hm['stat_langs'])}</span></div><div><b>{len(L['code_page']['files'])}</b><span>{E(hm['stat_scripts'])}</span></div></div>
</section>
<section class="band"><div class="wrap">
<span class="eyebrow">{E(hm['series_eyebrow'])}</span><h2>{E(hm['series_h2'])}</h2><p class="sub">{E(hm['series_sub'])}</p>
<div class="series"><div><span class="eyebrow">{E(hm['series_card_eyebrow'].replace('{n}',str(N)))}</span><h3><a href="{url(lang,'series')}">{E(S['title'])}</a></h3><p>{E(S['lead'])}</p><a class="link" href="{url(lang,'series')}">{E(hm['series_link'])}</a></div><ol class="parts">{parts}</ol></div>
</div></section>
<section class="wrap sec"><div class="head"><div><span class="eyebrow">{E(hm['latest_eyebrow'])}</span><h2>{E(hm['latest_h2'])}</h2><p class="sub">{E(hm['latest_sub'])}</p></div><a class="more" href="{url(lang,'notes')}">{E(hm['see_all'])}</a></div>
<div class="grid">{''.join(card(lang,a) for a in reversed(A))}</div></section>
<section class="wrap sec"><span class="eyebrow">{E(hm['method_eyebrow'])}</span><h2>{E(hm['method_h2'])}</h2>
<div class="steps">{steps}</div>
<div class="callout"><span class="eyebrow">{E(hm['transp_eyebrow'])}</span><p>{E(hm['transp_text'])} <a href="{url(lang,'method')}">{E(hm['transp_link'])}</a>.</p></div></section>'''
    wr(url(lang,'home'),page(lang,ui['site_title'],ui['site_desc'],home,('home',)))

    # notas
    notas=f'''<section class="wrap pagehead"><div class="hot"></div><span class="eyebrow">{E(hm['latest_eyebrow'])}</span><h1>{E(ui['notes_title'])}</h1><p class="lead">{E(ui['notes_lead'])}</p>
<input class="filter" id="f" type="search" placeholder="{E(ui['filter_ph'])}" aria-label="{E(ui['filter_aria'])}"></section>
<section class="wrap"><div class="grid" id="g">{''.join(card(lang,a) for a in reversed(A))}</div><p class="empty" id="e" hidden>{E(ui['empty'])}</p></section>
<script>(function(){{var f=document.getElementById('f'),cards=[].slice.call(document.querySelectorAll('#g .card')),e=document.getElementById('e');
function n(s){{return (s||'').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');}}
function run(){{var q=n(f.value),k=0;cards.forEach(function(c){{var ok=!q||n(c.dataset.q).indexOf(q)>=0;c.hidden=!ok;if(ok)k++;}});e.hidden=k>0;}}
try{{var q=new URLSearchParams(location.search).get('q');if(q)f.value=q;}}catch(x){{}}
f.addEventListener('input',run);run();}})();</script>'''
    wr(url(lang,'notes'),page(lang,ui['notes_title']+' · Física Revisitada',ui['notes_desc'],notas,('notes',),cur='notes'))

    # série
    sl=''.join(f'''<li><a href="{a['url']}"><span class="pn">{a['part']:02d}</span><div><span class="eyebrow">{E(a['type'])} · {a['code']}</span><h3>{E(a['title'])}</h3><p>{E(a['abstract'][:240].rsplit(' ',1)[0])}…</p></div></a><a class="pdfl" href="{a['pdf']}">PDF · {a['pdfkb']} KB</a></li>''' for a in A)
    ser=f'''<section class="wrap pagehead"><div class="hot"></div><span class="eyebrow">{E(ui['series_eyebrow'])}</span><h1>{E(S['title'])}</h1><p class="lead">{E(S['lead'])}</p></section>
<section class="wrap"><ol class="slist">{sl}</ol>
<div class="callout"><span class="eyebrow">{E(ui['series_order_title'])}</span><p>{E(ui['series_order_text'])}</p></div></section>'''
    wr(url(lang,'series'),page(lang,S['title']+' · Física Revisitada',S['lead'],ser,('series',),cur='series'))

    # artigos
    for i,a in enumerate(A):
        prev=A[i-1] if i else None; nxt=A[i+1] if i<N-1 else None
        refs=''.join(f'<li id="ref-{k+1}"><span class="rn">[{k+1}]</span><span>{E(t)}'+(f' <a href="{u}">{E(u.replace("https://",""))}</a>' if u else '')+'</span></li>' for k,(t,u) in enumerate(a['refs']))
        toc=''.join(f'<li class="l{lv}"><a href="#{sid}"><span>{no}</span> {E(t)}</a></li>' for sid,no,t,lv in a['toc'])
        stoc=''.join(f'<li{" class=\"on\"" if b is a else ""}><span>{b["part"]:02d}</span><a href="{b["url"]}">{E(b["short"])}</a></li>' for b in A)
        cite=ui['cite_tpl'].replace('{title}',a['title']).replace('{code}',a['code']).replace('{url}',SITE+a['url'])
        langs=''.join(f'<a href="{url(l,"art",a["slug"])}" hreflang="{HREFLANG[l]}" lang="{HREFLANG[l]}"{" aria-current=\"true\"" if l==lang else ""}>{E(I[l]["name"])}</a>' for l in LANGS)
        tn=f'<p class="trnote">{E(ui["translation_note"])} <a href="{url("pt","art",a["slug"])}" hreflang="pt-BR">PT</a></p>' if ui['translation_note'] else ''
        part=ui['part'].replace('{n}',str(a['part'])).replace('{N}',str(N))
        pager='<nav class="pager">'+(f'<a href="{prev["url"]}"><span class="eyebrow">{E(ui["prev"])}</span>{E(prev["short"])}</a>' if prev else f'<a href="{url(lang,"series")}"><span class="eyebrow">{E(ui["series"])}</span>{E(ui["overview"])}</a>')+(f'<a class="r" href="{nxt["url"]}"><span class="eyebrow">{E(ui["next"])}</span>{E(nxt["short"])}</a>' if nxt else f'<a class="r" href="{url(lang,"notes")}"><span class="eyebrow">{E(ui["more"])}</span>{E(ui["all_notes"])}</a>')+'</nav>'
        data=E(ui['backmatter_data_text']).replace('{codeurl}',f'<a href="{url(lang,"code")}">{SITE}{url(lang,"code")}</a>')
        body=f'''<article class="paper" lang="{HREFLANG[lang]}">
<div class="wrap pgrid"><div class="pmain">
<div class="masthead"><span class="jn">Física Revisitada</span><span class="js">{E(ui['journal_sub'])}</span><span class="jc">{a['code']} (2026)</span></div>
<span class="ptype">{E(a['type'])}</span>
<h1 class="ptitle">{E(a['title'])}</h1>
<div class="authors"><span class="aname">{AUTHOR} <a class="orcid" href="{ORCID}" title="ORCID {ORCID_ID}" aria-label="ORCID {ORCID_ID}">{ORCID_SVG}<span>{ORCID_ID}</span></a></span><span class="aff">{E(ui['author_role'])}</span>{(f'<span class="aff">{E(ui["contact"])}: <a href="mailto:{EMAIL}">{EMAIL}</a></span>') if a['part']>=13 else ''}</div>
<dl class="pinfo"><div><dt>{E(ui['published'])}</dt><dd>{E(a.get('date_long',ui['date_long']))}</dd></div><div><dt>{E(ui['version'])}</dt><dd>{E(a.get('version_note',ui['version_note']))}</dd></div><div><dt>{E(ui['status'])}</dt><dd>{E(ui['status_text'])}</dd></div><div><dt>{E(ui['series'])}</dt><dd><a href="{url(lang,'series')}">{E(S['title'])}</a>, {E(part)}</dd></div></dl>
<div class="pactions"><a class="btn pri" href="{a['pdf']}" download>{E(ui['download_pdf'])} · {a['pdfkb']} KB</a><a class="btn" href="#citar">{E(ui['cite_as'])}</a></div>
<nav class="plangs" aria-label="{E(ui['other_langs'])}"><span>{E(ui['other_langs'])}:</span>{langs}</nav>
{tn}
<section class="abstract"><h2>{E(ui['abstract'])}</h2><p>{E(a['abstract'])}</p><p class="kw"><b>{E(ui['keywords'])}:</b> {E('; '.join(a['kw']))}.</p></section>
<div class="pbody">{a['body']}</div>
<section class="back">
<h2>{E(ui['backmatter_transparency_title'])}</h2><p>{E(ui['backmatter_transparency_text'])}</p>
<h2>{E(ui['backmatter_data_title'])}</h2><p>{data}</p>
<h2>{E(ui['backmatter_coi_title'])}</h2><p>{E(ui['backmatter_coi_text'])}</p>
<h2>{E(ui['backmatter_review_title'])}</h2><p>{E(ui['backmatter_review_text'])}</p>
</section>
<section class="refs"><h2>{E(ui['references'])}</h2><ol>{refs}</ol></section>
<section class="citebox" id="citar"><span class="eyebrow">{E(ui['cite_as'])}</span><p class="mono">{E(cite)}</p></section>
{pager}
</div>
<aside class="pside"><div class="stick"><span class="eyebrow">{E(ui['contents'])}</span><ol class="ptoc">{toc}</ol><a class="btn pri full" href="{a['pdf']}" download>{E(ui['download_pdf'])}</a><span class="eyebrow sp">{E(ui['series'])}</span><a class="stitle" href="{url(lang,'series')}">{E(S['title'])}</a><ol class="toc">{stoc}</ol></div></aside>
</div></article>'''
        ld={"@context":"https://schema.org","@type":"ScholarlyArticle","headline":a['title'],"abstract":a['abstract'],"keywords":a['kw'],"datePublished":a.get("date_iso",DATE),"dateModified":a.get("date_iso",DATE),"version":a.get("version_num","2"),"inLanguage":HREFLANG[lang],"url":SITE+a['url'],"identifier":a['code'],"isPartOf":{"@type":"CreativeWorkSeries","name":S['title']},"author":{"@type":"Person","name":AUTHOR,"description":ui['author_role'],"identifier":ORCID,"sameAs":[ORCID]},"publisher":{"@type":"Organization","name":"Física Revisitada"},"citation":[t for t,_ in a['refs']],"encoding":{"@type":"MediaObject","contentUrl":SITE+a['pdf'],"encodingFormat":"application/pdf"}}
        if lang!='pt': ld["translationOfWork"]={"@type":"ScholarlyArticle","url":SITE+url('pt','art',a['slug'])}
        hw=f'<meta name="citation_title" content="{E(a["title"])}"><meta name="citation_author" content="Cunha, Willian Wistuba Melo da"><meta name="citation_author_orcid" content="'+ORCID+'"><meta name="citation_publication_date" content="2026/11/03"><meta name="citation_journal_title" content="Física Revisitada"><meta name="citation_technical_report_number" content="{a["code"]}"><meta name="citation_language" content="{lang}"><meta name="citation_pdf_url" content="{SITE}{a["pdf"]}"><meta name="citation_abstract_html_url" content="{SITE}{a["url"]}">'+''.join(f'<meta name="citation_keywords" content="{E(k)}">' for k in a['kw'])+''.join(f'<meta name="citation_reference" content="{E(t)}">' for t,_ in a['refs'])
        extra_meta[a['url']]=hw
        wr(a['url'],page(lang,a['title']+' · Física Revisitada',a['abstract'][:300],body,('art',a['slug']),cur='notes',math=True,ld=ld,ogtype='article'))

    # método
    mp=L['method_page']
    met=f'''<section class="wrap pagehead"><div class="hot"></div><span class="eyebrow">{E(mp['eyebrow'])}</span><h1>{E(mp['h1'])}</h1><p class="lead">{E(mp['lead'])}</p></section>
<section class="wrap prose">{mp['body'].replace('{byline}',byline(L,True))}</section>'''
    wr(url(lang,'method'),page(lang,ui['method_title']+' · Física Revisitada',ui['method_desc'],met,('method',),cur='method'))

    # código
    cp=L['code_page']
    if lang=='pt':
        os.makedirs(os.path.join(OUT,'codigo'),exist_ok=True)
        for f in cp['files']:
            os.makedirs(os.path.dirname(os.path.join(OUT,'codigo',f)),exist_ok=True); shutil.copy('codigo_src/'+f, os.path.join(OUT,'codigo',f))
    rows=''.join(f'<tr><td><a href="/codigo/{f}"><code>{f}</code></a></td><td>{E(d)}</td></tr>' for f,d in cp['files'].items())
    cod=f'''<section class="wrap pagehead"><div class="hot"></div><span class="eyebrow">{E(cp['eyebrow'])}</span><h1>{E(cp['h1'])}</h1><p class="lead">{E(cp['lead'])}</p></section>
<section class="wrap prose"><p>{cp['intro']}</p>
<div class="tblwrap"><table><thead><tr><th>{E(cp['th_file'])}</th><th>{E(cp['th_what'])}</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="note">{cp['note']}</p></section>'''
    wr(url(lang,'code'),page(lang,ui['code_title']+' · Física Revisitada',ui['code_desc'],cod,('code',),cur='code'))

    # pdf, rss
    od=os.path.join(OUT,'pdf') if lang=='pt' else os.path.join(OUT,'pdf',lang); os.makedirs(od,exist_ok=True)
    for a in A: shutil.copy(('pdf/' if lang=='pt' else f'pdf/{lang}/')+a['slug']+'.pdf', os.path.join(od,a['slug']+'.pdf'))
    items=''.join(f'<item><title>{E(a["title"])}</title><link>{SITE}{a["url"]}</link><guid>{SITE}{a["url"]}</guid><pubDate>Tue, 03 Nov 2026 03:00:00 GMT</pubDate><description>{E(a["abstract"])}</description><enclosure url="{SITE}{a["pdf"]}" type="application/pdf" length="{os.path.getsize(OUT+a["pdf"].split("?")[0])}"/></item>' for a in reversed(A))
    rp=os.path.join(OUT,PREFIX[lang].strip('/'),'rss.xml'); os.makedirs(os.path.dirname(rp),exist_ok=True)
    open(rp,'w',encoding='utf-8').write(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Física Revisitada</title><link>{SITE}{url(lang,"home")}</link><description>{E(ui["rss_desc"])}</description><language>{HREFLANG[lang]}</language>{items}</channel></rss>')

keys=[('home',),('notes',),('series',),('method',),('code',)]+[('art',a['slug']) for a in ARTS]
sm=''.join(f'<url><loc>{SITE}{kurl(l,k)}</loc><lastmod>{DATE}</lastmod>'+''.join(f'<xhtml:link rel="alternate" hreflang="{HREFLANG[x]}" href="{SITE}{kurl(x,k)}"/>' for x in LANGS)+'</url>' for k in keys for l in LANGS)
open(os.path.join(OUT,'sitemap.xml'),'w',encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'+sm+'</urlset>')
open(os.path.join(OUT,'robots.txt'),'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
# índice para o script de envio ao Zenodo (lido por zenodo-envio.user.js)
ZL={'pt':'por','en':'eng','de':'deu','fr':'fra'}
zn=[]
for a in ARTS:
    c=a['code']; s=a['slug']
    zn.append({'code':c,'part':a['part'],'slug':s,
        'langs':{l:{'iso':ZL[l],'title':I[l]['articles'][c]['title'],'abstract':I[l]['articles'][c]['abstract'],
                    'keywords':I[l]['articles'][c]['kw'],'page':SITE+kurl(l,('art',s)),
                    'pdf':SITE+('/pdf/' if l=='pt' else f'/pdf/{l}/')+s+'.pdf'} for l in LANGS}})
json.dump({'site':SITE,'code_page':SITE+'/codigo/','generated':DATE,'notes':zn},open(os.path.join(OUT,'zenodo.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)

print('ok', sum(len(f) for _,_,f in os.walk(OUT)),'arquivos')
