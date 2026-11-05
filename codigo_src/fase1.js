const {lagrange,survive,PERTS}=require('./core.js');
// Fase 1: um corpo grande (1) e dois pequenos (mu): reproduzir a regra de Routh (limite teórico mu ~ 0,0198)
const T=1500;
for(const mu of [0.005,0.01,0.015,0.018,0.0195,0.0205,0.022,0.025,0.03,0.05,0.1,0.3,1]){
  const r=PERTS.map(p=>survive(()=>lagrange([1,mu,mu],{pert:p}),0.002,T));
  const routh=(1+2*mu)**2 > 27*(2*mu+mu*mu);
  console.log('mu',mu.toString().padEnd(6),'Routh diz', routh?'ESTÁVEL ':'instável','| sobrevivência:',r.map(x=>x.t>=T?'∞':x.t.toFixed(0)).join(' '),'| deformação máx',Math.max(...r.map(x=>x.maxd)).toFixed(3));
}
