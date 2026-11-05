const {lagrange,survive,PERTS}=require('./core.js');
const T=1500, P3=PERTS.slice(0,3);
const med=a=>a.slice().sort((x,y)=>x-y)[Math.floor(a.length/2)];
const fmtT=t=>t>=T?'∞':t.toFixed(0);
for(const mu of [0.015,0.022,0.025,0.03]){
  const c=med(P3.map(p=>survive(()=>lagrange([1,mu,mu],{pert:p}),0.002,T).t));
  let line=`mu ${mu} controle ${fmtT(c)} | par no corpo grande:`;
  for(const ab of [0.005,0.01,0.02,0.04,0.07,0.1,0.15,0.2]){
    const Pb=2*Math.PI*Math.sqrt(ab**3/1), dt=Math.min(0.002,Pb/50);
    const r=med(P3.map(p=>survive(()=>lagrange([1,mu,mu],{pert:p,binaryAt:0,ab}),dt,T).t));
    line+=` ${ab}:${fmtT(r)}`;
  }
  console.log(line);
}
