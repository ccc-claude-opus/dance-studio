"""Rule-based choreography generator for dances with no free mocap (bachata, jive).
Produces the same 22-joint position format as the mocap clips, so the page renders them identically.
Steps follow the standard syllabus counts; legs/arms are solved with 2-bone IK so feet plant on the floor."""
import numpy as np
from lib import CAN
J={n:i for i,n in enumerate(CAN)}
FPS=30
THIGH,SHIN=0.43,0.42
UPARM,FORE,HAND=0.29,0.26,0.09

def ease(x): x=np.clip(x,0,1); return x*x*x*(x*(6*x-15)+10)   # minimum-jerk profile

class Track:
    """keyframes (t_beats, value); value is np.array"""
    def __init__(s,v0): s.k=[(-1e9,np.array(v0,float))]
    def add(s,t,v): s.k.append((t,np.array(v,float))); s.k.sort(key=lambda a:a[0])
    def at(s,t,dur=None):
        k=s.k
        for i in range(len(k)-1,-1,-1):
            if k[i][0]<=t:
                if i+1<len(k):
                    t0,v0=k[i];t1,v1=k[i+1]
                    return v0 if t<t1-(dur or (t1-t0)) else v0+(v1-v0)*ease((t-(t1-(dur or (t1-t0))))/(dur or (t1-t0)))
                return k[i][1]
        return k[0][1]

class Dancer:
    def __init__(s,pos,heading,scale=1.0):
        s.sc=scale
        s.head=Track([heading])
        f=np.array([np.cos(heading),np.sin(heading)]); l=np.array([f[1],-f[0]])
        p=np.array(pos,float)
        s.foot={'l':Track([*(p+l*0.09),0.0]),'r':Track([*(p-l*0.09),0.0])}   # x,z,height
        s.moves={'l':[], 'r':[]}   # (t_land, dur) for arcs
        s.w=Track([0.5])           # 0 = on left, 1 = on right
        s.hip=Track([0.0])         # cuban hip accent (-1..1, + = right hip out)
        s.bounce=0.0; s.lean=0.0
        s.rise=Track([0.0]); s.sway=Track([0.0]); s.knee=0.0
    def fwd(s,t): h=s.head.at(t)[0]; return np.array([np.cos(h),np.sin(h)])
    def left(s,t): f=s.fwd(t); return np.array([f[1],-f[0]])
    def cur(s,side,t): return s.foot[side].at(t)
    def step(s,side,t,xz,dur=0.6,weight=True,h=0.0,wdur=0.25):
        s.foot[side].add(t,[xz[0],xz[1],h]); s.moves[side].append((t,dur))
        if weight: s.w.add(t, [0.0 if side=='l' else 1.0]); s.wdur=wdur
    def hold_foot(s,side,t): v=s.foot[side].at(t); s.foot[side].add(t,v)

def foot_pos(d,side,t):
    tr=d.foot[side]; k=tr.k
    # find surrounding keys
    i=max(j for j in range(len(k)) if k[j][0]<=t)
    if i+1<len(k):
        t0,v0=k[i];t1,v1=k[i+1]
        dur=next((du for (tl,du) in d.moves[side] if abs(tl-t1)<1e-6),t1-t0)
        dur=min(dur*1.35,t1-t0) if t1-t0>0 else dur
        st=t1-dur
        if t<st: v=v0
        else:
            u=(t-st)/dur; e=ease(u); v=v0+(v1-v0)*e
            dist=np.hypot(*(v1[:2]-v0[:2]))
            if v0[2]<0.01 and v1[2]<0.01 and dist>0.03: v=v.copy(); v[2]+=min(0.055,0.22*dist)*np.sin(np.pi*u)**1.5
    else: v=k[i][1]
    return v

def ik2(a,target,l1,l2,pole):
    d=target-a; L=np.linalg.norm(d)
    L=min(L,(l1+l2)*0.999); L=max(L,abs(l1-l2)+1e-3)
    dn=d/ (np.linalg.norm(d)+1e-9)
    end=a+dn*L
    x=(l1*l1-l2*l2+L*L)/(2*L); y=np.sqrt(max(l1*l1-x*x,0))
    p=pole-np.dot(pole,dn)*dn; p/= (np.linalg.norm(p)+1e-9)
    mid=a+dn*x+p*y
    return mid,end

def body(d,t):
    """lower body + torso joints (world, meters) at beat time t"""
    sc=d.sc; P={}
    h=d.head.at(t)[0]; f3=np.array([np.cos(h),0,np.sin(h)]); l3=np.array([np.sin(h),0,-np.cos(h)]); up=np.array([0,1,0.])
    fl=foot_pos(d,'l',t); fr=foot_pos(d,'r',t)
    w=float(d.w.at(t,dur=0.5)[0])
    gl=np.array([fl[0],0,fl[1]]); gr=np.array([fr[0],0,fr[1]])
    base=gl*(1-w)+gr*w
    hip=float(d.hip.at(t,dur=0.35)[0])
    support=(gr if w>0.5 else gl)
    base=base+(support-base)*0.15 + l3*(-hip*0.035)
    frac=t-np.floor(t)
    rise=float(d.rise.at(t,dur=0.6)[0]); sway=float(d.sway.at(t,dur=0.6)[0])
    py=0.95*sc - 0.025 - d.knee - d.bounce*(0.5+0.5*np.cos(2*np.pi*frac)) + rise*0.045*sc
    hipw=0.095*sc
    # pelvis tilt from hip accent
    hl_y=-0.06*sc - hip*0.025; hr_y=-0.06*sc + hip*0.025
    # reach constraint
    for side,fp,hy,sg in (('l',fl,hl_y,1),('r',fr,hr_y,-1)):
        a3=np.array([fp[0],0.08*sc+fp[2]+rise*0.045*sc,fp[1]])
        wt=(1-w) if side=='l' else w
        if wt<0.3 or fp[2]>0.02: continue
        hj=base+l3*hipw*sg
        hz=np.hypot(*(hj[[0,2]]-a3[[0,2]]))
        maxy=a3[1]+np.sqrt(max((THIGH+SHIN)*sc*0.985,hz+1e-3)**2-hz*hz)-hy
        py=min(py,maxy)
    pel=np.array([base[0],py,base[2]])
    P['hips']=pel
    P['lHip']=pel+l3*hipw+up*hl_y; P['rHip']=pel-l3*hipw+up*hr_y
    lean=d.lean
    tup=(up+f3*lean+l3*sway*0.12); tup/=np.linalg.norm(tup)
    P['spine']=pel+tup*0.11*sc; P['chest']=P['spine']+tup*0.12*sc - l3*hip*0.01
    P['neck']=P['chest']+tup*0.22*sc; P['head']=P['neck']+tup*0.07*sc+f3*0.01; P['headTop']=P['head']+tup*0.2*sc
    fd=np.dot(np.array([fl[0]-fr[0],0,fl[1]-fr[1]]),f3); tw=float(np.clip(-fd*0.35,-0.14,0.14))
    l3t=l3*np.cos(tw)+f3*np.sin(tw)
    P['lSh']=P['chest']+tup*0.15*sc+l3t*0.18*sc; P['rSh']=P['chest']+tup*0.15*sc-l3t*0.18*sc
    for side,fp in (('l',fl),('r',fr)):
        an=np.array([fp[0],0.08*sc+fp[2]+(rise*0.045*sc if fp[2]<=0.02 else 0),fp[1]])
        if fp[2]>0.02:  # airborne: foot pointed, set from explicit kick target
            pass
        knee,ank=ik2(P[side+'Hip'],an,THIGH*sc,SHIN*sc,f3+up*0.1)
        P[side+'Kn']=knee; P[side+'An']=ank
        toe_dir=f3.copy()
        if fp[2]>0.02: toe_dir=(ank-knee); toe_dir=toe_dir/np.linalg.norm(toe_dir)*0.6+f3*0.4
        P[side+'Toe']=ank+toe_dir/np.linalg.norm(toe_dir)*0.17*sc + np.array([0,-(0.06+rise*0.045)*sc,0])*(fp[2]<=0.02)
    P['_f3']=f3; P['_l3']=l3; P['_up']=tup
    return P

def gsmooth(x,sig):
    if sig<=0: return x
    r=int(3*sig); k=np.exp(-0.5*(np.arange(-r,r+1)/sig)**2); k/=k.sum()
    pad=np.concatenate([np.repeat(x[:1],r,0),x,np.repeat(x[-1:],r,0)],0)
    out=np.zeros_like(x)
    for i,w in enumerate(k): out+=w*pad[i:i+len(x)]
    return out
def refine(A,sc):
    """Smooth the body's centre and upper body over time, then re-solve knees and elbows so bones keep their length
    and planted feet stay put. Removes the stop-start look of keyframed steps."""
    J_=J; X=A.copy()
    core=['hips','spine','chest','neck','head','headTop','lSh','rSh','lHip','rHip']
    for n in core:
        X[:,J_[n],0::2]=gsmooth(A[:,J_[n],0::2],2.4); X[:,J_[n],1]=gsmooth(A[:,J_[n],1:2],1.0)[:,0]
    for n in ['lWr','rWr','lHd','rHd']: X[:,J_[n]]=gsmooth(A[:,J_[n]],1.6)
    for i in range(len(X)):
        for s_ in 'lr':
            h=X[i,J_[s_+'Hip']]; an=A[i,J_[s_+'An']]; pole=A[i,J_[s_+'Kn']]-(h+an)/2
            kn,an2=ik2(h,an,THIGH*sc,SHIN*sc,pole)
            X[i,J_[s_+'Kn']]=kn; d_=an2-an; X[i,J_[s_+'An']]=an2; X[i,J_[s_+'Toe']]=A[i,J_[s_+'Toe']]+d_
            S_=X[i,J_[s_+'Sh']]; wr=X[i,J_[s_+'Wr']]; pole=A[i,J_[s_+'El']]-(S_+wr)/2
            el,wr2=ik2(S_,wr,UPARM*sc,FORE*sc,pole)
            X[i,J_[s_+'El']]=el; X[i,J_[s_+'Hd']]+=wr2-wr; X[i,J_[s_+'Wr']]=wr2
    return X

def arm(P,side,target,sc):
    S=P[side+'Sh']; l3=P['_l3']; sg=1 if side=='l' else -1
    pole=-P['_up']*0.7+l3*sg*0.6-P['_f3']*0.2
    el,wr=ik2(S,target,UPARM*sc,FORE*sc,pole)
    P[side+'El']=el;P[side+'Wr']=wr
    dv=wr-el; dv/=np.linalg.norm(dv)
    P[side+'Hd']=wr+dv*HAND*sc

def free_arm(P,side,sc,t,style):
    f3=P['_f3'];l3=P['_l3'];up=np.array([0,1,0.]);sg=1 if side=='l' else -1
    if style=='jive': tgt=P[side+'Sh']+l3*sg*0.32*sc-up*0.12*sc+f3*0.1*sc+up*0.03*np.sin(np.pi*2*t)
    elif style=='up': tgt=P[side+'Sh']+l3*sg*0.45*sc+up*0.22*sc+f3*0.05*sc
    elif style=='paso': tgt=P[side+'Sh']+l3*sg*0.35*sc+up*0.08*sc-f3*0.05*sc
    elif style=='turn': tgt=P[side+'Sh']+l3*sg*0.15*sc-up*0.30*sc+f3*0.18*sc
    else: tgt=P[side+'Sh']+l3*sg*0.22*sc-up*0.42*sc+f3*0.1*sc
    arm(P,side,tgt,sc)

def render(lead,fol,beats,bpm,holds):
    """holds(t)->dict(mode,raise) mode in closed/open/release/turnL/turnF"""
    spb=60/bpm; F=int(beats*spb*FPS)
    A=np.zeros((F,len(CAN),3)); B=np.zeros((F,len(CAN),3))
    for i in range(F):
        t=i/FPS/spb
        PL=body(lead,t); PF=body(fol,t); hd=holds(t); m=hd['mode']; r=hd.get('raise',0.0)
        if m=='standard':
            back=PF['chest']+PF['_l3']*0.1*fol.sc-PF['_f3']*0.12*fol.sc+np.array([0,0.04,0])
            arm(PL,'r',back,lead.sc)
            j=PL['lSh']+PL['_l3']*0.26+PL['_f3']*0.2+np.array([0,0.04+0.5*r,0])
            arm(PL,'l',j,lead.sc); arm(PF,'r',j,fol.sc)
            arm(PF,'l',PL['rSh']-PL['_l3']*0.06+np.array([0,-0.02,0]),fol.sc)
        elif m=='two':
            mid=(PL['chest']+PF['chest'])/2; mid[1]=1.0
            arm(PL,'l',mid+PL['_l3']*0.2,lead.sc); arm(PF,'r',mid+PL['_l3']*0.2,fol.sc)
            arm(PL,'r',mid-PL['_l3']*0.2,lead.sc); arm(PF,'l',mid-PL['_l3']*0.2,fol.sc)
        elif m=='closed':
            c=(PL['chest']+PF['chest'])/2
            back=PF['chest']+PF['_l3']*0.08*fol.sc-PF['_f3']*0.11*fol.sc+np.array([0,0.02,0])
            arm(PL,'r',back,lead.sc)
            j=c+PL['_l3']*0.36+np.array([0,0.0+0.85*r,0])
            arm(PL,'l',j,lead.sc); arm(PF,'r',j,fol.sc)
            arm(PF,'l',PL['rSh']+PL['_f3']*(-0.02)+np.array([0,-0.03,0]),fol.sc)
        else:
            mid=(PL['hips']+PF['hips'])/2
            j=mid+PL['_l3']*0.08+np.array([0,0.0,0])
            j[1]=1.0+0.9*r
            if m=='release':
                free_arm(PL,'l',lead.sc,t,hd.get('free','jive'));free_arm(PF,'r',fol.sc,t,'turn' if r>0 else hd.get('free','jive'))
            else:
                arm(PL,'l',j,lead.sc); arm(PF,'r',j,fol.sc)
            free_arm(PL,'r',lead.sc,t,hd.get('free','jive')); free_arm(PF,'l',fol.sc,t,hd.get('free','jive'))
        for P,O in ((PL,A),(PF,B)):
            for n in CAN: O[i,J[n]]=P[n]
    return refine(A,lead.sc),refine(B,fol.sc)
