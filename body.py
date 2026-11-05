"""Leitura dos artigos (src/<lang>/aN.html) e renderização para o site e para LaTeX (REVTeX)."""
import re, json, math, html as H
from bs4 import BeautifulSoup, NavigableString, Tag
from meta import *

def load_i18n(lang): return json.load(open(f'i18n/{lang}.json',encoding='utf-8'))
def roman(n): return ['','I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII'][n]
def num(x,L): return str(x).replace('.',L['decimal'])
E=H.escape

# ---------------- figuras: dados ----------------
A2_AB=[0.02,0.04,0.07,0.1,0.15,0.2,0.3,0.4,0.5,0.6]
A2_DATA=[('M = 1','hot',10.7,[10.7,10.0,9.7,7.2,7.4,7.6,4.2,5.6,4.9,4.6]),('M = 3','accent',7.8,[7.8,7.9,7.7,6.5,5.5,5.6,3.1,3.7,3.4,2.1]),('M = 10','ink',7.4,[7.3,7.0,6.6,5.9,5.4,4.1,2.7,2.0,1.2,0.6])]
A4_V=[2.02,3.17,3.30,0.87,0.81,0.66,3.26,3.36,5.13]; A4_C=['hot']*3+['accent']*3+['ink']*3

def svg_a2(L):
    f=L['fig']['A2']; W,Hh,Lm,R,T,B=640,340,60,92,26,50
    X=lambda a:Lm+(W-Lm-R)*math.log(a/0.02)/math.log(30); Y=lambda v:Hh-B-(Hh-B-T)*v/1.25
    xl=E(f['x']).replace('a_b','<tspan font-style="italic">a</tspan><tspan baseline-shift="sub" font-size="75%">b</tspan>')
    s=[f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="{E(f["aria"])}">']
    for v in [0,0.25,0.5,0.75,1.0,1.25]:
        s.append(f'<line x1="{Lm}" y1="{Y(v):.1f}" x2="{W-R}" y2="{Y(v):.1f}" stroke="var(--line)"/><text x="{Lm-8}" y="{Y(v)+4:.1f}" text-anchor="end" class="ax">{num(f'{v:g}',L)}</text>')
    for a in [0.02,0.05,0.1,0.2,0.6]: s.append(f'<text x="{X(a):.1f}" y="{Hh-B+18}" text-anchor="middle" class="ax">{num(a,L)}</text>')
    s.append(f'<text x="{(Lm+W-R)/2:.0f}" y="{Hh-10}" text-anchor="middle" class="ax">{xl}</text><text x="{Lm}" y="{T-10}" class="ax">{E(f["y"])}</text>')
    s.append(f'<line x1="{Lm}" y1="{Y(1):.1f}" x2="{W-R}" y2="{Y(1):.1f}" stroke="var(--muted)" stroke-width="1.5" stroke-dasharray="6 4"/><text x="{W-R+6}" y="{Y(1)+4:.1f}" class="lbl">{E(f["control"])}</text>')
    for k,c,ct,v in A2_DATA:
        c=f'var(--{c})'
        s.append(f'<polyline points="{" ".join(f"{X(a):.1f},{Y(x/ct):.1f}" for a,x in zip(A2_AB,v))}" fill="none" stroke="{c}" stroke-width="2.2"/>')
        s.append(''.join(f'<circle cx="{X(a):.1f}" cy="{Y(x/ct):.1f}" r="3.2" fill="{c}"/>' for a,x in zip(A2_AB,v)))
        s.append(f'<text x="{X(0.6)+8:.1f}" y="{Y(v[-1]/ct)+4:.1f}" class="lbl" fill="{c}">{k}</text>')
    return ''.join(s)+'</svg>'

def svg_a4(L):
    f=L['fig']['A4']; rows=f['rows']; W=640;Lm=190;R=36;T=16;rh=28;Hh=T+rh*len(rows)+46
    X=lambda v:Lm+(W-Lm-R)*math.log(v/0.5)/math.log(16)
    pct=lambda v:(num(v,L)+(' %' if L['lang'] in ('de','fr') else '%'))
    s=[f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="{E(f["aria"])}">']
    for v in [0.5,1,2,4,8]: s.append(f'<line x1="{X(v):.1f}" y1="{T-4}" x2="{X(v):.1f}" y2="{T+rh*len(rows)}" stroke="var(--line)"/><text x="{X(v):.1f}" y="{T+rh*len(rows)+16}" text-anchor="middle" class="ax">{pct(v)}</text>')
    s.append(f'<text x="{(Lm+W-R)/2:.0f}" y="{Hh-8}" text-anchor="middle" class="ax">{E(f["x"])}</text>')
    for i,(n,v,c) in enumerate(zip(rows,A4_V,A4_C)):
        y=T+rh*i+rh/2; c=f'var(--{c})'
        s.append(f'<text x="{Lm-10}" y="{y+4:.1f}" text-anchor="end" class="lbl">{E(n)}</text><line x1="{X(0.5):.1f}" y1="{y:.1f}" x2="{X(v):.1f}" y2="{y:.1f}" stroke="{c}" stroke-width="2"/><circle cx="{X(v):.1f}" cy="{y:.1f}" r="5.5" fill="{c}"/><text x="{X(v)+10:.1f}" y="{y+4:.1f}" class="ax">{pct(f"{v:.2f}")}</text>')
    return ''.join(s)+'</svg>'

# ---------------- LaTeX: texto ----------------
UMAP={'≈':r'$\approx$','×':r'$\times$','√':r'$\surd$','≤':r'$\leq$','≥':r'$\geq$','÷':r'$\div$','°':r'\textdegree{}','<':r'$<$','>':r'$>$',
      'μ':r'$\mu$','β':r'$\beta$','ε':r'$\varepsilon$','γ':r'$\gamma$','δ':r'$\delta$','λ':r'$\lambda$','π':r'$\pi$','Λ':r'$\Lambda$',
      '₃':r'$_3$','³':r'$^3$','²':r'$^2$','→':r'$\rightarrow$','←':r'$\leftarrow$','∞':r'$\infty$','·':r'\textperiodcentered{}','−':'-',
      '\u202f':r'\,','\u2009':r'\,','≲':r'$\lesssim$','§':r'\S{}'}
def esc_text(s):
    s=s.replace('⁻³','\x00')
    out=[]
    for ch in s:
        if ch=='\x00': out.append(r'$^{-3}$'); continue
        if ch in UMAP: out.append(UMAP[ch]); continue
        if ch in '&%#_$': out.append('\\'+ch); continue
        if ch=='{': out.append(r'\{'); continue
        if ch=='}': out.append(r'\}'); continue
        if ch=='~': out.append(r'\textasciitilde{}'); continue
        if ch=='^': out.append(r'\textasciicircum{}'); continue
        if ch=='\\': out.append(r'\textbackslash{}'); continue
        out.append(ch)
    t=''.join(out)
    t=re.sub(r'"([^"]*)"', r"``\1''", t)
    return t
MATH=re.compile(r'(\\\(.*?\\\)|\\\[.*?\\\])', re.S)
def conv_str(s):
    r=[]
    for p in MATH.split(s):
        if not p: continue
        r.append(p if (p.startswith('\\(') or p.startswith('\\[')) else esc_text(p))
    return ''.join(r)
def tex_inline(node):
    if isinstance(node, NavigableString): return conv_str(str(node))
    if not isinstance(node, Tag): return ''
    n=node.name
    if n=='cite': return r'~\cite{'+','.join('r'+x.strip() for x in node.get_text().split(','))+'}'
    inner=''.join(tex_inline(c) for c in node.children)
    if n in ('b','strong'): return r'\textbf{'+inner+'}'
    if n in ('i','em'): return r'\emph{'+inner+'}'
    if n=='a': return r'\href{'+node.get('href','').replace('%','\\%').replace('#','\\#')+'}{'+inner+'}'
    if n=='code': return r'\texttt{'+inner+'}'
    return inner
def strip_cite_space(t): return re.sub(r'\s+~\\cite',r'~\\cite',t)

def tex_fig_a2(L,cap):
    f=L['fig']['A2']; d=L['decimal']
    sep='{,}' if d==',' else '.'
    plots=''.join(f"\\addplot[color=fr{c},mark={mk},mark size=1.4pt,thick] coordinates {{{' '.join(f'({a},{v/ct:.3f})' for a,v in zip(A2_AB,vals))}}};\n\\addlegendentry{{${name.replace(' ','')}$}}\n" for (name,c,ct,vals),mk in zip(A2_DATA,['*','square*','triangle*']))
    xl=esc_text(f['x']).replace('a\\_b','$a_b$'); yl=esc_text(f['y'])
    tl=lambda xs:','.join(str(x).replace('.',sep) for x in xs)
    return r"""\begin{figure}[tb]\centering
\begin{tikzpicture}\begin{axis}[width=\columnwidth,height=5.6cm,xmode=log,xmin=0.018,xmax=0.66,ymin=0,ymax=1.25,
xlabel={"""+xl+r"""},ylabel={"""+yl+r"""},
xtick={0.02,0.05,0.1,0.2,0.6},xticklabels={"""+tl([0.02,0.05,0.1,0.2,0.6])+r"""},
ytick={0,0.25,0.5,0.75,1,1.25},yticklabels={"""+tl([0,0.25,0.5,0.75,1,1.25])+r"""},
grid=major,grid style={line width=.2pt,draw=gray!30},legend pos=south west,legend style={font=\scriptsize,draw=none,fill=white,fill opacity=0.9,text opacity=1},tick label style={font=\scriptsize},label style={font=\footnotesize}]
\addplot[black,dashed,domain=0.018:0.66,forget plot] {1};
"""+plots+r"""\end{axis}\end{tikzpicture}
\caption{"""+cap+r"""}\end{figure}
"""
def tex_fig_a4(L,cap):
    f=L['fig']['A4']; d=L['decimal']; sep='{,}' if d==',' else '.'
    rows=f['rows']; n=len(rows); sp='\\,' if L['lang'] in ('de','fr') else ''
    pts=''.join(f"\\addplot[only marks,mark=*,mark size=2pt,color=fr{c}] coordinates {{({v},{n-i})}};\n\\draw[fr{c},line width=.7pt] (axis cs:0.5,{n-i}) -- (axis cs:{v},{n-i});\n\\node[anchor=west,font=\\tiny] at (axis cs:{v*1.07},{n-i}) {{{f'{v:.2f}'.replace('.',sep)}{sp}\\%}};\n" for i,(v,c) in enumerate(zip(A4_V,A4_C)))
    yl=','.join('{'+esc_text(r)+'}' for r in reversed(rows))
    xt=','.join(f'{str(x).replace(".",sep)}{sp}\\%' for x in [0.5,1,2,4,8])
    return r"""\begin{figure}[tb]\centering
\begin{tikzpicture}\begin{axis}[width=0.72\columnwidth,height=6.4cm,xmode=log,xmin=0.5,xmax=8,ymin=0.4,ymax="""+str(n+0.6)+r""",
ytick={1,...,"""+str(n)+r"""},yticklabels={"""+yl+r"""},xtick={0.5,1,2,4,8},xticklabels={"""+xt+r"""},
xlabel={"""+esc_text(f['x'])+r"""},grid=major,grid style={line width=.2pt,draw=gray!30},
tick label style={font=\scriptsize},label style={font=\footnotesize},clip=false]
"""+pts+r"""\end{axis}\end{tikzpicture}
\caption{"""+cap+r"""}\end{figure}
"""
TEXFIG={'A2':tex_fig_a2,'A4':tex_fig_a4}
SVGFIG={'A2':svg_a2,'A4':svg_a4}

def render(a,lang,L):
    """Devolve (html_site, tex_body, toc)."""
    raw=open(f'src/{lang}/{a["src"]}',encoding='utf-8').read()
    soup=BeautifulSoup(raw,'html.parser')
    H_out=[]; T_out=[]; toc=[]
    sec=0; sub=0; eq=0; fig=0; tab=0
    ui=L['ui']
    def site_inline(node):
        if isinstance(node,NavigableString): return str(node)
        if not isinstance(node,Tag): return ''
        if node.name=='cite':
            ns=[x.strip() for x in node.get_text().split(',')]
            return '<span class="cite">['+', '.join(f'<a href="#ref-{x}">{x}</a>' for x in ns)+']</span>'
        inner=''.join(site_inline(c) for c in node.children)
        attrs=''.join(f' {k}="{E(v if isinstance(v,str) else " ".join(v))}"' for k,v in node.attrs.items())
        return f'<{node.name}{attrs}>{inner}</{node.name}>'
    for node in soup.children:
        if isinstance(node,NavigableString):
            if node.strip(): H_out.append(str(node)); T_out.append(conv_str(str(node)))
            continue
        n=node.name; cls=node.get('class') or []
        if n=='h2':
            sec+=1; sub=0; t=node.get_text().strip(); sid=f's{sec}'
            toc.append((sid,roman(sec)+'.',t,2))
            H_out.append(f'<h2 id="{sid}"><span class="no">{roman(sec)}.</span> {E(t)}</h2>')
            T_out.append('\\section{'+conv_str(t)+'}\n')
        elif n=='h3':
            sub+=1; t=node.get_text().strip(); sid=f's{sec}{chr(96+sub)}'
            toc.append((sid,chr(64+sub)+'.',t,3))
            H_out.append(f'<h3 id="{sid}"><span class="no">{chr(64+sub)}.</span> {E(t)}</h3>')
            T_out.append('\\subsection{'+conv_str(t)+'}\n')
        elif n=='p':
            H_out.append(site_inline(node))
            T_out.append(strip_cite_space(''.join(tex_inline(c) for c in node.children))+'\n\n')
        elif n in ('ul','ol'):
            H_out.append(site_inline(node))
            env='itemize' if n=='ul' else 'enumerate'
            T_out.append(f'\\begin{{{env}}}\n'+''.join('\\item '+strip_cite_space(''.join(tex_inline(c) for c in li.children))+'\n' for li in node.find_all('li',recursive=False))+f'\\end{{{env}}}\n')
        elif n=='div' and 'eq' in cls:
            eq+=1; m=node.get_text().strip(); m=m[2:-2].strip() if m.startswith('\\[') else m
            H_out.append(f'<div class="eq" id="eq{eq}">\\[ {m} \\tag{{{eq}}} \\]</div>')
            T_out.append('\\begin{equation}\n'+m+'\n\\end{equation}\n')
        elif n=='figure':
            fig+=1; key=node['data-fig']; capn=node.find('figcaption')
            caph=site_inline(capn)[len('<figcaption>'):-len('</figcaption>')]
            H_out.append(f'<figure id="fig{fig}">{SVGFIG[key](L)}<figcaption><b>{ui["figure"]} {fig}.</b> {caph}</figcaption></figure>')
            T_out.append(TEXFIG[key](L,strip_cite_space(''.join(tex_inline(c) for c in capn.children))))
        elif n=='div' and 'tblwrap' in cls:
            tab+=1; capn=node.find('p',class_='cap'); tb=node.find('table')
            caph=site_inline(capn)[len('<p class="cap">'):-len('</p>')]
            H_out.append(f'<div class="tblwrap" id="tab{tab}"><p class="tcap"><b>{ui["table"]} {roman(tab)}.</b> {caph}</p>{site_inline(tb)}</div>')
            rows=tb.find_all('tr'); nc=len(rows[0].find_all(['th','td']))
            lines=[]
            for i,r in enumerate(rows):
                cells=[''.join(tex_inline(c) for c in td.children) for td in r.find_all(['th','td'])]
                lines.append(' & '.join(cells)+r' \\')
                if i==0: lines.append(r'\colrule')
            wide=nc>5 or any(len(td.get_text())>22 for td in tb.find_all('td')) or (nc>=4 and sum(len(th.get_text()) for th in tb.find_all('th'))>45)
            env='table*' if wide else 'table'
            T_out.append(f'\\begin{{{env}}}[tb]\\caption{{'+strip_cite_space(''.join(tex_inline(c) for c in capn.children))+'}\n\\begin{ruledtabular}\n\\begin{tabular}{'+'l'*nc+'}\n'+'\n'.join(lines)+f'\n\\end{{tabular}}\n\\end{{ruledtabular}}\n\\end{{{env}}}\n')
        else:
            H_out.append(str(node)); T_out.append(conv_str(node.get_text())+'\n')
    return '\n'.join(H_out), ''.join(T_out), toc

# ---------------- figura A5 (ejeção) ----------------
A5_ROWS=['1, 1, 1','1, 1, 3','1, 1, 10','3, 3, 1','10, 10, 1']
A5_MOST=[0.367,0.518,0.598,0.759,0.950]; A5_NAIVE=[None,0.485,0.498,0.942,0.974]
def svg_a5(L):
    f=L['fig']['A5']; W=640; Lm=96; R=40; T=48; gh=46; Hh=T+gh*len(A5_ROWS)+46
    X=lambda v:Lm+(W-Lm-R)*v
    pct=lambda v:(num(f'{v*100:.0f}',L)+(' %' if L['lang'] in ('de','fr') else '%'))
    s=[f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="{E(f["aria"])}">']
    s.append(f'<rect x="{Lm}" y="8" width="12" height="12" fill="var(--accent)"/><text x="{Lm+18}" y="18" class="lbl">{E(f["most"])}</text>')
    s.append(f'<rect x="{Lm+330}" y="8" width="12" height="12" fill="var(--hot)"/><text x="{Lm+348}" y="18" class="lbl">{E(f["naive"])}</text>')
    yb=T+gh*len(A5_ROWS)
    for v in [0,0.25,0.5,0.75,1]: s.append(f'<line x1="{X(v):.1f}" y1="{T-4}" x2="{X(v):.1f}" y2="{yb}" stroke="var(--line)"/><text x="{X(v):.1f}" y="{yb+16}" text-anchor="middle" class="ax">{pct(v)}</text>')
    s.append(f'<line x1="{X(1/3):.1f}" y1="{T-4}" x2="{X(1/3):.1f}" y2="{yb}" stroke="var(--muted)" stroke-width="1.5" stroke-dasharray="6 4"/><text x="{X(1/3)+4:.1f}" y="{T-8}" class="ax">{E(f["chance"])}</text>')
    s.append(f'<text x="{(Lm+W-R)/2:.0f}" y="{Hh-8}" text-anchor="middle" class="ax">{E(f["x"])}</text>')
    for i,(lab,a,b) in enumerate(zip(A5_ROWS,A5_MOST,A5_NAIVE)):
        y=T+gh*i+6
        s.append(f'<text x="{Lm-10}" y="{y+17}" text-anchor="end" class="lbl">{lab}</text>')
        s.append(f'<rect x="{X(0):.1f}" y="{y}" width="{X(a)-X(0):.1f}" height="14" fill="var(--accent)"/><text x="{X(a)+6:.1f}" y="{y+11}" class="ax">{pct(a)}</text>')
        if b is None: s.append(f'<text x="{X(0)+4:.1f}" y="{y+28}" class="ax">{E(f["na"])}</text>')
        else: s.append(f'<rect x="{X(0):.1f}" y="{y+17}" width="{X(b)-X(0):.1f}" height="14" fill="var(--hot)"/><text x="{X(b)+6:.1f}" y="{y+28}" class="ax">{pct(b)}</text>')
    return ''.join(s)+'</svg>'
def tex_fig_a5(L,cap):
    f=L['fig']['A5']; sep='{,}' if L['decimal']==',' else '.'; sp='\\,' if L['lang'] in ('de','fr') else ''
    n=len(A5_ROWS)
    most=' '.join(f'({v*100:.1f},{n-i})' for i,v in enumerate(A5_MOST))
    naive=' '.join(f'({v*100:.1f},{n-i})' for i,v in enumerate(A5_NAIVE) if v is not None)
    yl=','.join('{'+r+'}' for r in reversed(A5_ROWS))
    return r"""\begin{figure}[tb]\centering
\begin{tikzpicture}\begin{axis}[width=\columnwidth,height=6.2cm,xbar=1pt,bar width=5pt,xmin=0,xmax=100,ymin=0.4,ymax="""+str(n+0.6)+r""",
ytick={1,...,"""+str(n)+r"""},yticklabels={"""+yl+r"""},xtick={0,25,50,75,100},xticklabels={0"""+sp+r"""\%,25"""+sp+r"""\%,50"""+sp+r"""\%,75"""+sp+r"""\%,100"""+sp+r"""\%},
xlabel={"""+esc_text(f['x'])+r"""},grid=major,grid style={line width=.2pt,draw=gray!30},legend style={font=\scriptsize,at={(0.5,1.02)},anchor=south,legend columns=2,draw=none},
tick label style={font=\scriptsize},label style={font=\footnotesize}]
\addplot[fill=fraccent,draw=none] coordinates {"""+most+r"""};\addlegendentry{"""+esc_text(f['most'])+r"""}
\addplot[fill=frhot,draw=none] coordinates {"""+naive+r"""};\addlegendentry{"""+esc_text(f['naive'])+r"""}
\draw[black,dashed] (axis cs:33.3,0.4) -- (axis cs:33.3,"""+str(n+0.6)+r""");
\end{axis}\end{tikzpicture}
\caption{"""+cap+r"""}\end{figure}
"""
TEXFIG['A5']=tex_fig_a5; SVGFIG['A5']=svg_a5

# ---------------- figura A6 (velocidade x massas) ----------------
A6_ROWS=['1, 1, 1','1, 1, 3','1, 1, 10','3, 3, 1','10, 10, 1',None]
A6_VALS=[[0.333,0.369,0.369],[0.487,0.555,0.559],[0.497,0.601,0.584],[0.940,0.701,0.940],[0.980,0.716,0.980],[0.714,0.573,0.717]]
A6_COLS=['ink','accent','hot']
def svg_a6(L):
    f=L['fig']['A6']; rows=[r or f['rows_last'] for r in A6_ROWS]
    W=640; Lm=100; R=44; T=50; gh=58; Hh=T+gh*len(rows)+46
    X=lambda v:Lm+(W-Lm-R)*v
    pct=lambda v:(num(f'{v*100:.0f}',L)+(' %' if L['lang'] in ('de','fr') else '%'))
    s=[f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="{E(f["aria"])}">']
    for j,(key,c) in enumerate(zip(['mass','speed','both'],A6_COLS)):
        x0=Lm+j*175; s.append(f'<rect x="{x0}" y="8" width="12" height="12" fill="var(--{c})"/><text x="{x0+18}" y="18" class="lbl">{E(f[key])}</text>')
    yb=T+gh*len(rows)
    for v in [0,0.25,0.5,0.75,1]: s.append(f'<line x1="{X(v):.1f}" y1="{T-6}" x2="{X(v):.1f}" y2="{yb}" stroke="var(--line)"/><text x="{X(v):.1f}" y="{yb+16}" text-anchor="middle" class="ax">{pct(v)}</text>')
    s.append(f'<line x1="{X(1/3):.1f}" y1="{T-6}" x2="{X(1/3):.1f}" y2="{yb}" stroke="var(--muted)" stroke-width="1.5" stroke-dasharray="6 4"/><text x="{X(1/3)+4:.1f}" y="{T-10}" class="ax">{E(f["chance"])}</text>')
    s.append(f'<text x="{(Lm+W-R)/2:.0f}" y="{Hh-8}" text-anchor="middle" class="ax">{E(f["x"])}</text>')
    for i,(lab,vals) in enumerate(zip(rows,A6_VALS)):
        y=T+gh*i+4
        s.append(f'<text x="{Lm-10}" y="{y+24}" text-anchor="end" class="lbl">{E(lab)}</text>')
        for j,(v,c) in enumerate(zip(vals,A6_COLS)):
            yy=y+j*16; s.append(f'<rect x="{X(0):.1f}" y="{yy}" width="{X(v)-X(0):.1f}" height="13" fill="var(--{c})"/><text x="{X(v)+6:.1f}" y="{yy+10}" class="ax">{pct(v)}</text>')
    return ''.join(s)+'</svg>'
def tex_fig_a6(L,cap):
    f=L['fig']['A6']; sp='\\,' if L['lang'] in ('de','fr') else ''; rows=[r or f['rows_last'] for r in A6_ROWS]; n=len(rows)
    yl=','.join('{'+esc_text(r)+'}' for r in reversed(rows))
    plots=''
    for j,(key,c) in enumerate(zip(['mass','speed','both'],A6_COLS)):
        co=' '.join(f'({v[j]*100:.1f},{n-i})' for i,v in enumerate(A6_VALS))
        plots+=r"\addplot[fill=fr"+c+r",draw=none] coordinates {"+co+r"};\addlegendentry{"+esc_text(f[key])+"}\n"
    return r"""\begin{figure}[tb]\centering
\begin{tikzpicture}\begin{axis}[width=\columnwidth,height=7.4cm,xbar=0.6pt,bar width=3.6pt,xmin=0,xmax=100,ymin=0.4,ymax="""+str(n+0.6)+r""",
ytick={1,...,"""+str(n)+r"""},yticklabels={"""+yl+r"""},xtick={0,25,50,75,100},xticklabels={0"""+sp+r"""\%,25"""+sp+r"""\%,50"""+sp+r"""\%,75"""+sp+r"""\%,100"""+sp+r"""\%},
xlabel={"""+esc_text(f['x'])+r"""},grid=major,grid style={line width=.2pt,draw=gray!30},legend style={font=\scriptsize,at={(0.5,1.02)},anchor=south,legend columns=3,draw=none},reverse legend=false,
tick label style={font=\scriptsize},label style={font=\footnotesize}]
"""+plots+r"""\draw[black,dashed] (axis cs:33.3,0.4) -- (axis cs:33.3,"""+str(n+0.6)+r""");
\end{axis}\end{tikzpicture}
\caption{"""+cap+r"""}\end{figure}
"""
TEXFIG['A6']=tex_fig_a6; SVGFIG['A6']=svg_a6

# ---------------- figura A7 (primeiro contato) ----------------
A7_Q=[2,3,10,30]; A7_C10=[0.636,0.726,0.779,0.827]; A7_C30=[0.532,0.581,0.642,0.629]; A7_NEAR=[0.480,0.488,0.500,0.512]
def svg_a7(L):
    f=L['fig']['A7']; W,Hh,Lm,R,T,B=640,340,62,30,44,52
    X=lambda q:Lm+(W-Lm-R)*math.log(q/2)/math.log(15); Y=lambda v:Hh-B-(Hh-B-T)*(v-0.4)/0.5
    pct=lambda v:(num(f'{v*100:.0f}',L)+(' %' if L['lang'] in ('de','fr') else '%'))
    s=[f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="{E(f["aria"])}">']
    for j,(k,c) in enumerate([('c10','hot'),('c30','accent'),('near','ink')]):
        x0=Lm+j*180; s.append(f'<rect x="{x0}" y="8" width="12" height="12" fill="var(--{c})"/><text x="{x0+18}" y="18" class="lbl">{E(f[k])}</text>')
    for v in [0.4,0.5,0.6,0.7,0.8,0.9]: s.append(f'<line x1="{Lm}" y1="{Y(v):.1f}" x2="{W-R}" y2="{Y(v):.1f}" stroke="var(--line)"/><text x="{Lm-8}" y="{Y(v)+4:.1f}" text-anchor="end" class="ax">{pct(v)}</text>')
    for q in A7_Q: s.append(f'<text x="{X(q):.1f}" y="{Hh-B+18}" text-anchor="middle" class="ax">{q}</text>')
    s.append(f'<line x1="{Lm}" y1="{Y(0.5):.1f}" x2="{W-R}" y2="{Y(0.5):.1f}" stroke="var(--muted)" stroke-width="1.5" stroke-dasharray="6 4"/><text x="{W-R-4}" y="{Y(0.5)-6:.1f}" text-anchor="end" class="ax">{E(f["chance"])}</text>')
    s.append(f'<text x="{(Lm+W-R)/2:.0f}" y="{Hh-10}" text-anchor="middle" class="ax">{E(f["x"])}</text><text x="{Lm}" y="{T-10}" class="ax">{E(f["y"])}</text>')
    for vals,c in [(A7_C10,'hot'),(A7_C30,'accent'),(A7_NEAR,'ink')]:
        s.append(f'<polyline points="{" ".join(f"{X(q):.1f},{Y(v):.1f}" for q,v in zip(A7_Q,vals))}" fill="none" stroke="var(--{c})" stroke-width="2.2"/>')
        s.append(''.join(f'<circle cx="{X(q):.1f}" cy="{Y(v):.1f}" r="3.6" fill="var(--{c})"/>' for q,v in zip(A7_Q,vals)))
    return ''.join(s)+'</svg>'
def tex_fig_a7(L,cap):
    f=L['fig']['A7']; sep='{,}' if L['decimal']==',' else '.'; sp='\\,' if L['lang'] in ('de','fr') else ''
    pl=''
    for vals,c,mk,k in [(A7_C10,'hot','*','c10'),(A7_C30,'accent','square*','c30'),(A7_NEAR,'ink','triangle*','near')]:
        pl+=r"\addplot[color=fr"+c+",mark="+mk+r",mark size=1.5pt,thick] coordinates {"+' '.join(f'({q},{v*100:.1f})' for q,v in zip(A7_Q,vals))+r"};\addlegendentry{"+esc_text(f[k])+"}\n"
    return r"""\begin{figure}[tb]\centering
\begin{tikzpicture}\begin{axis}[width=\columnwidth,height=5.8cm,xmode=log,xmin=1.8,xmax=34,ymin=40,ymax=90,
xtick={2,3,10,30},xticklabels={2,3,10,30},ytick={40,50,60,70,80,90},yticklabels={40"""+sp+r"""\%,50"""+sp+r"""\%,60"""+sp+r"""\%,70"""+sp+r"""\%,80"""+sp+r"""\%,90"""+sp+r"""\%},
xlabel={"""+esc_text(f['x'])+r"""},ylabel={"""+esc_text(f['y'])+r"""},grid=major,grid style={line width=.2pt,draw=gray!30},legend pos=north west,legend style={font=\scriptsize,draw=none,fill=white,fill opacity=0.9,text opacity=1},
tick label style={font=\scriptsize},label style={font=\footnotesize}]
\addplot[black,dashed,domain=1.8:34,forget plot] {50};
"""+pl+r"""\end{axis}\end{tikzpicture}
\caption{"""+cap+r"""}\end{figure}
"""
TEXFIG['A7']=tex_fig_a7; SVGFIG['A7']=svg_a7

# ---------------- figura A7 (primeiro contato) ----------------
A7_Q=[2,3,10,30]; A7_C10=[0.636,0.726,0.779,0.827]; A7_C30=[0.532,0.581,0.642,0.629]; A7_NEAR=[0.480,0.488,0.500,0.512]
def svg_a7(L):
    f=L['fig']['A7']; W,Hh,Lm,R,T,B=640,340,62,30,44,52
    X=lambda q:Lm+(W-Lm-R)*math.log(q/2)/math.log(15); Y=lambda v:Hh-B-(Hh-B-T)*(v-0.4)/0.5
    pct=lambda v:(num(f'{v*100:.0f}',L)+(' %' if L['lang'] in ('de','fr') else '%'))
    s=[f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="{E(f["aria"])}">']
    for j,(k,c) in enumerate([('c10','hot'),('c30','accent'),('near','ink')]):
        x0=Lm+j*180; s.append(f'<rect x="{x0}" y="8" width="12" height="12" fill="var(--{c})"/><text x="{x0+18}" y="18" class="lbl">{E(f[k])}</text>')
    for v in [0.4,0.5,0.6,0.7,0.8,0.9]: s.append(f'<line x1="{Lm}" y1="{Y(v):.1f}" x2="{W-R}" y2="{Y(v):.1f}" stroke="var(--line)"/><text x="{Lm-8}" y="{Y(v)+4:.1f}" text-anchor="end" class="ax">{pct(v)}</text>')
    for q in A7_Q: s.append(f'<text x="{X(q):.1f}" y="{Hh-B+18}" text-anchor="middle" class="ax">{q}</text>')
    s.append(f'<line x1="{Lm}" y1="{Y(0.5):.1f}" x2="{W-R}" y2="{Y(0.5):.1f}" stroke="var(--muted)" stroke-width="1.5" stroke-dasharray="6 4"/><text x="{W-R-4}" y="{Y(0.5)-6:.1f}" text-anchor="end" class="ax">{E(f["chance"])}</text>')
    s.append(f'<text x="{(Lm+W-R)/2:.0f}" y="{Hh-10}" text-anchor="middle" class="ax">{E(f["x"])}</text><text x="{Lm}" y="{T-10}" class="ax">{E(f["y"])}</text>')
    for vals,c in [(A7_C10,'hot'),(A7_C30,'accent'),(A7_NEAR,'ink')]:
        s.append(f'<polyline points="{" ".join(f"{X(q):.1f},{Y(v):.1f}" for q,v in zip(A7_Q,vals))}" fill="none" stroke="var(--{c})" stroke-width="2.2"/>')
        s.append(''.join(f'<circle cx="{X(q):.1f}" cy="{Y(v):.1f}" r="3.6" fill="var(--{c})"/>' for q,v in zip(A7_Q,vals)))
    return ''.join(s)+'</svg>'
def tex_fig_a7(L,cap):
    f=L['fig']['A7']; sp='\\,' if L['lang'] in ('de','fr') else ''
    pl=''
    for vals,c,mk,k in [(A7_C10,'hot','*','c10'),(A7_C30,'accent','square*','c30'),(A7_NEAR,'ink','triangle*','near')]:
        pl+=r"\addplot[color=fr"+c+",mark="+mk+r",mark size=1.5pt,thick] coordinates {"+' '.join(f'({q},{v*100:.1f})' for q,v in zip(A7_Q,vals))+r"};\addlegendentry{"+esc_text(f[k])+"}\n"
    return r"""\begin{figure}[tb]\centering
\begin{tikzpicture}\begin{axis}[width=\columnwidth,height=5.8cm,xmode=log,xmin=1.8,xmax=34,ymin=40,ymax=90,
xtick={2,3,10,30},xticklabels={2,3,10,30},ytick={40,50,60,70,80,90},yticklabels={40"""+sp+r"""\%,50"""+sp+r"""\%,60"""+sp+r"""\%,70"""+sp+r"""\%,80"""+sp+r"""\%,90"""+sp+r"""\%},
xlabel={"""+esc_text(f['x'])+r"""},ylabel={"""+esc_text(f['y'])+r"""},grid=major,grid style={line width=.2pt,draw=gray!30},legend pos=north west,legend style={font=\scriptsize,draw=none,fill=white,fill opacity=0.9,text opacity=1},
tick label style={font=\scriptsize},label style={font=\footnotesize}]
\addplot[black,dashed,domain=1.8:34,forget plot] {50};
"""+pl+r"""\end{axis}\end{tikzpicture}
\caption{"""+cap+r"""}\end{figure}
"""
TEXFIG['A7']=tex_fig_a7; SVGFIG['A7']=svg_a7

# ---------------- figura A8 (sobrevivência) ----------------
A8_T=[1,2,3,5,10,20,30,50,100,200,300,500,1000,2000,3000,5000,10000]
A8_S={('eq','rest'):[0.9593,0.9253,0.9013,0.8667,0.764,0.612,0.498,0.3673,0.1633,0.0793,0.054,0.0387,0.018,0.0093,0.006,0.0053,0.0033],
('eq','vir'):[0.8467,0.8333,0.8113,0.7653,0.6793,0.5607,0.4747,0.3593,0.2333,0.1493,0.122,0.0993,0.078,0.0587,0.054,0.048,0.042],
('l10','rest'):[0.876,0.7833,0.7173,0.6033,0.4267,0.27,0.192,0.1153,0.0633,0.0367,0.0307,0.02,0.0147,0.0113,0.0087,0.0053,0.0047],
('l10','vir'):[0.7533,0.7053,0.6667,0.6007,0.4807,0.3593,0.2907,0.216,0.1533,0.1047,0.0867,0.0707,0.0567,0.0453,0.038,0.034,0.028],
('h10','rest'):[0.7127,0.5893,0.5087,0.398,0.2573,0.1427,0.0993,0.0653,0.0447,0.0253,0.0187,0.0147,0.008,0.0047,0.004,0.0033,None],
('h10','vir'):[0.6353,0.5433,0.492,0.408,0.3033,0.24,0.2047,0.1687,0.1287,0.1067,0.1027,0.0893,0.0827,0.074,0.0713,0.068,0.0633]}
A8_C={'eq':'ink','l10':'accent','h10':'hot'}
def svg_a8(L):
    f=L['fig']['A8']; W,Hh,Lm,R,T,B=640,380,64,24,52,52
    X=lambda t:Lm+(W-Lm-R)*math.log10(t)/4; Y=lambda s:T+(Hh-B-T)*(-math.log10(s))/3
    s=[f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="{E(f["aria"])}">']
    for j,k in enumerate(['eq','l10','h10']):
        x0=Lm+j*150; s.append(f'<rect x="{x0}" y="8" width="12" height="12" fill="var(--{A8_C[k]})"/><text x="{x0+18}" y="18" class="lbl">{E(f[k])}</text>')
    x0=Lm+450; s.append(f'<line x1="{x0}" y1="14" x2="{x0+22}" y2="14" stroke="var(--muted)" stroke-width="2"/><text x="{x0+26}" y="18" class="ax">{E(f["rest"])}</text>')
    s.append(f'<line x1="{x0}" y1="32" x2="{x0+22}" y2="32" stroke="var(--muted)" stroke-width="2" stroke-dasharray="5 4"/><text x="{x0+26}" y="36" class="ax">{E(f["vir"])}</text>')
    for e,lab in zip([0,-1,-2,-3],['1','0'+L['decimal']+'1','0'+L['decimal']+'01','0'+L['decimal']+'001']):
        yy=Y(10**e); s.append(f'<line x1="{Lm}" y1="{yy:.1f}" x2="{W-R}" y2="{yy:.1f}" stroke="var(--line)"/><text x="{Lm-8}" y="{yy+4:.1f}" text-anchor="end" class="ax">{lab}</text>')
    for e in range(5):
        xx=X(10**e); s.append(f'<line x1="{xx:.1f}" y1="{T}" x2="{xx:.1f}" y2="{Hh-B}" stroke="var(--line)"/><text x="{xx:.1f}" y="{Hh-B+18}" text-anchor="middle" class="ax">{10**e if e<4 else "10⁴"}</text>')
    s.append(f'<text x="{(Lm+W-R)/2:.0f}" y="{Hh-10}" text-anchor="middle" class="ax">{E(f["x"])}</text><text x="{Lm}" y="{T-10}" class="ax">{E(f["y"])}</text>')
    for (k,e),vals in A8_S.items():
        pts=' '.join(f'{X(t):.1f},{Y(v):.1f}' for t,v in zip(A8_T,vals) if v)
        s.append(f'<polyline points="{pts}" fill="none" stroke="var(--{A8_C[k]})" stroke-width="2.2"{" stroke-dasharray=\"6 4\"" if e=="vir" else ""}/>')
    return ''.join(s)+'</svg>'
def tex_fig_a8(L,cap):
    f=L['fig']['A8']; sep='{,}' if L['decimal']==',' else '.'
    pl=''
    for (k,e),vals in A8_S.items():
        sty=('dashed,' if e=='vir' else '')
        co=' '.join(f'({t},{v})' for t,v in zip(A8_T,vals) if v)
        leg=(r"\addlegendentry{"+esc_text(f[k])+"}" if e=='rest' else '')
        pl+=r"\addplot[color=fr"+A8_C[k]+","+sty+r"thick"+("" if e=='rest' else ",forget plot")+r"] coordinates {"+co+"};"+leg+"\n"
    return r"""\begin{figure}[tb]\centering
\begin{tikzpicture}\begin{axis}[width=\columnwidth,height=6.4cm,xmode=log,ymode=log,xmin=1,xmax=10000,ymin=0.001,ymax=1.05,
xtick={1,10,100,1000,10000},ytick={0.001,0.01,0.1,1},yticklabels={0"""+sep+r"""001,0"""+sep+r"""01,0"""+sep+r"""1,1},
xlabel={"""+esc_text(f['x'])+r"""},ylabel={"""+esc_text(f['y'])+r"""},grid=major,grid style={line width=.2pt,draw=gray!30},legend pos=south west,legend style={font=\scriptsize,draw=none,fill=white,fill opacity=0.9,text opacity=1},
tick label style={font=\scriptsize},label style={font=\footnotesize}]
"""+pl+r"""\end{axis}\end{tikzpicture}
\caption{"""+cap+r"""}\end{figure}
"""
TEXFIG['A8']=tex_fig_a8; SVGFIG['A8']=svg_a8

# ---------------- figura A9 (excentricidade: medido x teorias) ----------------
A9_MEAS=[0.013,0.032,0.046,0.058,0.072,0.086,0.100,0.108,0.137,0.347]
A9_SL=[0.003,0.009,0.017,0.026,0.039,0.056,0.078,0.111,0.171,0.490]
A9_FL=[0.005,0.015,0.026,0.037,0.050,0.066,0.086,0.114,0.164,0.436]
A9_FA=[0.011,0.032,0.048,0.059,0.069,0.080,0.094,0.107,0.139,0.361]
def svg_a9(L):
    f=L['fig']['A9']; W,Hh,Lm,R,T,B=640,380,64,24,62,52
    X=lambda v:Lm+(W-Lm-R)*v; Y=lambda p:Hh-B-(Hh-B-T)*p/0.5
    s=[f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="{E(f["aria"])}">']
    s.append(f'<rect x="{Lm}" y="8" width="12" height="12" fill="var(--muted)" opacity="0.55"/><text x="{Lm+18}" y="18" class="lbl">{E(f["meas"])}</text>')
    s.append(f'<line x1="{Lm+300}" y1="14" x2="{Lm+322}" y2="14" stroke="var(--accent)" stroke-width="2.6"/><text x="{Lm+328}" y="18" class="lbl">{E(f["fa"])}</text>')
    s.append(f'<line x1="{Lm}" y1="36" x2="{Lm+22}" y2="36" stroke="var(--hot)" stroke-width="2.2" stroke-dasharray="6 4"/><text x="{Lm+28}" y="40" class="lbl">{E(f["sl"])}</text>')
    s.append(f'<line x1="{Lm+300}" y1="36" x2="{Lm+322}" y2="36" stroke="var(--ink)" stroke-width="1.8" stroke-dasharray="2 3"/><text x="{Lm+328}" y="40" class="lbl">{E(f["flux"])}</text>')
    for p in [0,0.1,0.2,0.3,0.4,0.5]:
        yy=Y(p); s.append(f'<line x1="{Lm}" y1="{yy:.1f}" x2="{W-R}" y2="{yy:.1f}" stroke="var(--line)"/><text x="{Lm-8}" y="{yy+4:.1f}" text-anchor="end" class="ax">{num(f"{p:.1f}",L)}</text>')
    for v in [0,0.2,0.4,0.6,0.8,1.0]:
        s.append(f'<text x="{X(v):.1f}" y="{Hh-B+18}" text-anchor="middle" class="ax">{num(f"{v:.1f}",L)}</text>')
    for i,m in enumerate(A9_MEAS):
        s.append(f'<rect x="{X(i/10)+3:.1f}" y="{Y(m):.1f}" width="{X(0.1)-X(0)-6:.1f}" height="{Y(0)-Y(m):.1f}" fill="var(--muted)" opacity="0.55"/>')
    for data,sty in ((A9_SL,'stroke="var(--hot)" stroke-width="2.2" stroke-dasharray="6 4"'),(A9_FL,'stroke="var(--ink)" stroke-width="1.8" stroke-dasharray="2 3"'),(A9_FA,'stroke="var(--accent)" stroke-width="2.6"')):
        pts=' '.join(f'{X(i/10+0.05):.1f},{Y(v):.1f}' for i,v in enumerate(data))
        s.append(f'<polyline points="{pts}" fill="none" {sty}/>')
    s.append(f'<text x="{(Lm+W-R)/2:.0f}" y="{Hh-10}" text-anchor="middle" class="ax">{E(f["x"])}</text><text x="{Lm}" y="{T-8}" class="ax">{E(f["y"])}</text>')
    return ''.join(s)+'</svg>'
def tex_fig_a9(L,cap):
    f=L['fig']['A9']; sep='{,}' if L['decimal']==',' else '.'
    c=lambda d:' '.join(f'({i/10+0.05:.2f},{v})' for i,v in enumerate(d))
    return r"""\begin{figure}[tb]\centering
\begin{tikzpicture}\begin{axis}[width=\columnwidth,height=6.4cm,xmin=0,xmax=1,ymin=0,ymax=0.52,
xtick={0,0.2,0.4,0.6,0.8,1},xticklabels={0,0"""+sep+r"""2,0"""+sep+r"""4,0"""+sep+r"""6,0"""+sep+r"""8,1},ytick={0,0.1,0.2,0.3,0.4,0.5},yticklabels={0,0"""+sep+r"""1,0"""+sep+r"""2,0"""+sep+r"""3,0"""+sep+r"""4,0"""+sep+r"""5},
xlabel={"""+esc_text(f['x'])+r"""},ylabel={"""+esc_text(f['y'])+r"""},grid=major,grid style={line width=.2pt,draw=gray!30},legend pos=north west,legend style={font=\scriptsize,draw=none,fill=white,fill opacity=0.9,text opacity=1},
tick label style={font=\scriptsize},label style={font=\footnotesize}]
\addplot[ybar,bar width=0.07,fill=gray!45,draw=none,area legend] coordinates {"""+c(A9_MEAS)+r"""};\addlegendentry{"""+esc_text(f['meas'])+r"""}
\addplot[sharp plot,color=fraccent,very thick] coordinates {"""+c(A9_FA)+r"""};\addlegendentry{"""+esc_text(f['fa'])+r"""}
\addplot[sharp plot,color=frhot,thick,dashed] coordinates {"""+c(A9_SL)+r"""};\addlegendentry{"""+esc_text(f['sl'])+r"""}
\addplot[sharp plot,color=frink,thick,dotted] coordinates {"""+c(A9_FL)+r"""};\addlegendentry{"""+esc_text(f['flux'])+r"""}
\end{axis}\end{tikzpicture}
\caption{"""+cap+r"""}\end{figure}
"""
TEXFIG['A9']=tex_fig_a9; SVGFIG['A9']=svg_a9

# ---------------- figura A10 (mapas de fase e orientacao) ----------------
def _a10_png(L):
    import io, numpy as _np
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as _plt
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch
    f = L['fig']['A10']; G = _np.load('a10_grids.npz')
    cols = ['#d9d9d9', '#111318', '#E8480C', '#F5B700', '#1D3FD8', '#7a7a7a']
    _plt.rcParams.update({'font.family': 'serif', 'font.size': 8})
    fig, axs = _plt.subplots(1, 4, figsize=(7.2, 2.35))
    for ax, k, t in zip(axs, 'abcd', f['panels']):
        ax.imshow(G[k].T, origin='lower', extent=[0, 360, 0, 360], cmap=ListedColormap(cols), vmin=-1, vmax=4, interpolation='nearest')
        ax.set_title(t, fontsize=7.5); ax.set_xticks([0, 180, 360]); ax.set_yticks([0, 180, 360]); ax.tick_params(labelsize=6.5)
        ax.set_xlabel(f['x'], fontsize=7)
    axs[0].set_ylabel(f['y'], fontsize=7)
    hs = [Patch(color=cols[1], label=f['chaos']), Patch(color=cols[2], label=f['ex0']), Patch(color=cols[3], label=f['ex1']), Patch(color=cols[4], label=f['fly']), Patch(color=cols[5], label=f['bound'])]
    fig.legend(handles=hs, loc='lower center', ncol=5, fontsize=7, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    buf = io.BytesIO(); fig.savefig(buf, format='png', dpi=220); _plt.close(fig); return buf.getvalue()
def svg_a10(L):
    import base64
    b = base64.b64encode(_a10_png(L)).decode()
    return f'<svg viewBox="0 0 1584 517" role="img" aria-label="{E(L["fig"]["A10"]["aria"])}"><image href="data:image/png;base64,{b}" x="0" y="0" width="1584" height="517"/></svg>'
def tex_fig_a10(L, cap):
    fn = f"a10_{L['lang']}.png"
    open('texbuild/' + fn, 'wb').write(_a10_png(L))
    return r"""\begin{figure*}[!t]\centering
\includegraphics[width=\textwidth]{""" + fn + r"""}
\caption{""" + cap + r"""}\end{figure*}
"""
TEXFIG['A10'] = tex_fig_a10; SVGFIG['A10'] = svg_a10

# ---------------- figura A11 (probabilidade de troca na primeira passagem) ----------------
A11_X = [0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 10.0]
A11_S = {'0.1': [0.09, 0.31, 0.58, 0.88, 0.87, 0.83, 0.75], '0.25': [0.01, 0.24, 0.50, 0.94, 0.92, 0.85, 0.78],
         '0.5': [0.00, 0.08, 0.40, 0.95, 0.97, 0.96, 0.87], '1': [0.00, 0.01, 0.37, 0.84, 1.00, 0.99, 0.96]}
A11_C = {'0.1': 'hot', '0.25': 'accent', '0.5': 'ink', '1': 'muted'}
A11_TC = {'0.1': 'frhot', '0.25': 'fraccent', '0.5': 'frink', '1': 'gray'}
A11_MK = {'0.1': 'o', '0.25': 's', '0.5': 'd', '1': 't'}
def _a11_fit(r): return 1 / (1 + (0.52 / r) ** 1.9)
def svg_a11(L):
    f = L['fig']['A11']; W, Hh, Lm, R, T, B = 640, 380, 64, 24, 56, 52
    X = lambda v: Lm + (W - Lm - R) * (math.log10(v) + 1) / 2; Y = lambda p: Hh - B - (Hh - B - T) * p
    s = [f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="{E(f["aria"])}">']
    for j, k in enumerate(A11_S):
        x0 = Lm + j * 118; s.append(f'<circle cx="{x0+6}" cy="14" r="5" fill="var(--{A11_C[k]})"/><text x="{x0+16}" y="18" class="lbl">{E(f["mb"].replace("{v}", num(k, L)))}</text>')
    s.append(f'<line x1="{Lm+480}" y1="14" x2="{Lm+502}" y2="14" stroke="var(--ink)" stroke-width="2" stroke-dasharray="6 4"/><text x="{Lm+508}" y="18" class="ax">{E(f["fit"])}</text>')
    for p in [0, 0.25, 0.5, 0.75, 1]:
        yy = Y(p); s.append(f'<line x1="{Lm}" y1="{yy:.1f}" x2="{W-R}" y2="{yy:.1f}" stroke="var(--line)"/><text x="{Lm-8}" y="{yy+4:.1f}" text-anchor="end" class="ax">{num(f"{p:.2f}", L)}</text>')
    for v in [0.1, 0.25, 0.5, 1, 2, 4, 10]:
        s.append(f'<text x="{X(v):.1f}" y="{Hh-B+18}" text-anchor="middle" class="ax">{num(str(v), L)}</text>')
    pts = ' '.join(f'{X(v):.1f},{Y(_a11_fit(v)):.1f}' for v in [0.1 * 1.06 ** i for i in range(90) if 0.1 * 1.06 ** i <= 4.0])
    s.append(f'<polyline points="{pts}" fill="none" stroke="var(--ink)" stroke-width="2" stroke-dasharray="6 4"/>')
    for k, vals in A11_S.items():
        p2 = ' '.join(f'{X(v):.1f},{Y(p):.1f}' for v, p in zip(A11_X, vals))
        s.append(f'<polyline points="{p2}" fill="none" stroke="var(--{A11_C[k]})" stroke-width="1.2" opacity="0.6"/>')
        for v, p in zip(A11_X, vals): s.append(f'<circle cx="{X(v):.1f}" cy="{Y(p):.1f}" r="4.2" fill="var(--{A11_C[k]})"/>')
    s.append(f'<text x="{(Lm+W-R)/2:.0f}" y="{Hh-10}" text-anchor="middle" class="ax">{E(f["x"])}</text><text x="{Lm}" y="{T-12}" class="ax">{E(f["y"])}</text>')
    return ''.join(s) + '</svg>'
def tex_fig_a11(L, cap):
    f = L['fig']['A11']; sep = '{,}' if L['decimal'] == ',' else '.'
    pl = ''
    for k, vals in A11_S.items():
        co = ' '.join(f'({v},{p})' for v, p in zip(A11_X, vals))
        pl += r"\addplot[color=" + A11_TC[k] + r",mark=*,mark size=1.6pt,thin] coordinates {" + co + "};\\addlegendentry{" + esc_text(f['mb'].replace('{v}', k.replace('.', ',') if L['decimal'] == ',' else k)) + "}\n"
    fit = ' '.join(f'({0.1*1.06**i:.4f},{_a11_fit(0.1*1.06**i):.4f})' for i in range(90) if 0.1 * 1.06 ** i <= 4.0)
    pl += r"\addplot[color=frink,thick,dashed] coordinates {" + fit + "};\\addlegendentry{" + esc_text(f['fit']) + "}\n"
    return r"""\begin{figure}[tb]\centering
\begin{tikzpicture}\begin{axis}[width=\columnwidth,height=6.4cm,xmode=log,xmin=0.08,xmax=12,ymin=-0.02,ymax=1.05,
xtick={0.1,0.25,0.5,1,2,4,10},xticklabels={0"""+sep+r"""1,0"""+sep+r"""25,0"""+sep+r"""5,1,2,4,10},ytick={0,0.25,0.5,0.75,1},yticklabels={0,0"""+sep+r"""25,0"""+sep+r"""5,0"""+sep+r"""75,1},
xlabel={"""+esc_text(f['x'])+r"""},ylabel={"""+esc_text(f['y'])+r"""},grid=major,grid style={line width=.2pt,draw=gray!30},legend pos=south east,legend style={font=\scriptsize,draw=none,fill=white,fill opacity=0.9,text opacity=1},
tick label style={font=\scriptsize},label style={font=\footnotesize}]
"""+pl+r"""\end{axis}\end{tikzpicture}
\caption{"""+cap+r"""}\end{figure}
"""
TEXFIG['A11'] = tex_fig_a11; SVGFIG['A11'] = svg_a11

# ---------------- figura A12 (absortividade: formula contra medida) ----------------
def _a12(): 
    import json as _j; return _j.load(open('a12_points.json'))
def svg_a12(L):
    f = L['fig']['A12']; D = _a12(); W, Hh, Lm, R, T, B = 520, 460, 64, 24, 40, 52
    X = lambda v: Lm + (W - Lm - R) * v; Y = lambda v: Hh - B - (Hh - B - T) * v
    s = [f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="{E(f["aria"])}">']
    for v in [0, 0.25, 0.5, 0.75, 1]:
        s.append(f'<line x1="{Lm}" y1="{Y(v):.1f}" x2="{W-R}" y2="{Y(v):.1f}" stroke="var(--line)"/><text x="{Lm-8}" y="{Y(v)+4:.1f}" text-anchor="end" class="ax">{num(f"{v:.2f}", L)}</text>')
        s.append(f'<text x="{X(v):.1f}" y="{Hh-B+18}" text-anchor="middle" class="ax">{num(f"{v:.2f}", L)}</text>')
    s.append(f'<line x1="{X(0):.1f}" y1="{Y(0):.1f}" x2="{X(1):.1f}" y2="{Y(1):.1f}" stroke="var(--ink)" stroke-width="1.5" stroke-dasharray="6 4"/>')
    for a, b in zip(D['meas'], D['f']): s.append(f'<circle cx="{X(a):.1f}" cy="{Y(min(b,1)):.1f}" r="2.4" fill="var(--accent)" opacity="0.55"/>')
    s.append(f'<text x="{(Lm+W-R)/2:.0f}" y="{Hh-10}" text-anchor="middle" class="ax">{E(f["x"])}</text><text x="{Lm}" y="{T-12}" class="ax">{E(f["y"])}</text>')
    return ''.join(s) + '</svg>'
def tex_fig_a12(L, cap):
    f = L['fig']['A12']; D = _a12(); sep = '{,}' if L['decimal'] == ',' else '.'
    co = ' '.join(f'({a},{min(b,1)})' for a, b in zip(D['meas'], D['f']))
    t = '{0,0' + sep + '25,0' + sep + '5,0' + sep + '75,1}'
    return r"""\begin{figure}[tb]\centering
\begin{tikzpicture}\begin{axis}[width=0.9\columnwidth,height=0.9\columnwidth,xmin=0,xmax=1,ymin=0,ymax=1,xtick={0,0.25,0.5,0.75,1},ytick={0,0.25,0.5,0.75,1},xticklabels=""" + t + r""",yticklabels=""" + t + r""",
xlabel={""" + esc_text(f['x']) + r"""},ylabel={""" + esc_text(f['y']) + r"""},grid=major,grid style={line width=.2pt,draw=gray!30},tick label style={font=\scriptsize},label style={font=\footnotesize}]
\addplot[only marks,mark=*,mark size=0.7pt,color=fraccent,opacity=0.6] coordinates {""" + co + r"""};
\addplot[frink,dashed,domain=0:1] {x};
\end{axis}\end{tikzpicture}
\caption{""" + cap + r"""}\end{figure}
"""
TEXFIG['A12'] = tex_fig_a12; SVGFIG['A12'] = svg_a12

# ---------------- figura A13 (muro de excentricidade em funcao de m_s/mu) ----------------
def _a13():
    import json as _j; return _j.load(open('a13_points.json'))
A13_C = {'11': 'accent', '12': 'hot'}; A13_TC = {'11': 'fraccent', '12': 'frhot'}
def svg_a13(L):
    f = L['fig']['A13']; D = _a13(); W, Hh, Lm, R, T, B = 640, 380, 64, 24, 56, 52
    X = lambda v: Lm + (W - Lm - R) * v / 1.7; Y = lambda p: Hh - B - (Hh - B - T) * p
    s = [f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="{E(f["aria"])}">']
    for j, k in enumerate(('11', '12')):
        x0 = Lm + j * 260; s.append(f'<circle cx="{x0+6}" cy="14" r="5" fill="var(--{A13_C[k]})"/><text x="{x0+16}" y="18" class="lbl">{E(f["s" + k])}</text>')
    for p in [0, 0.25, 0.5, 0.75, 1]:
        yy = Y(p); s.append(f'<line x1="{Lm}" y1="{yy:.1f}" x2="{W-R}" y2="{yy:.1f}" stroke="var(--line)"/><text x="{Lm-8}" y="{yy+4:.1f}" text-anchor="end" class="ax">{num(f"{p:.2f}", L)}</text>')
    for v in [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5]:
        s.append(f'<text x="{X(v):.1f}" y="{Hh-B+18}" text-anchor="middle" class="ax">{num(f"{v:g}", L)}</text>')
    for k in ('11', '12'):
        pts = D[k]
        s.append(f'<polyline points="{" ".join(f"{X(r):.1f},{Y(m):.1f}" for r, m, lo, hi in pts)}" fill="none" stroke="var(--{A13_C[k]})" stroke-width="1.4" opacity="0.7"/>')
        for r, m, lo, hi in pts:
            s.append(f'<line x1="{X(r):.1f}" y1="{Y(lo):.1f}" x2="{X(r):.1f}" y2="{Y(hi):.1f}" stroke="var(--{A13_C[k]})" stroke-width="1.4"/><circle cx="{X(r):.1f}" cy="{Y(m):.1f}" r="4.2" fill="var(--{A13_C[k]})"/>')
    s.append(f'<text x="{(Lm+W-R)/2:.0f}" y="{Hh-10}" text-anchor="middle" class="ax">{E(f["x"])}</text><text x="{Lm}" y="{T-12}" class="ax">{E(f["y"])}</text>')
    return ''.join(s) + '</svg>'
def tex_fig_a13(L, cap):
    f = L['fig']['A13']; D = _a13(); sep = '{,}' if L['decimal'] == ',' else '.'
    pl = ''
    for k in ('11', '12'):
        co = ' '.join(f'({r},{m}) +- (0,0)' for r, m, lo, hi in D[k])
        co = ' '.join(f'({r},{m}) += (0,{hi-m:.3f}) -= (0,{m-lo:.3f})' for r, m, lo, hi in D[k])
        pl += r"\addplot[color=" + A13_TC[k] + r",mark=*,mark size=1.6pt,thin,error bars/.cd,y dir=both,y explicit] coordinates {" + co + "};\\addlegendentry{" + esc_text(f['s' + k]) + "}\n"
    t = lambda vs: ','.join(v.replace('.', sep) for v in vs)
    return r"""\begin{figure}[tb]\centering
\begin{tikzpicture}\begin{axis}[width=\columnwidth,height=6.2cm,xmin=0,xmax=1.7,ymin=-0.03,ymax=1.03,
xtick={0,0.25,0.5,0.75,1,1.25,1.5},xticklabels={""" + t(['0', '0.25', '0.5', '0.75', '1', '1.25', '1.5']) + r"""},ytick={0,0.25,0.5,0.75,1},yticklabels={""" + t(['0', '0.25', '0.5', '0.75', '1']) + r"""},
xlabel={""" + esc_text(f['x']) + r"""},ylabel={""" + esc_text(f['y']) + r"""},grid=major,grid style={line width=.2pt,draw=gray!30},legend pos=north east,legend style={font=\scriptsize,draw=none,fill=white,fill opacity=0.9,text opacity=1},
tick label style={font=\scriptsize},label style={font=\footnotesize}]
""" + pl + r"""\end{axis}\end{tikzpicture}
\caption{""" + cap + r"""}\end{figure}
"""
TEXFIG['A13'] = tex_fig_a13; SVGFIG['A13'] = svg_a13

def _a14():
    import json as _j; return _j.load(open('a14_points.json'))
A14_C = {'v10': 'hot', 'v11': 'accent'}; A14_TC = {'v10': 'frhot', 'v11': 'fraccent'}
def svg_a14(L):
    f = L['fig']['A14']; D = _a14(); W, Hh, Lm, R, T, B = 640, 380, 64, 24, 56, 52; ym = 0.05
    X = lambda v: Lm + (W - Lm - R) * v; Y = lambda p: Hh - B - (Hh - B - T) * (p + ym) / (2 * ym)
    s = [f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="{E(f["aria"])}">']
    for j, k in enumerate(('v11', 'v10')):
        x0 = Lm + j * 200; s.append(f'<line x1="{x0}" y1="14" x2="{x0+18}" y2="14" stroke="var(--{A14_C[k]})" stroke-width="2.4"/><text x="{x0+24}" y="18" class="lbl">{E(f["s_" + k])}</text>')
    x0 = Lm + 400; s.append(f'<line x1="{x0}" y1="14" x2="{x0+18}" y2="14" stroke="var(--muted)" stroke-width="1.4" stroke-dasharray="5 4"/><text x="{x0+24}" y="18" class="lbl">{E(f["s_crit"])}</text>')
    for p in [-0.04, -0.02, 0, 0.02, 0.04]:
        yy = Y(p); s.append(f'<line x1="{Lm}" y1="{yy:.1f}" x2="{W-R}" y2="{yy:.1f}" stroke="var(--line)"/><text x="{Lm-8}" y="{yy+4:.1f}" text-anchor="end" class="ax">{num(f"{p:.2f}", L)}</text>')
    for v in [0, 0.2, 0.4, 0.6, 0.8, 1]:
        s.append(f'<text x="{X(v):.1f}" y="{Hh-B+18}" text-anchor="middle" class="ax">{num(f"{v:g}", L)}</text>')
    for c in (D['crit'], -D['crit']):
        s.append(f'<line x1="{Lm}" y1="{Y(c):.1f}" x2="{W-R}" y2="{Y(c):.1f}" stroke="var(--muted)" stroke-width="1.4" stroke-dasharray="5 4"/>')
    for k in ('v10', 'v11'):
        s.append(f'<polyline points="{" ".join(f"{X(e):.1f},{Y(d):.1f}" for e, d in D[k])}" fill="none" stroke="var(--{A14_C[k]})" stroke-width="2.4"/>')
    s.append(f'<text x="{(Lm+W-R)/2:.0f}" y="{Hh-10}" text-anchor="middle" class="ax">{E(f["x"])}</text><text x="{Lm}" y="{T-12}" class="ax">{E(f["y"])}</text>')
    return ''.join(s) + '</svg>'
def tex_fig_a14(L, cap):
    f = L['fig']['A14']; D = _a14(); sep = '{,}' if L['decimal'] == ',' else '.'
    t = lambda vs: ','.join(v.replace('.', sep) for v in vs)
    pl = ''
    for k in ('v11', 'v10'):
        pl += r"\addplot[color=" + A14_TC[k] + r",very thick] coordinates {" + ' '.join(f'({e},{d})' for e, d in D[k]) + "};\\addlegendentry{" + esc_text(f['s_' + k]) + "}\n"
    c = D['crit']
    pl += r"\addplot[color=gray,dashed,thick,domain=0:1] {" + str(c) + "};\\addlegendentry{" + esc_text(f['s_crit']) + "}\n"
    pl += r"\addplot[color=gray,dashed,thick,domain=0:1,forget plot] {" + str(-c) + "};\n"
    return r"""\begin{figure}[tb]\centering
\begin{tikzpicture}\begin{axis}[width=\columnwidth,height=6.2cm,xmin=0,xmax=1,ymin=-0.05,ymax=0.05,
xtick={0,0.2,0.4,0.6,0.8,1},xticklabels={""" + t(['0', '0.2', '0.4', '0.6', '0.8', '1']) + r"""},ytick={-0.04,-0.02,0,0.02,0.04},yticklabels={""" + t(['-0.04', '-0.02', '0', '0.02', '0.04']) + r"""},
scaled y ticks=false,xlabel={""" + esc_text(f['x']) + r"""},ylabel={""" + esc_text(f['y']) + r"""},grid=major,grid style={line width=.2pt,draw=gray!30},legend pos=south east,legend style={font=\scriptsize,draw=none,fill=white,fill opacity=0.9,text opacity=1},
tick label style={font=\scriptsize},label style={font=\footnotesize}]
""" + pl + r"""\end{axis}\end{tikzpicture}
\caption{""" + cap + r"""}\end{figure}
"""
TEXFIG['A14'] = tex_fig_a14; SVGFIG['A14'] = svg_a14
