/* Live camera: pose overlay while you dance, recording of video + skeleton, playback, and optional saving to server.py.
   Everything works without a server; the server only adds a place to keep recordings. */
import {getLandmarker,tsBase,nextTs,drawPoses,unpack,motionFromSamples} from './capture.js';

const r4=v=>Math.round(v*1e4)/1e4;
const packImg=L=>{const a=[];for(const p of L)a.push(r4(p.x),r4(p.y),r4(p.z),r4(p.visibility??1));return a;};
const packWorld=L=>{const a=[];for(const p of L)a.push(r4(p.x),r4(p.y),r4(p.z));return a;};
const onFrame=(v,cb)=>v.requestVideoFrameCallback?v.requestVideoFrameCallback(()=>cb()):requestAnimationFrame(cb);

function pickMime(){
  for(const m of ['video/webm;codecs=vp9','video/webm;codecs=vp8','video/webm','video/mp4'])
    if(window.MediaRecorder&&MediaRecorder.isTypeSupported(m))return m;
  return '';
}

export class LiveCam{
  constructor(canvas,{onStatus}={}){this.canvas=canvas;this.onStatus=onStatus||(()=>{});this.stream=null;this.rec=null;this.samples=null;}
  get open(){return !!this.stream;}
  get recording(){return !!this.rec;}
  async start(numPoses,mirror){
    if(!navigator.mediaDevices?.getUserMedia)throw new Error('nocam');
    this.numPoses=numPoses;this.mirror=mirror;
    this.stream=await navigator.mediaDevices.getUserMedia({video:{width:{ideal:1280},height:{ideal:720},facingMode:'user'},audio:false});
    const v=this.video=document.createElement('video');v.muted=true;v.playsInline=true;v.srcObject=this.stream;await v.play();
    this.aspect=v.videoWidth/v.videoHeight;
    this.canvas.width=Math.min(960,v.videoWidth);this.canvas.height=Math.round(this.canvas.width/this.aspect);
    this.lm=await getLandmarker(numPoses);
    this.base=tsBase();this.t0=performance.now();this.poses=[];this.fps=0;this.lastT=performance.now();
    const loop=()=>{
      if(!this.stream)return;
      const now=performance.now();
      try{
        const r=this.lm.detectForVideo(v,nextTs(this.base+(now-this.t0)));
        this.poses=r.landmarks||[];
        if(this.rec&&this.recT0!==null&&this.poses.length)
          this.samples.push({t:r4((now-this.recT0)/1000),p:this.poses.map(packImg),w:(r.worldLandmarks||[]).map(packWorld)});
      }catch(e){}
      drawPoses(this.canvas.getContext('2d'),v,this.poses,this.mirror);
      this.fps=this.fps*0.9+0.1*(1000/Math.max(1,now-this.lastT));this.lastT=now;
      this.onStatus({fps:this.fps,people:this.poses.length,sec:this.rec&&this.recT0!==null?(now-this.recT0)/1000:null});
      onFrame(v,loop);
    };
    onFrame(v,loop);
  }
  setMirror(m){this.mirror=m;}
  startRec(){
    if(!this.stream||this.rec)return;
    this.samples=[];this.chunks=[];this.recT0=null;this.mime=pickMime();
    const mr=this.rec=new MediaRecorder(this.stream,this.mime?{mimeType:this.mime,videoBitsPerSecond:2_500_000}:{});
    mr.ondataavailable=e=>{if(e.data.size)this.chunks.push(e.data);};
    mr.onstart=()=>{this.recT0=performance.now();};
    mr.start(1000);
  }
  stopRec(){
    const mr=this.rec;if(!mr)return Promise.resolve(null);
    return new Promise(res=>{mr.onstop=()=>{
      const type=(mr.mimeType||this.mime||'video/webm').split(';')[0];
      const out={name:'',created:new Date().toISOString(),duration:this.recT0?(performance.now()-this.recT0)/1000:0,
        aspect:this.aspect,people:this.numPoses,mirror:this.mirror,videoType:type,samples:this.samples,
        blob:new Blob(this.chunks,{type})};
      this.rec=null;this.recT0=null;this.samples=null;this.chunks=null;res(out);};mr.stop();});
  }
  async stop(){if(this.rec)await this.stopRec();if(this.stream)for(const t of this.stream.getTracks())t.stop();this.stream=null;if(this.video)this.video.srcObject=null;}
}

/* index of the sample nearest to time t (samples are sorted by t) */
function nearest(S,t){let lo=0,hi=S.length-1;if(hi<0)return -1;while(lo<hi){const m=(lo+hi)>>1;if(S[m].t<t)lo=m+1;else hi=m;}
  return lo>0&&Math.abs(S[lo-1].t-t)<Math.abs(S[lo].t-t)?lo-1:lo;}

/* plays a recording: the video drives the clock, the skeleton for that moment is drawn over it */
export class Player{
  constructor(canvas,video){this.canvas=canvas;this.video=video;this.rec=null;this.showVideo=true;
    const loop=()=>{if(this.rec)this.draw();requestAnimationFrame(loop);};requestAnimationFrame(loop);}
  async load(rec,url){
    this.rec=rec;const v=this.video;v.src=url;v.playsInline=true;
    await new Promise((res,rej)=>{v.onloadedmetadata=res;v.onerror=()=>rej(new Error('video'));});
    /* MediaRecorder webm files often report an unknown (Infinity) duration until the end has been read */
    if(!isFinite(v.duration)){await new Promise(res=>{v.ondurationchange=()=>{if(isFinite(v.duration)){v.ondurationchange=null;res();}};v.currentTime=1e7;setTimeout(res,3000);});v.currentTime=0;}
    const w=Math.min(960,v.videoWidth||960);this.canvas.width=w;this.canvas.height=Math.round(w/(rec.aspect||v.videoWidth/v.videoHeight||16/9));
  }
  get duration(){const d=this.video.duration;return isFinite(d)?d:(this.rec?.duration||0);}
  draw(){
    const S=this.rec.samples,i=nearest(S,this.video.currentTime);
    const poses=i>=0&&Math.abs(S[i].t-this.video.currentTime)<0.25?S[i].p.map(a=>unpack(a,4)):[];
    drawPoses(this.canvas.getContext('2d'),this.showVideo?this.video:null,poses,this.rec.mirror);
  }
  unload(){this.rec=null;this.video.pause();this.video.removeAttribute('src');this.video.load();}
}

export function toMotion(rec){return motionFromSamples(rec.samples,{aspect:rec.aspect,numPoses:rec.people||1});}

/* server.py API, addressed relative to the page so it also works under a sub-path */
export const server={
  ok:false,
  async ping(){try{const r=await fetch('api/ping',{cache:'no-store'});this.ok=r.ok&&(await r.json()).app==='dance-studio';}catch(e){this.ok=false;}return this.ok;},
  async list(){const r=await fetch('api/recordings',{cache:'no-store'});if(!r.ok)throw new Error(r.status);return r.json();},
  async get(id){const r=await fetch('api/recordings/'+id,{cache:'no-store'});if(!r.ok)throw new Error(r.status);return r.json();},
  videoURL(id){return 'api/recordings/'+id+'/video';},
  async save(rec){
    const {blob,...meta}=rec;
    let r=await fetch('api/recordings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(meta)});
    if(!r.ok)throw new Error(r.status);const {id}=await r.json();
    r=await fetch('api/recordings/'+id+'/video',{method:'PUT',headers:{'Content-Type':rec.videoType||'video/webm'},body:blob});
    if(!r.ok){await fetch('api/recordings/'+id,{method:'DELETE'});throw new Error(r.status);}
    return id;
  },
  async rename(id,name){const r=await fetch('api/recordings/'+id,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({name})});if(!r.ok)throw new Error(r.status);},
  async remove(id){const r=await fetch('api/recordings/'+id,{method:'DELETE'});if(!r.ok)throw new Error(r.status);}
};
