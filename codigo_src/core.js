// integrador leapfrog genérico + montagem de triângulo de Lagrange com massas quaisquer
function sys(bodies){ const n=bodies.length; return {n,t:0,m:bodies.map(b=>b.m),x:bodies.map(b=>b.x),y:bodies.map(b=>b.y),vx:bodies.map(b=>b.vx),vy:bodies.map(b=>b.vy),ax:new Float64Array(n),ay:new Float64Array(n)}; }
function acc(s){ s.ax.fill(0); s.ay.fill(0); for(let i=0;i<s.n;i++)for(let j=i+1;j<s.n;j++){ const dx=s.x[j]-s.x[i],dy=s.y[j]-s.y[i],r2=dx*dx+dy*dy+1e-10,f=1/(r2*Math.sqrt(r2)); s.ax[i]+=s.m[j]*dx*f; s.ay[i]+=s.m[j]*dy*f; s.ax[j]-=s.m[i]*dx*f; s.ay[j]-=s.m[i]*dy*f; } }
function step(s,dt){ for(let i=0;i<s.n;i++){ s.vx[i]+=s.ax[i]*dt/2; s.vy[i]+=s.ay[i]*dt/2; s.x[i]+=s.vx[i]*dt; s.y[i]+=s.vy[i]*dt; } acc(s); for(let i=0;i<s.n;i++){ s.vx[i]+=s.ax[i]*dt/2; s.vy[i]+=s.ay[i]*dt/2; } s.t+=dt; }
// triângulo equilátero de lado 1, girando rígido em torno do centro de massa
// opts.binaryAt = índice do vértice substituído por um par de separação ab (fração do lado), retro
function lagrange(ms, opts={}){
  const P=[[0,0],[1,0],[0.5,Math.sqrt(3)/2]], Mt=ms[0]+ms[1]+ms[2];
  const cx=(ms[0]*P[0][0]+ms[1]*P[1][0]+ms[2]*P[2][0])/Mt, cy=(ms[0]*P[0][1]+ms[1]*P[1][1]+ms[2]*P[2][1])/Mt;
  const w=Math.sqrt(Mt); // lado 1, G=1
  const b=[];
  for(let i=0;i<3;i++){ const x=P[i][0]-cx, y=P[i][1]-cy; b.push({m:ms[i],x,y,vx:-w*y,vy:w*x}); }
  if(opts.pert){ b[1].x+=opts.pert[0]; b[1].y+=opts.pert[1]; b[2].vx+=opts.pert[2]; }
  if(opts.binaryAt!==undefined){
    const k=opts.binaryAt, B=b[k], ab=opts.ab, mm=B.m/2, vb=(opts.retro?-1:1)*0.5*Math.sqrt(B.m/ab), th=opts.phase||0;
    const ux=Math.cos(th), uy=Math.sin(th);
    const p1={m:mm,x:B.x+ux*ab/2,y:B.y+uy*ab/2,vx:B.vx-uy*vb,vy:B.vy+ux*vb};
    const p2={m:mm,x:B.x-ux*ab/2,y:B.y-uy*ab/2,vx:B.vx+uy*vb,vy:B.vy-ux*vb};
    b.splice(k,1,p1,p2);
    return {s:sys(b), groups: groupsFor(k)};
  }
  return {s:sys(b), groups:[[0],[1],[2]]};
}
function groupsFor(k){ const g=[]; let idx=0; for(let i=0;i<3;i++){ if(i===k){ g.push([idx,idx+1]); idx+=2; } else { g.push([idx]); idx++; } } return g; }
function com(s,g){ let M=0,x=0,y=0; g.forEach(i=>{M+=s.m[i];x+=s.m[i]*s.x[i];y+=s.m[i]*s.y[i];}); return [x/M,y/M]; }
// deformação: desvio máximo dos lados em relação à média
function deform(s,groups){ const c=groups.map(g=>com(s,g)); const d=[[0,1],[1,2],[0,2]].map(([i,j])=>Math.hypot(c[i][0]-c[j][0],c[i][1]-c[j][1])); const m=(d[0]+d[1]+d[2])/3; return Math.max(...d.map(v=>Math.abs(v/m-1))); }
function survive(build, dt, Tmax, lim=0.3){
  const {s,groups}=build(); acc(s); let k=0, maxd=0;
  while(s.t<Tmax){ step(s,dt); if(++k%25===0){ const d=deform(s,groups); if(d>maxd) maxd=d; if(d>lim) return {t:s.t,maxd}; } }
  return {t:Tmax,maxd};
}
const PERTS=[[1e-4,0,0],[0,1e-4,0],[0,0,1e-4],[-1e-3,5e-4,0],[0,0,-1e-3]];
module.exports={lagrange,survive,PERTS};
