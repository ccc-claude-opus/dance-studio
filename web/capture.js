/* Video → 3D dance motion, fully in the browser with MediaPipe Pose Landmarker.
   Output uses the page's 22-joint layout so captured moves play exactly like the built-in ones. */
let landmarker=null, landmarkerPoses=0, lastTs=0;
/* MediaPipe VIDEO mode needs strictly increasing timestamps across every caller (file analysis and live camera) */
export function tsBase(){return lastTs+1000;}
export function nextTs(ms){lastTs=Math.max(lastTs+1,Math.round(ms));return lastTs;}

function loadScript(src){return new Promise((res,rej)=>{const s=document.createElement('script');s.src=src;s.onload=res;s.onerror=()=>rej(new Error('load '+src));document.head.appendChild(s);});}

export async function getLandmarker(numPoses){
  if(landmarker&&landmarkerPoses===numPoses)return landmarker;
  const {PoseLandmarker}=await import(new URL('vision_bundle.mjs',document.baseURI).href);
  if(!window.POSE_MODEL_B64)await loadScript('pose_model.js');
  const bin=atob(window.POSE_MODEL_B64);const u=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);
  const fileset={wasmLoaderPath:new URL('vision_wasm_internal.js',document.baseURI).href,wasmBinaryPath:new URL('vision_wasm_internal.wasm',document.baseURI).href};
  const opts=d=>({baseOptions:{modelAssetBuffer:u,delegate:d},runningMode:'VIDEO',numPoses,minPoseDetectionConfidence:0.4,minTrackingConfidence:0.4,minPosePresenceConfidence:0.4});
  if(landmarker){try{landmarker.close();}catch(e){}}
  try{landmarker=await PoseLandmarker.createFromOptions(fileset,opts('GPU'));}
  catch(e){landmarker=await PoseLandmarker.createFromOptions(fileset,opts('CPU'));}
  landmarkerPoses=numPoses;return landmarker;
}

const EDGES=[[11,12],[11,13],[13,15],[12,14],[14,16],[11,23],[12,24],[23,24],[23,25],[25,27],[27,31],[24,26],[26,28],[28,32],[27,29],[29,31],[28,30],[30,32],[15,19],[16,20],[7,8]];
const COLS=['#7f93c9','#e0607a'];
/* video frame plus skeletons; landmarks are normalised image coordinates. mirror flips both like a selfie view */
export function drawPoses(ctx,video,poses,mirror){
  const W=ctx.canvas.width,H=ctx.canvas.height;
  ctx.save();if(mirror){ctx.translate(W,0);ctx.scale(-1,1);}
  if(video&&video.readyState>=2)ctx.drawImage(video,0,0,W,H);else{ctx.fillStyle='#000';ctx.fillRect(0,0,W,H);}
  const lw=Math.max(2,W/220);
  poses.forEach((L,pi)=>{const ok=i=>L[i]&&(L[i].visibility??1)>0.3;
    ctx.strokeStyle=COLS[pi%2];ctx.lineWidth=lw;ctx.lineCap='round';ctx.beginPath();
    for(const [a,b] of EDGES)if(ok(a)&&ok(b)){ctx.moveTo(L[a].x*W,L[a].y*H);ctx.lineTo(L[b].x*W,L[b].y*H);}ctx.stroke();
    ctx.fillStyle='#fff';for(let i=11;i<33;i++)if(ok(i)){ctx.beginPath();ctx.arc(L[i].x*W,L[i].y*H,lw*0.9,0,7);ctx.fill();}
    if(ok(0)){ctx.strokeStyle=COLS[pi%2];ctx.beginPath();ctx.arc(L[0].x*W,L[0].y*H,lw*3,0,7);ctx.stroke();}});
  ctx.restore();
}
function drawOverlay(ctx,video,poses){drawPoses(ctx,video,poses,false);}

function seek(video,t){return new Promise(res=>{const h=()=>{video.removeEventListener('seeked',h);res();};video.addEventListener('seeked',h);video.currentTime=t;});}

/* one MediaPipe pose (world landmarks in metres, hip-centred; image landmarks normalised) → our 22 joints */
function toJoints(Wl,Il,aspect){
  const P=i=>[Wl[i].x,-Wl[i].y,-Wl[i].z];
  const mid=(a,b)=>[(a[0]+b[0])/2,(a[1]+b[1])/2,(a[2]+b[2])/2];
  const add=(a,b,k=1)=>[a[0]+b[0]*k,a[1]+b[1]*k,a[2]+b[2]*k];
  const sub=(a,b)=>[a[0]-b[0],a[1]-b[1],a[2]-b[2]];
  const nrm=a=>{const l=Math.hypot(...a)||1;return [a[0]/l,a[1]/l,a[2]/l];};
  const lHip=P(23),rHip=P(24),hips=mid(lHip,rHip),lSh=P(11),rSh=P(12),shm=mid(lSh,rSh),ears=mid(P(7),P(8));
  const up=nrm(sub(ears,shm));
  const spine=add(hips,sub(shm,hips),0.3),chest=add(hips,sub(shm,hips),0.62);
  const neck=add(shm,sub(ears,shm),0.3);const head=add(ears,up,-0.05);const headTop=add(head,up,0.2);
  const J=[hips,spine,chest,neck,head,headTop,lSh,P(13),P(15),P(19),rSh,P(14),P(16),P(20),lHip,P(25),P(27),P(31),rHip,P(26),P(28),P(32)];
  // root position in the room from where the hips sit in the frame
  const hx=(Il[23].x+Il[24].x)/2;const top=Math.min(Il[0].y,Il[11].y,Il[12].y),bot=Math.max(Il[27].y,Il[28].y,Il[31].y,Il[32].y);
  const hNorm=Math.max(0.05,bot-top);const mPerUnit=1.5/hNorm;   // ~1.5 m from nose to feet
  return {J,rx:(hx-0.5)*aspect*mPerUnit,scale:mPerUnit};
}

function smoothSeries(F,K,data,sig){
  const r=Math.max(1,Math.ceil(sig*3)),w=[];let s=0;for(let i=-r;i<=r;i++){const v=Math.exp(-0.5*(i/sig)**2);w.push(v);s+=v;}w.forEach((v,i)=>w[i]=v/s);
  const out=new Float32Array(data.length);
  for(let f=0;f<F;f++)for(let k=0;k<K;k++){let a=0;for(let i=-r;i<=r;i++){const g=Math.min(F-1,Math.max(0,f+i));a+=w[i+r]*data[g*K+k];}out[f*K+k]=a;}
  return out;
}

export async function captureVideo(file,{numPoses=1,start=0,end=null,rate=15,onProgress,overlay,signal}={}){
  const url=URL.createObjectURL(file);const video=document.createElement('video');video.muted=true;video.playsInline=true;video.preload='auto';video.src=url;
  await new Promise((res,rej)=>{video.onloadedmetadata=res;video.onerror=()=>rej(new Error('video'));});
  const dur=video.duration;end=Math.min(end??dur,dur,start+60);
  if(overlay){overlay.width=Math.min(480,video.videoWidth);overlay.height=Math.round(overlay.width*video.videoHeight/video.videoWidth);}
  onProgress&&onProgress(0,'model');
  const lm=await getLandmarker(numPoses);
  const aspect=video.videoWidth/video.videoHeight;
  const frames=[];const n=Math.max(2,Math.floor((end-start)*rate));const base=tsBase();
  for(let i=0;i<n;i++){
    if(signal&&signal.aborted)throw new Error('aborted');
    const t=start+i/rate;await seek(video,t);
    const r=lm.detectForVideo(video,nextTs(base+(t-start)*1000));
    const poses=(r.worldLandmarks||[]).map((W,k)=>toJoints(W,r.landmarks[k],aspect));
    frames.push(poses.map((p,k)=>({...p,img:r.landmarks[k]})));
    if(overlay)drawOverlay(overlay.getContext('2d'),video,r.landmarks||[]);
    onProgress&&onProgress((i+1)/n,'run');
    if(i%4===0)await new Promise(r=>setTimeout(r,0));
  }
  URL.revokeObjectURL(url);
  return assemble(frames,n,rate,numPoses);
}

/* camera recording samples ({t, p:[flat image landmarks x,y,z,v], w:[flat world landmarks x,y,z]}) → 3D motion */
export function unpack(a,k){const L=[];for(let i=0;i<33;i++)L.push(k===4?{x:a[i*4],y:a[i*4+1],z:a[i*4+2],visibility:a[i*4+3]}:{x:a[i*3],y:a[i*3+1],z:a[i*3+2]});return L;}
export function motionFromSamples(samples,{aspect=16/9,numPoses=1,rate=15}={}){
  if(samples.length<2)throw new Error('nobody');
  const t0=samples[0].t,t1=samples[samples.length-1].t;const n=Math.max(2,Math.floor((t1-t0)*rate));
  const frames=[];let j=0;
  for(let i=0;i<n;i++){const t=t0+i/rate;
    while(j+1<samples.length&&Math.abs(samples[j+1].t-t)<=Math.abs(samples[j].t-t))j++;
    const s=samples[j];frames.push(s.w.map((w,k)=>{const img=unpack(s.p[k],4);return {...toJoints(unpack(w,3),img,aspect),img};}));}
  return assemble(frames,n,rate,numPoses);
}

function assemble(frames,n,rate,numPoses){
  // track identities across frames by hip position in the image
  const people=Math.min(numPoses,Math.max(...frames.map(f=>f.length),0));
  if(!people)throw new Error('nobody');
  const tracks=Array.from({length:people},()=>new Array(n).fill(null));let last=null;
  for(let i=0;i<n;i++){
    const ps=frames[i].slice(0,people);if(!ps.length)continue;
    if(people===1||!last){ps.sort((a,b)=>a.rx-b.rx);ps.forEach((p,k)=>tracks[k][i]=p);}
    else if(ps.length===1){const p=ps[0];const k=Math.abs(p.rx-last[0])<=Math.abs(p.rx-last[1])?0:1;tracks[k][i]=p;}
    else{const [a,b]=ps;const keep=Math.abs(a.rx-last[0])+Math.abs(b.rx-last[1])<=Math.abs(a.rx-last[1])+Math.abs(b.rx-last[0]);tracks[0][i]=keep?a:b;tracks[1][i]=keep?b:a;}
    last=tracks.map((tr,k)=>tr[i]?tr[i].rx:(last?last[k]:0));
  }
  const coverage=tracks.map(tr=>tr.filter(Boolean).length/n);
  // fill gaps, assemble, smooth, resample to 30 fps, put on the floor
  const NJ=22,K=NJ*3,OUT=30;
  const actors=[];
  for(let k=0;k<people;k++){
    if(coverage[k]<0.4)continue;
    const tr=tracks[k];const raw=new Float32Array(n*K);const rx=new Float32Array(n);
    let prev=tr.findIndex(Boolean);
    for(let i=0;i<n;i++){
      let p=tr[i];
      if(!p){let nx=i+1;while(nx<n&&!tr[nx])nx++;const a=tr[prev]||tr[nx],b=nx<n?tr[nx]:a;const u=nx<n&&prev>=0&&prev<i?(i-prev)/(nx-prev):0;
        p={J:a.J.map((v,j)=>v.map((c,d)=>c*(1-u)+b.J[j][d]*u)),rx:a.rx*(1-u)+b.rx*u};}
      else prev=i;
      for(let j=0;j<NJ;j++)for(let d=0;d<3;d++)raw[i*K+j*3+d]=p.J[j][d];rx[i]=p.rx;
    }
    const sm=smoothSeries(n,K,raw,1.1);const srx=smoothSeries(n,1,rx,rate*0.25);
    const F=Math.max(2,Math.round((n-1)/rate*OUT)+1);const f=new Float32Array(F*K);
    for(let o=0;o<F;o++){const x=o/OUT*rate;const i0=Math.min(n-1,Math.floor(x)),i1=Math.min(n-1,i0+1),u=x-i0;
      const ox=srx[i0]*(1-u)+srx[i1]*u;
      for(let q=0;q<K;q++)f[o*K+q]=sm[i0*K+q]*(1-u)+sm[i1*K+q]*u;
      for(let j=0;j<NJ;j++)f[o*K+j*3]+=ox;}
    // ground: rolling minimum of the feet over ±0.4 s, smoothed
    const feet=[16,17,20,21];const lo=new Float32Array(F);
    for(let o=0;o<F;o++){let m=1e9;for(const j of feet)m=Math.min(m,f[o*K+j*3+1]);lo[o]=m;}
    const W=Math.round(0.4*OUT);const rl=new Float32Array(F);for(let o=0;o<F;o++){let m=1e9;for(let q=Math.max(0,o-W);q<=Math.min(F-1,o+W);q++)m=Math.min(m,lo[q]);rl[o]=m;}
    const gr=smoothSeries(F,1,rl,OUT*0.2);
    for(let o=0;o<F;o++)for(let j=0;j<NJ;j++)f[o*K+j*3+1]+=0.03-gr[o];
    actors.push({f,frames:F,cover:coverage[k]});
  }
  if(!actors.length)throw new Error('nobody');
  const F=Math.min(...actors.map(a=>a.frames));
  // centre the group on the floor
  let cx=0,cz=0,c=0;for(const a of actors)for(let o=0;o<F;o++){cx+=a.f[o*K];cz+=a.f[o*K+2];c++;}cx/=c;cz/=c;
  for(const a of actors)for(let o=0;o<F;o++)for(let j=0;j<NJ;j++){a.f[o*K+j*3]-=cx;a.f[o*K+j*3+2]-=cz;}
  return {fps:OUT,frames:F,actors:actors.map(a=>({f:a.f.slice(0,F*K),cover:a.cover})),duration:(F-1)/OUT};
}
