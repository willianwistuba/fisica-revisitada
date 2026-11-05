SITE='https://fisica-revisitada.vercel.app'
DATE='2026-11-03'
LANGS=['pt','en','de','fr']
BABEL={'pt':'brazilian','en':'english','de':'ngerman','fr':'french'}
HREFLANG={'pt':'pt-BR','en':'en','de':'de','fr':'fr'}
PREFIX={'pt':'','en':'/en','de':'/de','fr':'/fr'}
ROUTES={
 'pt':{'art':'artigos','notes':'notas','method':'metodo','code':'codigo'},
 'en':{'art':'articles','notes':'notes','method':'method','code':'code'},
 'de':{'art':'artikel','notes':'notizen','method':'methode','code':'code'},
 'fr':{'art':'articles','notes':'notes','method':'methode','code':'code'},
}
def url(lang,kind,slug=None):
    p=PREFIX[lang]
    if kind=='home': return p+'/'
    if kind=='series': return p+'/series/tres-corpos/'
    if kind=='art': return f"{p}/{ROUTES[lang]['art']}/{slug}/"
    if kind=='pdf': return f"/pdf/{slug}.pdf" if lang=='pt' else f"/pdf/{lang}/{slug}.pdf"
    return f"{p}/{ROUTES[lang][kind]}/"

ARTS=[
 dict(slug='por-que-nao-ha-solucao-geral', src='a1.html', part=1, code='FR-TC-01', refs=[
   ('H. Bruns, Über die Integrale des Vielkörper-Problems, Acta Math. 11, 25 (1887).','https://doi.org/10.1007/BF02612319'),
   ('H. Poincaré, Sur le problème des trois corps et les équations de la dynamique, Acta Math. 13, 1 (1890).','https://doi.org/10.1007/BF02392505'),
   ('K. F. Sundman, Mémoire sur le problème des trois corps, Acta Math. 36, 105 (1912).','https://doi.org/10.1007/BF02422379'),
   ('A. Chenciner and R. Montgomery, A remarkable periodic solution of the three-body problem in the case of equal masses, Ann. Math. 152, 881 (2000).','https://arxiv.org/abs/math/0011268'),
   ('N. C. Stone and N. W. C. Leigh, A statistical solution to the chaotic, non-hierarchical three-body problem, Nature 576, 406 (2019).','https://doi.org/10.1038/s41586-019-1833-8'),
   ('M. Šuvakov and V. Dmitrašinović, Three classes of Newtonian three-body planar periodic orbits, Phys. Rev. Lett. 110, 114301 (2013).','https://doi.org/10.1103/PhysRevLett.110.114301'),
   ('F. Diacu, The solution of the n-body problem, Math. Intelligencer 18, 66 (1996).','https://doi.org/10.1007/BF03024313'),
   ('R. Montgomery, The three-body problem and the shape sphere, Amer. Math. Monthly 122, 299 (2015).','https://arxiv.org/abs/1402.0841'),
 ]),
 dict(slug='estabilizacao-vibracional-binario-interno', src='a2.html', part=2, code='FR-TC-02', refs=[
   ('P. L. Kapitza, Dynamic stability of a pendulum when its point of suspension vibrates, Zh. Eksp. Teor. Fiz. 21, 588 (1951).',None),
   ('L. D. Landau and E. M. Lifshitz, Mechanics, 3rd ed. (Pergamon, Oxford, 1976), §30.',None),
   ('A. R. Dzhanoev, A. Loskutov, J. E. Howard, and M. A. F. Sanjuán, Stabilization of chaotic behavior in the restricted three-body problem, Int. J. Bifurcation Chaos 17 (2007).','https://doi.org/10.1142/S0218127407019433'),
   ('Data-driven stabilisation of unstable periodic orbits of the three-body problem, arXiv:2507.08630 (2025).','https://arxiv.org/abs/2507.08630'),
   ('S. Doolin and K. M. Blundell, The dynamics and stability of circumbinary orbits, Mon. Not. R. Astron. Soc. 418, 2656 (2011).','https://arxiv.org/abs/1108.4144'),
   ('E. Ott, C. Grebogi, and J. A. Yorke, Controlling chaos, Phys. Rev. Lett. 64, 1196 (1990).','https://doi.org/10.1103/PhysRevLett.64.1196'),
   ('R. Montgomery, The three-body problem and the shape sphere, Amer. Math. Monthly 122, 299 (2015).','https://arxiv.org/abs/1402.0841'),
   ('E. J. Routh, On Laplace\'s three particles, with a supplement on the stability of steady motion, Proc. London Math. Soc. 6, 86 (1875).',None),
 ]),
 dict(slug='mapa-de-estabilidade-poucos-corpos', src='a3.html', part=3, code='FR-TC-03', refs=[
   ('J. Gascheau, Examen d\'une classe d\'équations différentielles et application à un cas particulier du problème des trois corps, C. R. Acad. Sci. Paris 16, 393 (1843).',None),
   ('E. J. Routh, On Laplace\'s three particles, with a supplement on the stability of steady motion, Proc. London Math. Soc. 6, 86 (1875).',None),
   ('A. Deprit and A. Deprit-Bartholomé, Stability of the triangular Lagrangian points, Astron. J. 72, 173 (1967).','https://doi.org/10.1086/110213'),
   ('J. C. Maxwell, On the Stability of the Motion of Saturn\'s Rings (Macmillan, Cambridge, 1859).',None),
   ('R. Moeckel, Linear stability of relative equilibria with a dominant mass, J. Dyn. Differ. Equ. 6, 37 (1994).','https://doi.org/10.1007/BF02219187'),
   ('R. A. Mardling and S. J. Aarseth, Tidal interactions in star cluster simulations, Mon. Not. R. Astron. Soc. 321, 398 (2001).','https://doi.org/10.1046/j.1365-8711.2001.03974.x'),
   ('N. G. Chetaev, The Stability of Motion (Pergamon, Oxford, 1961); W. Thomson and P. G. Tait, Treatise on Natural Philosophy (Cambridge University Press, 1879).',None),
 ]),
 dict(slug='limiar-universal-de-acoplamento', src='a4.html', part=4, code='FR-TC-04', refs=[
   ('E. J. Routh, On Laplace\'s three particles, with a supplement on the stability of steady motion, Proc. London Math. Soc. 6, 86 (1875).',None),
   ('J. C. Maxwell, On the Stability of the Motion of Saturn\'s Rings (Macmillan, Cambridge, 1859).',None),
   ('R. A. Mardling and S. J. Aarseth, Tidal interactions in star cluster simulations, Mon. Not. R. Astron. Soc. 321, 398 (2001).','https://doi.org/10.1046/j.1365-8711.2001.03974.x'),
   ('B. V. Chirikov, A universal instability of many-dimensional oscillator systems, Phys. Rep. 52, 263 (1979).','https://doi.org/10.1016/0370-1573(79)90023-1'),
   ('R. A. Mardling, Resonance, chaos and stability: the three-body problem in astrophysics, in The Cambridge N-Body Lectures, Lecture Notes in Physics 760 (Springer, Berlin, 2008), p. 59.','https://doi.org/10.1007/978-1-4020-8431-7_3'),
   ('Lagrange vs. Lyapunov stability of hierarchical triple systems, arXiv:2209.08487 (2022).','https://arxiv.org/abs/2209.08487'),
   ('V. I. Arnold, Small denominators and problems of stability of motion in classical and celestial mechanics, Russ. Math. Surv. 18, 85 (1963).','https://doi.org/10.1070/RM1963v018n06ABEH001143'),
   ('W. W. M. da Cunha, Física Revisitada, Technical Note FR-TC-03 (2026).',SITE+'/artigos/mapa-de-estabilidade-poucos-corpos/'),
 ]),
 dict(slug='sinais-da-ejecao', src='a5.html', part=5, code='FR-TC-05', refs=[
   ('M. Valtonen and H. Karttunen, The Three-Body Problem (Cambridge University Press, Cambridge, 2006).','https://doi.org/10.1017/CBO9780511616006'),
   ('N. C. Stone and N. W. C. Leigh, A statistical solution to the chaotic, non-hierarchical three-body problem, Nature 576, 406 (2019).','https://doi.org/10.1038/s41586-019-1833-8'),
   ('J. J. Monaghan, A statistical theory of the disruption of three-body systems. I. Low angular momentum, Mon. Not. R. Astron. Soc. 176, 63 (1976).','https://doi.org/10.1093/mnras/176.1.63'),
   ('S. Mikkola and S. J. Aarseth, An implementation of N-body chain regularization, Celest. Mech. Dyn. Astron. 57, 439 (1993).','https://doi.org/10.1007/BF00695714'),
   ('S. Mikkola and K. Tanikawa, Algorithmic regularization of the few-body problem, Mon. Not. R. Astron. Soc. 310, 745 (1999).','https://doi.org/10.1046/j.1365-8711.1999.02982.x'),
   ('D. C. Heggie, Binary evolution in stellar dynamics, Mon. Not. R. Astron. Soc. 173, 729 (1975).','https://doi.org/10.1093/mnras/173.3.729'),
 ]),
 dict(slug='velocidade-e-ejecao', src='a6.html', part=6, code='FR-TC-06', refs=[
   ('D. C. Heggie, Binary evolution in stellar dynamics, Mon. Not. R. Astron. Soc. 173, 729 (1975).','https://doi.org/10.1093/mnras/173.3.729'),
   ('J. G. Hills, Encounters between binary and single stars and their effect on the dynamical evolution of stellar systems, Astron. J. 80, 809 (1975).','https://doi.org/10.1086/111815'),
   ('M. Valtonen and H. Karttunen, The Three-Body Problem (Cambridge University Press, Cambridge, 2006).','https://doi.org/10.1017/CBO9780511616006'),
   ('S. Mikkola and S. J. Aarseth, An implementation of N-body chain regularization, Celest. Mech. Dyn. Astron. 57, 439 (1993).','https://doi.org/10.1007/BF00695714'),
   ('S. Mikkola and K. Tanikawa, Algorithmic regularization of the few-body problem, Mon. Not. R. Astron. Soc. 310, 745 (1999).','https://doi.org/10.1046/j.1365-8711.1999.02982.x'),
   ('W. W. M. da Cunha, Física Revisitada, Technical Note FR-TC-05 (2026).',SITE+'/artigos/sinais-da-ejecao/'),
 ]),
 dict(slug='primeiro-contato', src='a7.html', part=7, code='FR-TC-07', refs=[
   ('E. J. Routh, On Laplace\'s three particles, with a supplement on the stability of steady motion, Proc. London Math. Soc. 6, 86 (1875).',None),
   ('D. C. Heggie, Binary evolution in stellar dynamics, Mon. Not. R. Astron. Soc. 173, 729 (1975).','https://doi.org/10.1093/mnras/173.3.729'),
   ('J. G. Hills, Encounters between binary and single stars and their effect on the dynamical evolution of stellar systems, Astron. J. 80, 809 (1975).','https://doi.org/10.1086/111815'),
   ('M. Valtonen and H. Karttunen, The Three-Body Problem (Cambridge University Press, Cambridge, 2006).','https://doi.org/10.1017/CBO9780511616006'),
   ('S. Mikkola and K. Tanikawa, Algorithmic regularization of the few-body problem, Mon. Not. R. Astron. Soc. 310, 745 (1999).','https://doi.org/10.1046/j.1365-8711.1999.02982.x'),
   ('W. W. M. da Cunha, Física Revisitada, Technical Note FR-TC-05 (2026).',SITE+'/artigos/sinais-da-ejecao/'),
   ('W. W. M. da Cunha, Física Revisitada, Technical Note FR-TC-03 (2026).',SITE+'/artigos/mapa-de-estabilidade-poucos-corpos/'),
 ]),
 dict(slug='meia-vida', src='a8.html', part=8, code='FR-TC-08', refs=[
   ('V. V. Orlov, A. V. Rubinov, and I. I. Shevchenko, Disruption of three-body gravitational systems: lifetime statistics, Mon. Not. R. Astron. Soc. (2010), arXiv:1004.2506.','https://arxiv.org/abs/1004.2506'),
   ('V. Manwadkar, A. A. Trani, and N. W. C. Leigh, Chaos and Lévy flights in the three-body problem, Mon. Not. R. Astron. Soc. 497, 3694 (2020).','https://doi.org/10.1093/mnras/staa1722'),
   ('M. Valtonen and H. Karttunen, The Three-Body Problem (Cambridge University Press, Cambridge, 2006).','https://doi.org/10.1017/CBO9780511616006'),
   ('S. Mikkola and K. Tanikawa, Algorithmic regularization of the few-body problem, Mon. Not. R. Astron. Soc. 310, 745 (1999).','https://doi.org/10.1046/j.1365-8711.1999.02982.x'),
   ('W. W. M. da Cunha, Física Revisitada, Technical Note FR-TC-05 (2026).',SITE+'/artigos/sinais-da-ejecao/'),
 ]),
 dict(slug='memoria-e-acaso', src='a9.html', part=9, code='FR-TC-09', refs=[
   ('N. C. Stone and N. W. C. Leigh, A statistical solution to the chaotic, non-hierarchical three-body problem, Nature 576, 406 (2019).','https://doi.org/10.1038/s41586-019-1833-8'),
   ('B. Kol, Flux-based statistical prediction of three-body outcomes, Celest. Mech. Dyn. Astron. 133, 17 (2021).','https://doi.org/10.1007/s10569-021-10015-x'),
   ('V. Manwadkar, B. Kol, A. A. Trani, and N. W. C. Leigh, Testing the flux-based statistical prediction of the three-body problem, Mon. Not. R. Astron. Soc. 506, 692 (2021).','https://doi.org/10.1093/mnras/stab1689'),
   ('V. Manwadkar, A. A. Trani, and B. Kol, Measurement of three-body chaotic absorptivity predicts chaotic outcome distribution, Celest. Mech. Dyn. Astron. 136, 4 (2024).','https://doi.org/10.1007/s10569-023-10174-z'),
   ('J. J. Monaghan, A statistical theory of the disruption of three-body systems. I. Low angular momentum, Mon. Not. R. Astron. Soc. 176, 63 (1976).','https://doi.org/10.1093/mnras/176.1.63'),
   ('T. A. Agekyan and Zh. P. Anosova, A study of the dynamics of triple systems by means of statistical sampling, Sov. Astron. 11, 1006 (1968).',None),
   ('S. Mikkola and K. Tanikawa, Algorithmic regularization of the few-body problem, Mon. Not. R. Astron. Soc. 310, 745 (1999).','https://doi.org/10.1046/j.1365-8711.1999.02982.x'),
   ('M. Valtonen and H. Karttunen, The Three-Body Problem (Cambridge University Press, Cambridge, 2006).','https://doi.org/10.1017/CBO9780511616006'),
   ('W. W. M. da Cunha, Física Revisitada, Technical Note FR-TC-05 (2026).',SITE+'/artigos/sinais-da-ejecao/'),
   ('Y. Dandekar, E. Springer, S. Zard, A. A. Trani, B. Kol, and O. Birnholtz, Planar three-body problem: theoretical predictions and simulation results, arXiv:2608.30414 (2026).','https://arxiv.org/abs/2608.30414'),
   ('D. Meylakh, N. C. Stone, and N. W. C. Leigh, Intermediate states in chaotic triple evolution and applications to black hole merger statistics, arXiv:2606.11294 (2026).','https://arxiv.org/abs/2606.11294'),
 ]),
 dict(slug='evolucao-e-absortividade', src='a10.html', part=10, code='FR-TC-10', refs=[
   ('B. Kol, Flux-based statistical prediction of three-body outcomes, Celest. Mech. Dyn. Astron. 133, 17 (2021).','https://doi.org/10.1007/s10569-021-10015-x'),
   ('V. Manwadkar, B. Kol, A. A. Trani, and N. W. C. Leigh, Testing the flux-based statistical prediction of the three-body problem, Mon. Not. R. Astron. Soc. 506, 692 (2021).','https://doi.org/10.1093/mnras/stab1689'),
   ('V. Manwadkar, A. A. Trani, and B. Kol, Measurement of three-body chaotic absorptivity predicts chaotic outcome distribution, Celest. Mech. Dyn. Astron. 136, 4 (2024).','https://doi.org/10.1007/s10569-023-10174-z'),
   ('Y. Dandekar, E. Springer, S. Zard, A. A. Trani, B. Kol, and O. Birnholtz, Planar three-body problem: theoretical predictions and simulation results, arXiv:2608.30414 (2026).','https://arxiv.org/abs/2608.30414'),
   ('D. Meylakh, N. C. Stone, and N. W. C. Leigh, Intermediate states in chaotic triple evolution and applications to black hole merger statistics, arXiv:2606.11294 (2026).','https://arxiv.org/abs/2606.11294'),
   ('D. C. Heggie, Binary evolution in stellar dynamics, Mon. Not. R. Astron. Soc. 173, 729 (1975).','https://doi.org/10.1093/mnras/173.3.729'),
   ('C. Grebogi, S. W. McDonald, E. Ott, and J. A. Yorke, Final state sensitivity: an obstruction to predictability, Phys. Lett. A 99, 415 (1983).','https://doi.org/10.1016/0375-9601(83)90945-3'),
   ('S. Mikkola and K. Tanikawa, Algorithmic regularization of the few-body problem, Mon. Not. R. Astron. Soc. 310, 745 (1999).','https://doi.org/10.1046/j.1365-8711.1999.02982.x'),
   ('W. W. M. da Cunha, Física Revisitada, Technical Note FR-TC-09 (2026).',SITE+'/artigos/memoria-e-acaso/'),
 ]),
 dict(slug='regras-de-massas', src='a11.html', part=11, code='FR-TC-11', refs=[
   ('B. Kol, Flux-based statistical prediction of three-body outcomes, Celest. Mech. Dyn. Astron. 133, 17 (2021).','https://doi.org/10.1007/s10569-021-10015-x'),
   ('V. Manwadkar, B. Kol, A. A. Trani, and N. W. C. Leigh, Testing the flux-based statistical prediction of the three-body problem, Mon. Not. R. Astron. Soc. 506, 692 (2021).','https://doi.org/10.1093/mnras/stab1689'),
   ('D. C. Heggie, P. Hut, and S. L. W. McMillan, Binary-single-star scattering. VII. Hard binary exchange cross sections for arbitrary mass ratios, Astrophys. J. 467, 359 (1996).','https://doi.org/10.1086/177611'),
   ('P. Hut and J. N. Bahcall, Binary-single star scattering. I. Numerical experiments for equal masses, Astrophys. J. 268, 319 (1983).','https://doi.org/10.1086/160956'),
   ('M. Valtonen and H. Karttunen, The Three-Body Problem (Cambridge University Press, Cambridge, 2006).','https://doi.org/10.1017/CBO9780511616006'),
   ('N. C. Stone and N. W. C. Leigh, A statistical solution to the chaotic, non-hierarchical three-body problem, Nature 576, 406 (2019).','https://doi.org/10.1038/s41586-019-1833-8'),
   ('S. Mikkola and K. Tanikawa, Algorithmic regularization of the few-body problem, Mon. Not. R. Astron. Soc. 310, 745 (1999).','https://doi.org/10.1046/j.1365-8711.1999.02982.x'),
   ('W. W. M. da Cunha, Física Revisitada, Technical Note FR-TC-05 (2026).',SITE+'/artigos/sinais-da-ejecao/'),
   ('W. W. M. da Cunha, Física Revisitada, Technical Note FR-TC-10 (2026).',SITE+'/artigos/evolucao-e-absortividade/'),
 ]),
 dict(slug='formula-da-absortividade', src='a12.html', part=12, code='FR-TC-12', refs=[
   ('B. Kol, Flux-based statistical prediction of three-body outcomes, Celest. Mech. Dyn. Astron. 133, 17 (2021).','https://doi.org/10.1007/s10569-021-10015-x'),
   ('N. C. Stone and N. W. C. Leigh, A statistical solution to the chaotic, non-hierarchical three-body problem, Nature 576, 406 (2019).','https://doi.org/10.1038/s41586-019-1833-8'),
   ('V. Manwadkar, A. A. Trani, and B. Kol, Measurement of three-body chaotic absorptivity predicts chaotic outcome distribution, Celest. Mech. Dyn. Astron. 136, 4 (2024).','https://doi.org/10.1007/s10569-023-10174-z'),
   ('W. W. M. da Cunha, Física Revisitada, Technical Note FR-TC-09 (2026).',SITE+'/artigos/memoria-e-acaso/'),
   ('W. W. M. da Cunha, Física Revisitada, Technical Note FR-TC-10 (2026).',SITE+'/artigos/evolucao-e-absortividade/'),
   ('W. W. M. da Cunha, Física Revisitada, Technical Note FR-TC-11 (2026).',SITE+'/artigos/regras-de-massas/'),
 ]),
 dict(slug='muro-de-excentricidade', src='a13.html', part=13, code='FR-TC-13', refs=[
   ('B. Kol, Flux-based statistical prediction of three-body outcomes, Celest. Mech. Dyn. Astron. 133, 17 (2021).','https://doi.org/10.1007/s10569-021-10015-x'),
   ('V. Manwadkar, A. A. Trani, and B. Kol, Measurement of three-body chaotic absorptivity predicts chaotic outcome distribution, Celest. Mech. Dyn. Astron. 136, 4 (2024).','https://doi.org/10.1007/s10569-023-10174-z'),
   ('W. W. M. da Cunha, Física Revisitada, Technical Note FR-TC-12 (2026).',SITE+'/artigos/formula-da-absortividade/'),
   ('W. W. M. da Cunha, Física Revisitada, Technical Note FR-TC-10 (2026).',SITE+'/artigos/evolucao-e-absortividade/'),
   ('S. Mikkola and K. Tanikawa, Algorithmic regularization of the few-body problem, Mon. Not. R. Astron. Soc. 310, 745 (1999).','https://doi.org/10.1046/j.1365-8711.1999.02982.x'),
   ('Y. Dandekar, E. Springer, S. Zard, A. A. Trani, B. Kol, and O. Birnholtz, Planar three-body problem: theoretical predictions and simulation results, arXiv:2608.30414 (2026).','https://arxiv.org/abs/2608.30414'),
   ('S. A. Astakhov, E. A. Lee, and D. Farrelly, Formation of Kuiper-belt binaries through multiple chaotic scattering encounters with low-mass intruders, Mon. Not. R. Astron. Soc. 360, 401 (2005).','https://arxiv.org/abs/astro-ph/0504060'),
   ('C. D. Murray and S. F. Dermott, Solar System Dynamics (Cambridge University Press, Cambridge, 1999).','https://doi.org/10.1017/CBO9781139174817'),
   ('Y. B. Ginat and H. B. Perets, Analytical, statistical approximate solution of dissipative and nondissipative binary-single stellar encounters, Phys. Rev. X 11, 031020 (2021).','https://doi.org/10.1103/PhysRevX.11.031020'),
   ('Y. B. Ginat et al., Dynamical evolution of quasi-hierarchical triples, arXiv:2509.02685 (2025).','https://arxiv.org/abs/2509.02685'),
   ('W. W. M. da Cunha, Física Revisitada, Technical Note FR-TC-09 (2026).',SITE+'/artigos/memoria-e-acaso/'),
 ]),
 dict(slug='formula-posta-a-prova', src='a14.html', part=14, code='FR-TC-14', date_iso='2026-11-05', version_num='1', refs=[
   ('B. Kol, Flux-based statistical prediction of three-body outcomes, Celest. Mech. Dyn. Astron. 133, 17 (2021).','https://doi.org/10.1007/s10569-021-10015-x'),
   ('V. Manwadkar, A. A. Trani, and B. Kol, Measurement of three-body chaotic absorptivity predicts chaotic outcome distribution, Celest. Mech. Dyn. Astron. 136, 4 (2024).','https://doi.org/10.1007/s10569-023-10174-z'),
   ('W. W. M. da Cunha, Física Revisitada, Technical Note FR-TC-13 (2026).',SITE+'/artigos/muro-de-excentricidade/'),
   ('W. W. M. da Cunha, Física Revisitada, Technical Note FR-TC-12 (2026).',SITE+'/artigos/formula-da-absortividade/'),
   ('S. Mikkola and K. Tanikawa, Algorithmic regularization of the few-body problem, Mon. Not. R. Astron. Soc. 310, 745 (1999).','https://doi.org/10.1046/j.1365-8711.1999.02982.x'),
   ('B. Efron and R. J. Tibshirani, An Introduction to the Bootstrap (Chapman and Hall/CRC, New York, 1993).','https://doi.org/10.1201/9780429246593'),
   ('S. Holm, A simple sequentially rejective multiple test procedure, Scand. J. Stat. 6, 65 (1979).','https://www.jstor.org/stable/4615733'),
   ('T. Hastie, R. Tibshirani, and J. Friedman, The Elements of Statistical Learning, 2nd ed. (Springer, New York, 2009).','https://doi.org/10.1007/978-0-387-84858-7'),
 ]),
]
