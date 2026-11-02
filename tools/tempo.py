import sys,numpy as np
sys.path.insert(0,'.')
from lib import load,CMU,CM,CAN
J={n:i for i,n in enumerate(CAN)}
def onset_sig(arrs,fps):
    sig=0
    for p in arrs:
        for a in ['lAn','rAn']:
            y=p[:,J[a],1]; v=np.gradient(y)*fps
            acc=np.gradient(v)*fps
            sig=sig+np.clip(acc,0,None)*(y<np.percentile(y,60))  # landing deceleration near floor
    return sig
def tempo(arrs,fps,lo=70,hi=150):
    sig=onset_sig(arrs,fps); sig=sig-sig.mean(); n=len(sig)
    N=8*n; F=np.abs(np.fft.rfft(sig*np.hanning(n),N))**2; fr=np.fft.rfftfreq(N,1/fps)*60
    m=(fr>=lo)&(fr<=hi); 
    # add harmonic (2x) support
    score=F[m].copy()
    for k,f in enumerate(fr[m]):
        i2=np.argmin(np.abs(fr-2*f)); score[k]+=0.5*F[i2]
    bpm=fr[m][np.argmax(score)]; T=60/bpm
    t=np.arange(n)/fps; w=np.clip(sig,0,None)
    ph=np.angle((w*np.exp(2j*np.pi*t/T)).sum()); off=((ph/(2*np.pi))*T)%T
    return round(float(bpm),1),round(float(off),3)
if __name__=='__main__':
    import os;D=os.environ.get('CMU_DIR','cmu/data')+'/'
    for s in ['060/60_01','060/60_08','060/60_03','093/93_03','093/93_06','093/93_08','055/55_02','094/94_01','094/94_05','085/85_03','085/85_04','005/05_09']:
        p,fps=load(D+s+'.bvh',CMU,CM); ex=[p]
        if s.startswith('060'): q,_=load(D+s.replace('060/60','061/61')+'.bvh',CMU,CM); n=min(len(p),len(q)); ex=[p[:n],q[:n]]
        print(s,tempo(ex,fps,70,150),tempo(ex,fps,140,220))
