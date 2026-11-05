const {lagrange,survive,PERTS}=require('./core.js');
const T=1500;
const stableLag=(ms)=>PERTS.every(p=>survive(()=>lagrange(ms,{pert:p}),0.002,T).t>=T);
function bisect(f, lo, hi, it=9){ // f(lo)=true(estável), f(hi)=false
  for(let i=0;i<it;i++){ const mid=Math.sqrt(lo*hi); if(f(mid)) lo=mid; else hi=mid; } return Math.sqrt(lo*hi); }
const out=[];
// Família A: Lagrange com 1 grande e dois pequenos de razão k (mu, k*mu)
// Atenção: a bissecção supõe monotonicidade e pode parar numa ilha ressonante (ver nota 03); confira com varredura.
for(const k of [1,0.25,4]){
  const thr=bisect(mu=>stableLag([1,mu,k*mu]),0.002,0.2);
  const m2=thr, m3=k*thr;
  const eps=Math.max(m3/(1+m2), m2/(1+m3));
  out.push(`Lagrange 1:${fmt(m2)}:${fmt(m3)} | limiar simulado mu=${thr.toFixed(4)} | acoplamento ${(100*eps).toFixed(2)}%`);
}
function fmt(x){return x.toFixed(4)}
console.log(out.join('\n'));
