// corpos: 0..2 triângulo externo (m=1), 3..4 par central (M/2 cada) OU 3 = massa única M
function setup(M, ab, mode, pert){
  const R=1, m=1, b=[];
  const q = mode==='par' ? 3/16*(ab/R)**2 : 0;
  const v = Math.sqrt((M*(1+q) + m/Math.sqrt(3))/R);
  for(let k=0;k<3;k++){ const a=Math.PI/2+k*2*Math.PI/3; b.push({m, x:R*Math.cos(a), y:R*Math.sin(a), vx:-v*Math.sin(a), vy:v*Math.cos(a)}); }
  b[0].x += pert[0]; b[0].y += pert[1]; b[1].vx += pert[2];
  if(mode==='par'){ const vb=(global.RETRO?-1:1)*0.5*Math.sqrt(M/ab); b.push({m:M/2,x:ab/2,y:0,vx:0,vy:vb}); b.push({m:M/2,x:-ab/2,y:0,vx:0,vy:-vb}); }
  else if(M>0) b.push({m:M,x:0,y:0,vx:0,vy:0});
  return b;
}
function shapeLat(b){
  const x=[b[0].x,b[1].x,b[2].x], y=[b[0].y,b[1].y,b[2].y];
  const z1=[(x[1]-x[0])/Math.SQRT2,(y[1]-y[0])/Math.SQRT2], z2=[(2*x[2]-x[0]-x[1])/Math.sqrt(6),(2*y[2]-y[0]-y[1])/Math.sqrt(6)];
  const A=z1[0]**2+z1[1]**2, B=z2[0]**2+z2[1]**2; const im=z1[1]*z2[0]-z1[0]*z2[1];
  return Math.abs(2*im/(A+B));
}
function run(M, ab, mode, pert, Tmax){
  const b=setup(M,ab,mode,pert), n=b.length;
  const Pb = mode==='par' ? 2*Math.PI*Math.sqrt(ab**3/M) : 1;
  const dt = Math.min(0.002, Pb/60);
  const ax=new Float64Array(n), ay=new Float64Array(n);
  const acc=()=>{ ax.fill(0); ay.fill(0); for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){ const dx=b[j].x-b[i].x, dy=b[j].y-b[i].y, r2=dx*dx+dy*dy+1e-8, f=1/(r2*Math.sqrt(r2)); ax[i]+=b[j].m*dx*f; ay[i]+=b[j].m*dy*f; ax[j]-=b[i].m*dx*f; ay[j]-=b[i].m*dy*f; } };
  acc(); let t=0, k=0;
  while(t<Tmax){ for(let i=0;i<n;i++){ b[i].vx+=ax[i]*dt/2; b[i].vy+=ay[i]*dt/2; b[i].x+=b[i].vx*dt; b[i].y+=b[i].vy*dt; } acc(); for(let i=0;i<n;i++){ b[i].vx+=ax[i]*dt/2; b[i].vy+=ay[i]*dt/2; } t+=dt; if(++k%20===0 && shapeLat(b)<0.8) return t; }
  return Tmax;
}
module.exports={run};
if(require.main===module){
  const P=[[1e-4,0,0],[0,1e-4,0],[0,0,1e-4]];
  for(const M of [0,1,3,10,30]){
    const B=P.map(p=>run(M,0,'single',p,200).toFixed(1));
    console.log('M',M,'controle',B.join(' '));
  }
}
