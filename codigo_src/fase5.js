// Fase 5: três massas iguais. Par interno (separação 1, circular) + terceiro em órbita circular a distância D do centro do par
function run(D, ph, T){
  const m=[1,1,1]; const vin=0.5*Math.sqrt(2/1); // par: massa total 2, separação 1
  const vout=Math.sqrt(3/D); // terceiro em volta da massa total
  // posições relativas ao centro do par, depois corrige centro de massa
  let b=[{x:0.5,y:0,vx:0,vy:vin},{x:-0.5,y:0,vx:0,vy:-vin},{x:D*Math.cos(ph),y:D*Math.sin(ph),vx:-vout*Math.sin(ph),vy:vout*Math.cos(ph)}];
  // centro de massa: terceiro tem massa 1 e o par 2 -> ajustar
  const cx=(b[2].x)/3, cy=(b[2].y)/3, cvx=b[2].vx/3, cvy=b[2].vy/3;
  b.forEach(o=>{o.x-=cx;o.y-=cy;o.vx-=cvx;o.vy-=cvy;});
  const x=b.map(o=>o.x),y=b.map(o=>o.y),vx=b.map(o=>o.vx),vy=b.map(o=>o.vy),ax=[0,0,0],ay=[0,0,0];
  const acc=()=>{for(let i=0;i<3;i++){ax[i]=0;ay[i]=0;}for(let i=0;i<3;i++)for(let j=i+1;j<3;j++){const dx=x[j]-x[i],dy=y[j]-y[i],r2=dx*dx+dy*dy+1e-10,f=1/(r2*Math.sqrt(r2));ax[i]+=dx*f;ay[i]+=dy*f;ax[j]-=dx*f;ay[j]-=dy*f;}};
  acc(); const h=0.004; let t=0,k=0;
  while(t<T){ let rmin=Math.min(Math.hypot(x[0]-x[1],y[0]-y[1]),Math.hypot(x[1]-x[2],y[1]-y[2]),Math.hypot(x[0]-x[2],y[0]-y[2]));
    const dt=Math.min(h,0.02*Math.pow(rmin,1.5));
    for(let i=0;i<3;i++){vx[i]+=ax[i]*dt/2;vy[i]+=ay[i]*dt/2;x[i]+=vx[i]*dt;y[i]+=vy[i]*dt;} acc(); for(let i=0;i<3;i++){vx[i]+=ax[i]*dt/2;vy[i]+=ay[i]*dt/2;} t+=dt;
    if(++k%100===0){ // quebra: o par original deixa de ser o par mais ligado, ou a separação interna sai de [0,5; 2]
      const d01=Math.hypot(x[0]-x[1],y[0]-y[1]); if(d01>2.2) return t; } }
  return T;
}
const T=1500; // ~340 voltas do par interno
for(const D of [2,2.5,3,3.25,3.5,3.75,4,5,6]){
  const r=[0,1.3,2.6].map(ph=>run(D,ph,T));
  console.log('D/separação interna',D,'|',r.map(t=>t>=T?'∞':t.toFixed(0)).join(' '));
}
