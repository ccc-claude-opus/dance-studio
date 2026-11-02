/* Synthesized accompaniment, scheduled against the dance clock so it follows speed, seek and loop. */
(function(){
const mtof=m=>440*Math.pow(2,(m-69)/12);
const N={C:0,Db:1,D:2,Eb:3,E:4,F:5,Gb:6,G:7,Ab:8,A:9,Bb:10,B:11};
function chord(root,q){const r=N[root];const iv={M:[0,4,7],m:[0,3,7],7:[0,4,7,10],m7:[0,3,7,10],M7:[0,4,7,11],6:[0,4,7,9],m9:[0,3,7,10,14]}[q];return {r,iv};}

const STYLES={
  salsa:{label:'薩爾薩伴奏：克拉維、康加鼓、鋼琴蒙圖諾、低音貝斯',label_en:'Salsa band: clave, congas, piano montuno and bass',spb:4,bar:16,
    prog:[chord('C','M'),chord('F','M'),chord('G','7'),chord('F','M')]},
  swing:{label:'搖擺爵士伴奏：疊鈸搖擺節奏、行走低音、鋼琴與銅管',label_en:'Swing jazz: ride cymbal swing, walking bass, piano and horns',spb:3,bar:12,
    prog:[chord('Bb','6'),chord('G','7'),chord('C','m7'),chord('F','7')]},
  lambada:{label:'拉丁流行伴奏：鼓組、切分貝斯、反拍和弦',label_en:'Latin pop: drums, syncopated bass and offbeat chords',spb:4,bar:16,
    prog:[chord('A','m'),chord('G','M'),chord('F','M'),chord('E','7')]},
  ballet:{label:'芭蕾課鋼琴伴奏：三拍子',label_en:'Ballet class piano in three-four',spb:2,bar:6,
    prog:[chord('C','M'),chord('A','m'),chord('D','m'),chord('G','7'),chord('C','M'),chord('F','M'),chord('G','7'),chord('C','M')]},
  indian:{label:'印度伴奏：塔布拉鼓 Keherwa 節奏、坦普拉持續音',label_en:'Indian: tabla in keherwa taal over a tanpura drone',spb:4,bar:16,prog:[chord('C','M')]},
  break:{label:'Boom bap 嘻哈鼓組與貝斯',label_en:'Boom bap hip-hop drums and bass',spb:4,bar:16,prog:[chord('C','m9'),chord('C','m9'),chord('Ab','M7'),chord('G','m7')]},
  bachata:{label:'巴恰塔伴奏：主奏吉他琶音、邦哥鼓、刮瓜、低音貝斯，第四拍加重',label_en:'Bachata band: requinto guitar arpeggios, bongos, güira and bass, with the accent on 4',spb:4,bar:16,
    prog:[chord('A','m'),chord('D','m'),chord('E','7'),chord('A','m')]},
  jive:{label:'吉魯巴搖滾伴奏：布基低音、反拍小鼓、鋼琴',label_en:'Rock and roll for jive: boogie bass, backbeat snare and piano',spb:2,bar:8,
    prog:[chord('C','7'),chord('C','7'),chord('F','7'),chord('C','7'),chord('G','7'),chord('F','7'),chord('C','7'),chord('G','7')]},
  waltz:{label:'華爾滋伴奏：三拍子鋼琴與弦樂',label_en:'Waltz: piano and strings in three-four',spb:2,bar:6,
    prog:[chord('F','M'),chord('F','M'),chord('C','7'),chord('C','7'),chord('C','7'),chord('C','7'),chord('F','M'),chord('F','M')]},
  vwaltz:{label:'維也納華爾滋伴奏：快速三拍子',label_en:'Viennese waltz: fast three-four',spb:2,bar:6,pat:'waltz',
    prog:[chord('D','M'),chord('D','M'),chord('A','7'),chord('A','7'),chord('A','7'),chord('A','7'),chord('D','M'),chord('D','M')]},
  tango:{label:'探戈伴奏：斷奏和弦、低音與手風琴式重音',label_en:'Tango: staccato chords, bass and bandoneon-style accents',spb:2,bar:8,
    prog:[chord('A','m'),chord('A','m'),chord('E','7'),chord('A','m'),chord('D','m'),chord('A','m'),chord('E','7'),chord('A','m')]},
  foxtrot:{label:'狐步伴奏：輕柔搖擺爵士',label_en:'Foxtrot: smooth swing',spb:3,bar:12,pat:'swing',
    prog:[chord('F','6'),chord('D','7'),chord('G','m7'),chord('C','7')]},
  quickstep:{label:'快步舞伴奏：快速搖擺爵士',label_en:'Quickstep: fast swing',spb:3,bar:12,pat:'swing',
    prog:[chord('C','6'),chord('A','7'),chord('D','m7'),chord('G','7')]},
  chacha:{label:'恰恰伴奏：牛鈴、刮瓜、康加與鋼琴，第 4&1 拍恰恰恰',label_en:'Cha cha: cowbell, güiro, congas and piano, cha-cha-cha on 4-and-1',spb:2,bar:8,
    prog:[chord('C','M'),chord('G','7'),chord('C','M'),chord('G','7')]},
  rumba:{label:'倫巴伴奏：慢速波麗露節奏',label_en:'Rumba: slow bolero groove',spb:2,bar:8,
    prog:[chord('A','m'),chord('D','m'),chord('G','7'),chord('C','M7')]},
  paso:{label:'鬥牛舞伴奏：二拍進行曲與銅管',label_en:'Paso doble: two-four march with brass',spb:2,bar:4,
    prog:[chord('E','m'),chord('E','m'),chord('B','7'),chord('B','7'),chord('E','m'),chord('A','m'),chord('B','7'),chord('E','m')]},
  bsamba:{label:'國標森巴伴奏：巴西打擊樂',label_en:'Ballroom samba: Brazilian percussion',spb:4,bar:16,pat:'samba',prog:[chord('G','M'),chord('D','7')]},
  samba:{label:'森巴打擊：蘇爾多大鼓、坦伯林、阿哥哥鈴、四弦琴',label_en:'Samba percussion: surdo, tamborim, agogô and cavaquinho',spb:4,bar:16,prog:[chord('G','M'),chord('D','7')]}
};

/* Real recordings streamed from incompetech.com (Kevin MacLeod, CC BY 4.0). bpm is the composer's listed tempo. */
const INC='https://incompetech.com/music/royalty-free/mp3-royaltyfree/';
const TRACKS={
  salsa:[['No Frills Salsa',144],['Arroz Con Pollo',200]],
  swing:[['George Street Shuffle',153],['Opportunity Walks',156]],
  lambada:[['Notanico Merengue',120],['Peppy Pepe',124]],
  ballet:[['Divertissement - Pizzicato','Divertissement',140],['Gymnopedie No. 3','Gymnopedie No 3',77]],
  indian:[['Vadodora',97],['Jalandhar',81]],
  break:[['Griphop',90],['Vicious',80]],
  bachata:[['Del Rio Bravo',120],['Sardana',75]],
  jive:[['Boogie Party',178]],
  waltz:[['Devonshire Waltz Moderato',93],['Grand Dark Waltz Moderato',92]],
  vwaltz:[['Starting Out Waltz Vivace',186]],
  tango:[['Tango de Manzana',127]],
  foxtrot:[['In Your Arms',98],['Long Stroll',98]],
  quickstep:[['Rollin at 5',210]],
  chacha:[['Peppy Pepe',124],['Cuban Sandwich',80]],
  rumba:[['Verano Sensual',103]],
  paso:[['El Magicia',118]],
  bsamba:[['Samba Isobel',95],['Carnivale Intrigue',95]],
  samba:[['Lagoa v1',109],['Modern Jazz Samba',85]]
};
for(const k in TRACKS)TRACKS[k]=TRACKS[k].map(a=>{const [title,file,bpm]=a.length===2?[a[0],a[0],a[1]]:a;
  return {id:'inc:'+file,name:title,bpm,url:INC+encodeURIComponent(file+'.mp3'),stream:true,
    credit:'“'+title+'” Kevin MacLeod (incompetech.com), CC BY 4.0'};});

/* Lead lines: voice, centre pitch, and two one-bar rhythms [step,length] that alternate. Pitches come from the chord
   (or scale) and are seeded per two-bar motif, so phrases repeat in an A A B A shape and follow the harmony. */
const MEL={
  salsa:{v:'trumpet',base:72,rh:[[[0,2],[3,1],[6,2],[10,2],[12,3]],[[2,2],[4,2],[8,4],[14,2]]]},
  swing:{v:'vibes',base:72,rh:[[[0,3],[5,1],[6,3],[11,1]],[[0,2],[3,3],[9,3]]]},
  lambada:{v:'bando',base:72,rh:[[[0,3],[4,2],[6,2],[8,4],[12,4]],[[0,2],[2,2],[4,4],[10,6]]]},
  ballet:{v:'flute',base:76,rh:[[[0,3],[3,1],[4,2]],[[0,4],[4,2]]]},
  indian:{v:'bansuri',base:67,scale:[0,1,4,5,7,8,11],rh:[[[0,6],[6,2],[8,4],[12,4]],[[0,4],[4,4],[8,8]]]},
  jive:{v:'sax',base:67,rh:[[[0,1],[1,1],[3,2],[6,2]],[[0,3],[4,1],[5,3]]]},
  waltz:{v:'violin',base:76,rh:[[[0,4],[4,2]],[[0,2],[2,2],[4,2]]]},
  vwaltz:{v:'violin',base:74,rh:[[[0,6]],[[0,2],[2,4]]]},
  tango:{v:'bando',base:69,rh:[[[0,1],[2,1],[3,1],[4,3],[7,1]],[[0,3],[3,1],[4,4]]]},
  foxtrot:{v:'sax',base:67,rh:[[[0,6],[6,3],[9,3]],[[0,3],[3,3],[6,6]]]},
  quickstep:{v:'trumpet',base:72,rh:[[[0,3],[3,3],[6,2],[9,3]],[[0,6],[6,6]]]},
  chacha:{v:'flute',base:79,rh:[[[0,2],[2,2],[4,1],[5,1],[6,2]],[[0,3],[3,1],[4,4]]]},
  rumba:{v:'violin',base:72,rh:[[[0,4],[4,2],[6,2]],[[0,6],[6,2]]]},
  paso:{v:'trumpet',base:71,rh:[[[0,1],[1,1],[2,2]],[[0,3],[3,1]]]},
  bsamba:{v:'flute',base:79,rh:[[[0,2],[3,2],[6,2],[8,2],[11,2],[14,2]],[[0,3],[3,3],[6,4],[12,4]]]},
  samba:{v:'flute',base:79,rh:[[[0,2],[3,2],[6,2],[8,2],[11,2],[14,2]],[[0,3],[3,3],[6,4],[12,4]]]}
};
const FILLS=new Set(['salsa','lambada','break','jive','chacha','samba','bsamba','swing','quickstep','paso','bachata']);
const rnd=n=>{n=Math.sin(n*12.9898+78.233)*43758.5453;return n-Math.floor(n);};

class Music{
  constructor(){this.ctx=null;this.on=false;this.vol=0.7;this.lastT=null;this.style='salsa';this.bpm=180;this.off=0;}
  ensure(){
    if(this.ctx) return;
    const C=window.AudioContext||window.webkitAudioContext; if(!C) return;
    const ctx=this.ctx=new C();
    this.comp=ctx.createDynamicsCompressor();this.comp.threshold.value=-14;this.comp.ratio.value=4;
    this.master=ctx.createGain();this.master.gain.value=this.vol*0.55;
    this.master.connect(this.comp);this.comp.connect(ctx.destination);
    /* melodic voices get a small room; drums stay dry */
    const sr=ctx.sampleRate,il=Math.floor(sr*2.2),ir=ctx.createBuffer(2,il,sr);
    for(let c=0;c<2;c++){const d=ir.getChannelData(c);for(let i=0;i<il;i++)d[i]=(Math.random()*2-1)*Math.pow(1-i/il,3.2);}
    this.verb=ctx.createConvolver();this.verb.buffer=ir;this.wet=ctx.createGain();this.wet.gain.value=0.22;
    this.mel=ctx.createGain();this.mel.connect(this.master);this.mel.connect(this.verb);this.verb.connect(this.wet);this.wet.connect(this.master);
    this.hv=1;
    const len=ctx.sampleRate;const b=ctx.createBuffer(1,len,ctx.sampleRate);const d=b.getChannelData(0);for(let i=0;i<len;i++)d[i]=Math.random()*2-1;this.noise=b;
  }
  setOn(v){this.ensure();if(!this.ctx)return false;this.on=v;if(v&&this.ctx.state!=='running')this.ctx.resume();this.lastT=null;return true;}
  setVol(v){this.vol=v;if(this.master)this.master.gain.setTargetAtTime(v*0.55,this.ctx.currentTime,0.05);}
  setGrid(style,bpm,off){this.style=style;this.bpm=bpm;this.off=off||0;this.lastT=null;}
  reset(){this.lastT=null;}
  tick(tNow,speed,playing){
    if(!this.on||!this.ctx||!playing||speed<=0) {this.lastT=null;return;}
    const st=STYLES[this.style];const stepDur=60/this.bpm/st.spb;
    const horizon=tNow+0.18*speed;
    if(this.lastT===null||this.lastT<tNow-0.5||this.lastT>horizon) this.lastT=tNow;
    let k=Math.ceil((this.lastT-this.off)/stepDur-1e-6);
    for(;;k++){
      const te=this.off+k*stepDur; if(te>=horizon) break; if(te<this.lastT) continue;
      const when=this.ctx.currentTime+0.03+Math.max(0,(te-tNow)/speed);
      /* slight per-hit timing and loudness drift so loops don't sound machine-stamped */
      this.hv=0.86+Math.random()*0.18;
      const j=(k%st.spb===0)?0:(Math.random()-0.5)*0.008;
      this.play(st,k,when+j,stepDur/speed);
    }
    this.lastT=horizon;
  }
  /* ---------- voices ---------- */
  env(g,when,a,peak,dec){peak*=this.hv||1;g.gain.setValueAtTime(0.0001,when);g.gain.exponentialRampToValueAtTime(peak,when+a);g.gain.exponentialRampToValueAtTime(0.0001,when+a+dec);}
  osc(type,f,when,dur,peak,dec,dest,f2,a=0.004){const c=this.ctx,o=c.createOscillator(),g=c.createGain();o.type=type;o.frequency.setValueAtTime(f,when);if(f2)o.frequency.exponentialRampToValueAtTime(f2,when+dur);this.env(g,when,a,peak,dec);o.connect(g);g.connect(dest||this.master);o.start(when);o.stop(when+a+dec+0.05);return o;}
  nz(when,peak,dec,type,freq,q=0.8){const c=this.ctx,s=c.createBufferSource(),f=c.createBiquadFilter(),g=c.createGain();s.buffer=this.noise;f.type=type;f.frequency.value=freq;f.Q.value=q;this.env(g,when,0.002,peak,dec);s.connect(f);f.connect(g);g.connect(this.master);s.start(when,Math.random()*0.5);s.stop(when+dec+0.05);}
  kick(w,v=1){this.osc('sine',150,w,0.12,0.9*v,0.32,null,45);}
  snare(w,v=1){this.nz(w,0.45*v,0.16,'bandpass',1900,0.7);this.osc('triangle',190,w,0.05,0.25*v,0.08);}
  brush(w,v=1){this.nz(w,0.18*v,0.12,'bandpass',3500,0.5);}
  hat(w,v=1,open){this.nz(w,0.22*v,open?0.22:0.04,'highpass',7500,0.7);}
  ride(w,v=1){this.nz(w,0.12*v,0.35,'bandpass',6200,1.2);this.osc('square',5100,w,0.01,0.015*v,0.25);}
  clave(w,v=1){this.osc('sine',2450,w,0.02,0.4*v,0.06);}
  cowbell(w,v=1){this.osc('square',562,w,0.01,0.06*v,0.18);this.osc('square',845,w,0.01,0.05*v,0.18);}
  conga(w,f,v=1,slap){if(slap){this.nz(w,0.3*v,0.05,'bandpass',2200,1);this.osc('sine',f*1.4,w,0.04,0.2*v,0.08);}else this.osc('sine',f*1.12,w,0.06,0.5*v,0.26,null,f);}
  bass(w,m,dur,v=1){const c=this.ctx,o=c.createOscillator(),s=c.createOscillator(),f=c.createBiquadFilter(),g=c.createGain();o.type='sawtooth';s.type='sine';o.frequency.value=s.frequency.value=mtof(m);f.type='lowpass';f.frequency.setValueAtTime(900,w);f.frequency.exponentialRampToValueAtTime(220,w+dur);g.gain.setValueAtTime(0.0001,w);g.gain.exponentialRampToValueAtTime(0.32*v,w+0.01);g.gain.setTargetAtTime(0.0001,w+dur*0.85,0.05);o.connect(f);s.connect(g);f.connect(g);g.connect(this.master);o.start(w);s.start(w);o.stop(w+dur+0.3);s.stop(w+dur+0.3);}
  keys(w,ms,dur,v=1){for(const m of ms){const f=mtof(m);this.osc('triangle',f,w,dur,0.11*v,dur*1.6,this.mel);this.osc('sine',f*2,w,dur,0.035*v,dur*0.9,this.mel);}}
  brass(w,ms,dur,v=1){const c=this.ctx;for(const m of ms){const o=c.createOscillator(),f=c.createBiquadFilter(),g=c.createGain();o.type='sawtooth';o.frequency.value=mtof(m);f.type='lowpass';f.frequency.setValueAtTime(500,w);f.frequency.linearRampToValueAtTime(2600,w+0.04);f.frequency.exponentialRampToValueAtTime(700,w+dur);this.env(g,w,0.02,0.07*v,dur);o.connect(f);f.connect(g);g.connect(this.mel);o.start(w);o.stop(w+dur+0.1);}}
  pluck(w,m,dec,v=1){const f=mtof(m);this.osc('sawtooth',f,w,dec,0.045*v,dec,this.mel,null,0.01);this.osc('sine',f*2.01,w,dec,0.03*v,dec*0.7,this.mel);}
  tom(w,f,v=1){this.osc('sine',f,w,0.18,0.45*v,0.22,null,f*0.6);this.nz(w,0.06*v,0.05,'bandpass',f*6,1);}
  crash(w,v=1){this.nz(w,0.16*v,1.4,'highpass',5200,0.5);}
  lead(w,m,dur,kind,v=1){
    const c=this.ctx,f=mtof(m);
    const K={flute:{w:['sine','triangle'],x:[1,1],det:[0,4],cut:3800,a:0.05,pk:0.12,vib:5.2,vd:0.005,bre:0.02},
      bansuri:{w:['sine','triangle'],x:[1,1],det:[0,3],cut:3000,a:0.07,pk:0.12,vib:5,vd:0.008,bre:0.03,glide:true},
      violin:{w:['sawtooth','sawtooth'],x:[1,1],det:[-6,6],cut:2400,a:0.1,pk:0.055,vib:5.8,vd:0.008},
      bando:{w:['square','sawtooth'],x:[1,1],det:[-8,8],cut:1600,a:0.03,pk:0.05,vib:0,vd:0},
      sax:{w:['sawtooth','square'],x:[1,1],det:[0,4],cut:1400,a:0.035,pk:0.065,vib:5,vd:0.006},
      trumpet:{w:['sawtooth','sawtooth'],x:[1,1],det:[-3,3],cut:2000,a:0.025,pk:0.06,vib:5.5,vd:0.004,bite:true},
      vibes:{w:['sine','sine'],x:[1,4],det:[0,0],cut:6000,a:0.004,pk:0.14,vib:0,vd:0,perc:true}}[kind];
    const lp=c.createBiquadFilter(),g=c.createGain();lp.type='lowpass';lp.Q.value=0.7;
    if(K.bite){lp.frequency.setValueAtTime(K.cut*0.35,w);lp.frequency.linearRampToValueAtTime(K.cut,w+0.06);lp.frequency.setTargetAtTime(K.cut*0.6,w+0.1,dur);}
    else lp.frequency.value=K.cut;
    const pk=K.pk*v*(this.hv||1),hold=w+Math.max(K.a,dur*0.9),end=K.perc?w+dur*1.5+0.6:hold+0.4;
    g.gain.setValueAtTime(0.0001,w);g.gain.exponentialRampToValueAtTime(pk,w+K.a);
    if(K.perc)g.gain.exponentialRampToValueAtTime(0.0001,end);
    else{g.gain.setValueAtTime(pk*0.85,hold);g.gain.setTargetAtTime(0.0001,hold,0.06);}
    let lg=null;
    if(K.vib){const lfo=c.createOscillator();lg=c.createGain();lfo.frequency.value=K.vib;lg.gain.setValueAtTime(0,w);lg.gain.linearRampToValueAtTime(f*K.vd,w+Math.min(0.35,dur*0.6)+0.01);lfo.connect(lg);lfo.start(w);lfo.stop(end);}
    K.w.forEach((type,i)=>{const o=c.createOscillator(),og=c.createGain();o.type=type;o.detune.value=K.det[i];
      if(K.glide){o.frequency.setValueAtTime(f*0.97*K.x[i],w);o.frequency.exponentialRampToValueAtTime(f*K.x[i],w+0.07);}else o.frequency.value=f*K.x[i];
      if(lg)lg.connect(o.frequency);og.gain.value=i?0.5:1;o.connect(og);og.connect(lp);o.start(w);o.stop(end);});
    if(K.bre)this.nz(w,K.bre*v,0.12,'bandpass',f*2,2);
    lp.connect(g);g.connect(this.mel);
  }
  /* one lead note per rhythm slot; pitch walks through chord or scale tones near the centre pitch */
  melody(st,bar,s,w,sd,ch){
    const M=MEL[this.style];if(!M)return;
    if(((bar%16)+16)%16<2)return; /* let the band breathe for two bars every sixteen */
    const ph=((bar%8)+8)%8,motif=[0,0,1,0][ph>>1],half=ph&1;
    const rh=M.rh[half],slot=rh.findIndex(x=>x[0]===s);if(slot<0)return;
    const iv=M.scale||ch.iv.slice(0,4),root=M.scale?0:ch.r,pool=[];
    for(const o of [-12,0,12])for(const i of iv){const n=M.base-(M.base%12)+root+i+o;if(n>=M.base-7&&n<=M.base+12)pool.push(n);}
    pool.sort((a,b)=>a-b);
    const seed=motif*101+half*17+this.style.length*7;
    let idx=Math.floor(pool.length/2)+Math.round((rnd(seed)-0.5)*3);
    for(let i=0;i<=slot;i++)idx+=Math.round((rnd(seed+i*13+1)-0.5)*4);
    idx=Math.max(0,Math.min(pool.length-1,idx));
    let n=pool[idx];
    const last=slot===rh.length-1,cad=ph===7&&last;
    /* end each eight-bar phrase on the chord root */
    if(cad){const r=pool.filter(x=>((x-ch.r)%12+12)%12===0);if(r.length)n=r.reduce((a,b)=>Math.abs(b-n)<Math.abs(a-n)?b:a);}
    this.lead(w,n,rh[slot][1]*sd*(cad?1.6:0.95),M.v,slot===0?1:0.85);
  }
  tabla(w,kind,v=1){
    if(kind==='dha'||kind==='dhi'){this.osc('sine',95,w,0.25,0.6*v,0.4,null,72);this.osc('sine',520,w,0.3,0.25*v,kind==='dha'?0.5:0.3);}
    else if(kind==='ge'){this.osc('sine',78,w,0.25,0.6*v,0.45,null,115);}
    else if(kind==='na'){this.osc('sine',525,w,0.2,0.3*v,0.35);this.osc('sine',1050,w,0.1,0.08*v,0.15);}
    else {this.nz(w,0.25*v,0.04,'bandpass',2600,1.5);this.osc('sine',380,w,0.03,0.12*v,0.05);}
  }
  surdo(w,v=1){this.osc('sine',72,w,0.3,0.8*v,0.6,null,52);}
  tamborim(w,v=1){this.osc('square',880,w,0.01,0.05*v,0.05);this.nz(w,0.15*v,0.04,'bandpass',4200,2);}
  agogo(w,hi,v=1){this.osc('sine',hi?930:620,w,0.01,0.25*v,0.18);this.osc('sine',(hi?930:620)*2.7,w,0.01,0.04*v,0.08);}
  /* ---------- patterns ---------- */
  play(st,k,w,sd){
    const bar=Math.floor(k/st.bar),s=((k%st.bar)+st.bar)%st.bar;
    const P=st.prog,ch=P[((bar%P.length)+P.length)%P.length],nx=P[(((bar+1)%P.length)+P.length)%P.length];
    const tones=(c,base,n)=>c.iv.slice(0,n||c.iv.length).map(i=>base+c.r+i);
    const beat=sd*st.spb;
    const style=st.pat||this.style,ph=((bar%8)+8)%8;
    this.melody(st,bar,s,w,sd,ch);
    if(FILLS.has(this.style)){
      if(ph===0&&s===0&&bar>0)this.crash(w,0.8);
      /* drum fill into each new eight-bar phrase */
      const f0=Math.floor(st.bar*3/4),hop=Math.max(1,st.spb/2);
      if(ph===7&&s>=f0&&(s-f0)%hop===0){const u=(s-f0)/(st.bar-f0);this.tom(w,260-u*130,0.75);if(s>f0)this.snare(w,0.35);}
    }
    switch(style){
      case 'salsa':{
        const two=(bar&1)===0;
        if(two?(s===4||s===8):(s===0||s===6||s===12)) this.clave(w,0.9);
        if(s%4===0) this.cowbell(w,s===0?0.9:0.6);
        if(s===4) this.conga(w,330,0.7,true);
        if(s===12||s===14) this.conga(w,s===12?205:180,0.8);
        if(s===0||s===8) this.conga(w,190,0.25);
        if(s===6) this.bass(w,36+ch.r+7,beat*1.4,0.9);
        if(s===12) this.bass(w,36+nx.r,beat*1.8,1);
        if([0,3,6,8,11,14].includes(s)){const v=tones(ch,60,3);this.keys(w,s%2?[v[1]+12,v[2]+12]:[v[0]+12,v[2]+12,v[0]+24],sd*1.3,0.85);}
        break;}
      case 'swing':{
        if([0,3,5,6,9,11].includes(s)) this.ride(w,s%3===0?1:0.7);
        if(s===3||s===9){this.hat(w,0.6);this.brush(w,0.9);}
        if(s%3===0){this.kick(w,0.18);const i=s/3;const n=i===0?36+ch.r:i===1?36+ch.r+ch.iv[1]:i===2?36+ch.r+7:36+nx.r+((bar&1)?-1:1);this.bass(w,n,beat*0.9,0.9);}
        if(s===0||s===5) this.keys(w,tones(ch,60).map(x=>x>=72?x-12:x),sd*1.6,0.8);
        if((bar&1)&&s===11) this.brass(w,tones(nx,67,3),beat*0.5,1);
        break;}
      case 'lambada':{
        if(s===0||s===8||s===14) this.kick(w,s===14?0.6:1);
        if(s===4||s===12) this.snare(w,0.8);
        if(s%2===0) this.hat(w,0.5);
        else this.hat(w,0.18);
        if([0,3,6,8,11,14].includes(s)) this.bass(w,40+ch.r+((s===6||s===14)?7:0),sd*1.6,0.9);
        if(s%4===2) this.keys(w,tones(ch,64,3),sd*1.4,0.9);
        break;}
      case 'ballet':{
        if(s===0){this.bass(w,36+ch.r,beat*2.5,0.55);const top=tones(ch,72);this.keys(w,[top[bar%top.length]],beat*2.6,1.1);}
        if(s===2||s===4) this.keys(w,tones(ch,60,3).slice(1).concat([60+ch.r+12]),beat*0.8,0.65);
        if(s===5&&bar%2) this.keys(w,[72+nx.r],sd*1.5,0.5);
        break;}
      case 'indian':{
        const bols=['dha','ge','na','ti','na','ka','dhi','na'];
        if(s%4===0) this.tabla(w,bols[((bar&1)*4)+s/4],1);
        if(s%4===2&&(s===6||s===14)) this.tabla(w,'ti',0.5);
        if(s%4===0){const seq=[55,60,60,48];this.pluck(w,seq[s/4],beat*3.5,0.9);}
        break;}
      case 'break':{
        if(s===0||s===7||s===10) this.kick(w,s===7?0.7:1);
        if(s===4||s===12) this.snare(w,1);
        if(s%2===0) this.hat(w,s===14&&(bar&1)?0.7:0.45,s===14&&(bar&1));
        if(s===0) this.bass(w,36+ch.r,beat*1.4,1);
        if(s===7) this.bass(w,36+ch.r,sd*1.5,0.8);
        if(s===10) this.bass(w,36+ch.r+(ch.iv[1]),beat*1,0.9);
        if(s===0&&bar%2===0) this.keys(w,tones(ch,55),beat*6,0.45);
        break;}
      case 'bachata':{
        const t=tones(ch,57,3);
        this.pluck(w,t[s%3]+12+(s%8>=4?12:0),sd*2.2,0.55);
        if(s%2===0) this.nz(w,s%4===0?0.16:0.09,s%4===0?0.12:0.05,'highpass',6000,0.6);
        if(s%4===0) this.conga(w,s===12?330:420,s===12?0.8:0.35,s!==12);
        if(s===14) this.conga(w,300,0.7);
        if(s===0) this.bass(w,40+ch.r,beat*0.9,1);
        if(s===6) this.bass(w,40+ch.r+7,sd*1.5,0.8);
        if(s===8) this.bass(w,40+ch.r+12,beat*0.8,0.8);
        if(s===12) this.bass(w,40+ch.r+7,beat*0.9,1);
        if(s===12) this.kick(w,0.5);
        break;}
      case 'jive':{
        if(s===0||s===4) this.kick(w,1);
        if(s===2||s===6) this.snare(w,1);
        this.hat(w,s%2?0.3:0.5);
        const walk=[0,4,7,9,10,9,7,4];this.bass(w,36+ch.r+walk[s],sd*0.9,0.95);
        if(s%2===1) this.keys(w,tones(ch,60,4).map(x=>x>=72?x-12:x),sd*0.6,0.6);
        if(s===7&&bar%2) this.brass(w,tones(nx,67,3),sd*0.8,0.8);
        break;}
      case 'waltz':{
        if(s===0){this.bass(w,36+ch.r,beat*1.5,0.7);this.keys(w,[72+ch.r+ch.iv[bar%3]],beat*3,1);}
        if(s===2||s===4) this.keys(w,tones(ch,60,3).slice(1).concat([60+ch.r+12]),beat*0.7,0.6);
        if(s===3&&bar%2) this.keys(w,[72+ch.r+ch.iv[(bar+1)%3]],sd*1.5,0.6);
        break;}
      case 'tango':{
        if(s%2===0) this.keys(w,tones(ch,57,3),sd*0.5,s===0?1.2:0.8);
        if(s===0||s===4) this.bass(w,40+ch.r,sd*0.8,1);
        if(s===6||s===7) this.bass(w,40+ch.r+(s===6?7:5),sd*0.6,0.8);
        if(s===7&&bar%2) this.brass(w,tones(nx,64,3),sd*0.9,0.8);
        if(s===0) this.kick(w,0.5);
        break;}
      case 'chacha':{
        if(s%2===0) this.cowbell(w,s===0?0.9:0.55);
        if(s===6||s===7||s===0) this.nz(w,0.14,0.09,'bandpass',4500,1.5);
        if(s===6) this.conga(w,200,0.8); if(s===7) this.conga(w,200,0.8); if(s===2) this.conga(w,330,0.6,true);
        if(s===0) this.bass(w,40+ch.r,beat*1.2,1); if(s===3) this.bass(w,40+ch.r+7,beat*0.8,0.8); if(s===6) this.bass(w,40+ch.r,beat*0.8,0.9);
        if(s===1||s===3||s===5||s===7) this.keys(w,tones(ch,60,3),sd*0.7,0.7);
        break;}
      case 'rumba':{
        if(s%2===0) this.nz(w,0.08,0.07,'highpass',6000,0.7);
        if(s===0) this.bass(w,40+ch.r,beat*1.4,0.9); if(s===3) this.bass(w,40+ch.r+7,beat*0.5,0.7); if(s===4) this.bass(w,40+ch.r,beat*1.8,0.8);
        if(s===0) this.keys(w,tones(ch,60),beat*3.5,0.55);
        if(s===2||s===3) this.conga(w,s===2?380:300,0.5);
        if(s===6) this.conga(w,220,0.7);
        if(s===4) this.clave(w,0.5);
        break;}
      case 'paso':{
        this.snare(w,s%2===0?0.5:0.25);
        if(s===0||s===2) this.bass(w,40+ch.r+(s===2?7:0),beat*0.6,1);
        if(s===0) this.kick(w,0.8);
        if(s===0||s===1) this.brass(w,tones(ch,64,3),sd*0.8,s===0?1:0.7);
        break;}
      case 'samba':{
        if(s===4||s===12) this.surdo(w,1); if(s===0||s===8) this.surdo(w,0.3);
        if([0,2,3,5,7,8,10,11,13,15].includes(s)) this.tamborim(w,s%4===0?0.9:0.55);
        if([0,3,6,8,10,13].includes(s)) this.agogo(w,!(s===6||s===13),0.6);
        this.hat(w,0.12);
        if([0,3,6,10,12,14].includes(s)) this.keys(w,tones(ch,67,3),sd*0.9,0.7);
        break;}
    }
  }
}
window.Music=Music;window.MUSIC_STYLES=STYLES;window.MUSIC_TRACKS=TRACKS;
})();
