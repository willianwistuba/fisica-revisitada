import os, subprocess, shutil, sys
from meta import *
from body import *

def build_tex(a,lang,L):
    ui=L['ui']; m=L['articles'][a['code']]
    _,body,_=render(a,lang,L)
    refs=''.join(f'\\bibitem{{r{i+1}}} '+esc_text(t)+(' \\href{'+u.replace('%','\\%').replace('#','\\#')+'}{\\nolinkurl{'+u.replace('https://','').replace('%','\\%').replace('#','\\#')+'}}' if u else '')+'\n' for i,(t,u) in enumerate(a['refs']))
    aurl=SITE+url(lang,'art',a['slug'])
    cite=esc_text(ui['cite_tpl'].replace('{title}',m['title']).replace('{code}',a['code']).replace('{url}','URLX')).replace('URLX','\\url{'+aurl+'}')
    tn=('\\\\[2pt]\\textit{'+esc_text(ui['translation_note'])+'}') if ui['translation_note'] else ''
    data=esc_text(ui['backmatter_data_text'].replace('{codeurl}','CODEX')).replace('CODEX','\\url{'+SITE+url(lang,'code')+'}')
    bab=BABEL[lang]
    others=','.join(BABEL[x] for x in LANGS if x!=lang)
    tex=r"""\documentclass[aps,pre,twocolumn,nofootinbib,floatfix,preprintnumbers,10pt]{revtex4-2}
\usepackage[T1]{fontenc}\usepackage[utf8]{inputenc}\usepackage{textcomp}
\usepackage["""+others+','+bab+r"""]{babel}
\usepackage{mathptmx}\usepackage{amsmath,amssymb}\usepackage{microtype}\usepackage{graphicx}
\usepackage{xcolor}\definecolor{fraccent}{HTML}{1D3FD8}\definecolor{frhot}{HTML}{E8480C}\definecolor{frink}{HTML}{111318}
\usepackage{pgfplots}\pgfplotsset{compat=1.16}\usetikzlibrary{babel}
\usepackage{hyperref}\usepackage{orcidlink}\hypersetup{colorlinks=true,urlcolor=fraccent,linkcolor=fraccent,citecolor=fraccent,pdfauthor={Willian Wistuba Melo da Cunha},pdftitle={"""+esc_text(m['title'])+r"""},pdflang={"""+HREFLANG[lang]+r"""}}
\AtBeginDocument{\renewcommand{\figurename}{"""+esc_text(ui['figure'])+r"""}\renewcommand{\tablename}{"""+esc_text(ui['table'])+r"""}\renewcommand{\refname}{"""+esc_text(ui['references'])+r"""}\renewcommand{\abstractname}{"""+esc_text(ui['abstract'])+r"""}}
\begin{document}
\preprint{F\'{I}SICA REVISITADA \textperiodcentered{} """+a['code']+r"""}
\preprint{"""+esc_text(m['type'])+r"""}
\title{"""+esc_text(m['title'])+r"""}
\author{Willian Wistuba Melo da Cunha\,\orcidlink{0009-0008-2875-6607}}
\affiliation{"""+esc_text(ui['pdf_author'])+r"""}

\begin{abstract}
"""+esc_text(m['abstract'])+r"""
\\[4pt]\noindent\textbf{"""+esc_text(ui['keywords'])+r""":} """+esc_text('; '.join(m['kw']))+r""".
\\[2pt]\noindent\textbf{ORCID:} \href{https://orcid.org/0009-0008-2875-6607}{0009-0008-2875-6607}"""+(("\\\\[2pt]\\noindent\\textbf{"+esc_text(ui["contact"])+":} \\href{mailto:profwistuba01@gmail.com}{profwistuba01@gmail.com}") if a["part"]>=13 else "")+r"""
\\[2pt]\noindent\textbf{"""+esc_text(ui['published'])+r""":} """+esc_text(ui['date_long'])+'. '+esc_text(ui['version'])+' 2. '+esc_text(ui['status_text'])+'.'+r"""
\\[2pt]\noindent\textbf{"""+esc_text(ui['series'])+r""":} """+esc_text(L['series']['title'])+', '+esc_text(ui['part'].replace('{n}',str(a['part'])).replace('{N}',str(len(ARTS))))+'. \\url{'+aurl+'}'+tn+r"""
\end{abstract}
\maketitle
"""+body+r"""
\section*{"""+esc_text(ui['backmatter_transparency_title'])+r"""}
"""+esc_text(ui['backmatter_transparency_text'])+r"""
\section*{"""+esc_text(ui['backmatter_data_title'])+r"""}
"""+data+r"""
\section*{"""+esc_text(ui['backmatter_coi_title'])+r"""}
"""+esc_text(ui['backmatter_coi_text'])+' '+esc_text(ui['backmatter_review_text'])+r"""
\section*{"""+esc_text(ui['cite_as'])+r"""}
{\small """+cite+r"""}
\begin{thebibliography}{99}
"""+refs+r"""\end{thebibliography}
\end{document}
"""
    return tex

def main(only=None):
    os.makedirs('texbuild',exist_ok=True)
    for lang in LANGS:
        L=load_i18n(lang); od='pdf' if lang=='pt' else f'pdf/{lang}'; os.makedirs(od,exist_ok=True)
        for a in ARTS:
            if only and a['code']!=only: continue
            name=f"{a['slug']}-{lang}"
            open(f'texbuild/{name}.tex','w',encoding='utf-8').write(build_tex(a,lang,L))
            for _ in range(2):
                r=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',name+'.tex'],cwd='texbuild',capture_output=True,text=True,errors='replace')
            if r.returncode!=0:
                print('ERRO',name); print(r.stdout[-3000:]); sys.exit(1)
            shutil.copy(f'texbuild/{name}.pdf', f"{od}/{a['slug']}.pdf")
            log=open(f'texbuild/{name}.log',errors='replace').read()
            ov=log.count('Overfull \\hbox')
            print('ok',lang,a['code'],os.path.getsize(f"{od}/{a['slug']}.pdf")//1024,'KB overfull',ov)
if __name__=='__main__': main(sys.argv[1] if len(sys.argv)>1 else None)
