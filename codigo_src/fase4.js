// Fase 4: atrito (gel girando junto com o sistema) sobre o triângulo de Lagrange ESTÁVEL (mu=0,01)
const {lagrange,PERTS}=require('./core.js');
function runDrag(mu, gam, pert, T){
  const {s}=lagrange([1,mu,mu],{pert}); const Mt=1+2*mu, w=Math.sqrt(Mt);
  const n=s.n, ax=new Float64Array(n), ay=new Float64Array(n);
  const acc=()=>{ax.fill(0);ay.fill(0);for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){const dx=s.x[j]-s.x[i],dy=s.y[j]-s.y[i],r2=dx*dx+dy*dy,f=1/(r2*Math.sqrt(r2));ax[i]+=s.m[j]*dx*f;ay[i]+=s.m[j]*dy*f;ax[j]-=s.m[i]*dx*f;ay[j]-=s.m[i]*dy*f;}
    for(let i=1;i<n;i++){ ax[i]+=-gam*(s.vx[i]-(-w*s.y[i])); ay[i]+=-gam*(s.vy[i]-(w*s.x[i])); } };
  acc(); const dt=0.002; let t=0,k=0, d0=null;
  const side=()=>{const d=[[0,1],[1,2],[0,2]].map(([i,j])=>Math.hypot(s.x[i]-s.x[j],s.y[i]-s.y[j]));const m=(d[0]+d[1]+d[2])/3;return Math.max(...d.map(v=>Math.abs(v/m-1)));};
  while(t<T){ for(let i=0;i<n;i++){s.vx[i]+=ax[i]*dt/2;s.vy[i]+=ay[i]*dt/2;s.x[i]+=s.vx[i]*dt;s.y[i]+=s.vy[i]*dt;} acc(); for(let i=0;i<n;i++){s.vx[i]+=ax[i]*dt/2;s.vy[i]+=ay[i]*dt/2;} t+=dt;
    if(++k%50===0 && side()>0.3) return t; }
  return T;
}
const T=3000;
for(const g of [0,1e-4,1e-3,1e-2]) console.log('atrito',g,'| sobrevivência:',[[1e-3,0,0],[0,1e-3,0]].map(p=>{const t=runDrag(0.01,g,p,T);return t>=T?'∞':t.toFixed(0);}).join(' '));
