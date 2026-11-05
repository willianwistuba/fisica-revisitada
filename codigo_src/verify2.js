// anel: limiar simulado e acoplamento de maré
function ringRun(n, mu, pert, T){
  const R=1; let S=0; for(let k=1;k<n;k++) S+=1/Math.sin(Math.PI*k/n); S/=4;
  const v=Math.sqrt((1+mu*S)/R); const m=[1],x=[0],y=[0],vx=[0],vy=[0];
  for(let i=0;i<n;i++){const a=2*Math.PI*i/n;m.push(mu);x.push(Math.cos(a));y.push(Math.sin(a));vx.push(-v*Math.sin(a));vy.push(v*Math.cos(a));}
  x[1]+=pert; vy[2]+=pert; let px=0,py=0; for(let i=0;i<=n;i++){px+=m[i]*vx[i];py+=m[i]*vy[i];} vx[0]-=px;vy[0]-=py;
  const N=n+1,ax=new Float64Array(N),ay=new Float64Array(N);
  const acc=()=>{ax.fill(0);ay.fill(0);for(let i=0;i<N;i++)for(let j=i+1;j<N;j++){const dx=x[j]-x[i],dy=y[j]-y[i],r2=dx*dx+dy*dy+1e-12,f=1/(r2*Math.sqrt(r2));ax[i]+=m[j]*dx*f;ay[i]+=m[j]*dy*f;ax[j]-=m[i]*dx*f;ay[j]-=m[i]*dy*f;}};
  acc(); const dt=0.002; let t=0,k=0;
  while(t<T){for(let i=0;i<N;i++){vx[i]+=ax[i]*dt/2;vy[i]+=ay[i]*dt/2;x[i]+=vx[i]*dt;y[i]+=vy[i]*dt;}acc();for(let i=0;i<N;i++){vx[i]+=ax[i]*dt/2;vy[i]+=ay[i]*dt/2;}t+=dt;
    if(++k%50===0){const ang=[];for(let i=1;i<=n;i++)ang.push(Math.atan2(y[i]-y[0],x[i]-x[0]));ang.sort((a,b)=>a-b);let w=0;for(let i=0;i<n;i++){const g=(i<n-1?ang[i+1]-ang[i]:ang[0]+2*Math.PI-ang[i]);w=Math.max(w,Math.abs(g/(2*Math.PI/n)-1));}if(w>0.3)return t;}}
  return T;
}
function ringEps(n,mu){ let ax=0,ay=0; for(let j=1;j<n;j++){const a=2*Math.PI*j/n, xj=Math.cos(a), yj=Math.sin(a); const dx=xj-1, dy=yj, d=Math.hypot(dx,dy); ax+=mu*(dx/d**3 - xj); ay+=mu*(dy/d**3 - yj);} return Math.hypot(ax,ay)/(1+mu); }
const T=600;
for(const n of [7,8,10]){
  const lim=2.298/n**3; let last=null;
  for(const f of [0.9,1.0,1.1,1.2,1.3,1.4,1.5]){ const ok=[1e-4,-1e-4,3e-4].every(p=>ringRun(n,f*lim,p,T)>=T); if(ok) last=f; else break; }
  console.log(`anel n=${n}: estável até ${last}× o limite de Maxwell | acoplamento de maré no limiar ${(100*ringEps(n,last*lim)).toFixed(2)}%`);
}
