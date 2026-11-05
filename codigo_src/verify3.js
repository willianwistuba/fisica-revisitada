function run(m3, D, ph, T){
  const vin=0.5*Math.sqrt(2), vout=Math.sqrt((2+m3)/D);
  const M=2+m3; let b=[{m:1,x:0.5,y:0,vx:0,vy:vin},{m:1,x:-0.5,y:0,vx:0,vy:-vin},{m:m3,x:D*Math.cos(ph),y:D*Math.sin(ph),vx:-vout*Math.sin(ph),vy:vout*Math.cos(ph)}];
  const cx=m3*b[2].x/M, cy=m3*b[2].y/M, cvx=m3*b[2].vx/M, cvy=m3*b[2].vy/M; b.forEach(o=>{o.x-=cx;o.y-=cy;o.vx-=cvx;o.vy-=cvy;});
  const m=b.map(o=>o.m),x=b.map(o=>o.x),y=b.map(o=>o.y),vx=b.map(o=>o.vx),vy=b.map(o=>o.vy),ax=[0,0,0],ay=[0,0,0];
  const acc=()=>{for(let i=0;i<3;i++){ax[i]=0;ay[i]=0;}for(let i=0;i<3;i++)for(let j=i+1;j<3;j++){const dx=x[j]-x[i],dy=y[j]-y[i],r2=dx*dx+dy*dy+1e-10,f=1/(r2*Math.sqrt(r2));ax[i]+=m[j]*dx*f;ay[i]+=m[j]*dy*f;ax[j]-=m[i]*dx*f;ay[j]-=m[i]*dy*f;}};
  acc(); const h=0.004; let t=0,k=0;
  while(t<T){const rmin=Math.min(Math.hypot(x[0]-x[1],y[0]-y[1]),Math.hypot(x[1]-x[2],y[1]-y[2]),Math.hypot(x[0]-x[2],y[0]-y[2]));const dt=Math.min(h,0.02*Math.pow(rmin,1.5));
    for(let i=0;i<3;i++){vx[i]+=ax[i]*dt/2;vy[i]+=ay[i]*dt/2;x[i]+=vx[i]*dt;y[i]+=vy[i]*dt;}acc();for(let i=0;i<3;i++){vx[i]+=ax[i]*dt/2;vy[i]+=ay[i]*dt/2;}t+=dt;
    if(++k%100===0){ if(Math.hypot(x[0]-x[1],y[0]-y[1])>2.2) return t; const bx=(x[0]+x[1])/2, by=(y[0]+y[1])/2, r3=Math.hypot(x[2]-bx,y[2]-by); if(r3<0.6*D||r3>1.8*D) return t; }}
  return T;
}
const T=1500;
for(const m3 of [0.1,1,10]){
  let thr=null;
  for(let D=1.6; D<=8.01; D+=0.1){ const ok=[0,1.3,2.6,4.0].every(ph=>run(m3,D,ph,T)>=T); if(ok){
      const ok2=[D+0.1,D+0.2].every(DD=>[0,2.6].every(ph=>run(m3,DD,ph,T)>=T)); if(ok2){thr=D;break;} } }
  const tidal=m3/thr**3; // maré do terceiro sobre o par dividida pela força interna
  const quad=(3/16)/thr**2; // quadrupolo do par sobre o terceiro dividido pelo monopolo
  const MA=2.8*Math.pow(1+m3/2,0.4);
  console.log(`hierarquia m3=${m3}: limiar simulado D≈${thr.toFixed(1)} (Mardling-Aarseth ${MA.toFixed(2)}) | maré no par ${(100*tidal).toFixed(2)}% | quadrupolo no terceiro ${(100*quad).toFixed(2)}% | maior ${(100*Math.max(tidal,quad)).toFixed(2)}%`);
}
