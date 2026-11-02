import numpy as np
from gen import Dancer, render, FPS

def V(*a): return np.array(a,float)

class S:
    """step scripting for one dancer; remembers last floor positions"""
    def __init__(s,d,first):  # first: the foot this dancer leads with ('l' for lead, 'r' for follow)
        s.d=d; s.a=first; s.b='r' if first=='l' else 'l'
        s.p={'l':d.foot['l'].k[-1][1][:2].copy(),'r':d.foot['r'].k[-1][1][:2].copy()}
        s.h=d.head.k[-1][1][0]
    def left(s,h=None):
        h=s.h if h is None else h; return V(np.sin(h),-np.cos(h))
    def fwd(s,h=None):
        h=s.h if h is None else h; return V(np.cos(h),np.sin(h))
    def step(s,side,t,xz,dur=0.6,w=True):
        s.d.step(side,t,xz,dur=dur,weight=w); s.p[side]=np.array(xz,float)
    def air(s,side,t,xz,h,dur=0.35):
        s.d.foot[side].add(t,[xz[0],xz[1],h]); s.d.moves[side].append((t,dur))
    def beside(s,side,other,gap=0.17,h=None):
        sg=1 if side=='l' else -1
        return s.p[other]+s.left(h)*gap*sg
    def turn_to(s,t0,t1,h1):
        s.d.head.add(t0,[s.h]); s.d.head.add(t1,[h1]); s.h=h1
    def hip(s,t,v,back=0.6):
        s.d.hip.add(t,[0.0]); s.d.hip.add(t+0.01,[v]); s.d.hip.add(t+back,[0.0])

# ---------------- BACHATA ----------------
def bachata():
    bpm=128.0
    L=Dancer((-0.17,0),0.0,1.0); F=Dancer((0.17,0),np.pi,0.93)
    sl,sf=S(L,'l'),S(F,'r')
    holds=[]  # (t0,t1,mode,raise)
    def side_half(s,t0,first,sv,size=0.21):
        o='r' if first=='l' else 'l'
        s.step(first,t0,s.p[first]+sv*size)
        s.step(o,t0+1,s.beside(o,first,0.17))
        s.step(first,t0+2,s.p[first]+sv*size)
        s.step(o,t0+3,s.beside(o,first,0.12),w=False)
        s.hip(t0+3,-1 if first=='l' else 1)
    def side_basic(t0):
        sv=sl.left()
        side_half(sl,t0,'l',sv); side_half(sf,t0,'r',sv)
        side_half(sl,t0+4,'r',-sv); side_half(sf,t0+4,'l',-sv)
    def fb_half(s,t0,first,fv,size=0.2):
        o='r' if first=='l' else 'l'
        s.step(first,t0,s.p[first]+fv*size)
        s.step(o,t0+1,s.p[o].copy())
        s.step(first,t0+2,s.beside(first,o,0.17))
        s.step(o,t0+3,s.beside(o,first,0.12),w=False)
        s.hip(t0+3,-1 if first=='l' else 1)
    def fb_basic(t0):
        fv=sl.fwd()
        fb_half(sl,t0,'l',fv); fb_half(sf,t0,'r',fv)
        fb_half(sl,t0+4,'r',-fv); fb_half(sf,t0+4,'l',-fv)
    def spin_steps(s,t0,sides,total,travel):
        """steps on counts t0, t0+1, t0+2 turning by total radians, tap on t0+3"""
        h0=s.h; pv=(s.p['l']+s.p['r'])/2
        s.turn_to(t0-0.2,t0+2.7,h0+total)
        for k,side in enumerate(sides):
            tt=t0+k; hk=h0+total*min(1,(k+0.7)/3)
            pv=pv+travel/3
            sg=1 if side=='l' else -1
            s.step(side,tt,pv+s.left(hk)*0.06*sg,dur=0.55)
        o=sides[2]; tap='l' if o=='r' else 'r'
        s.step(tap,t0+3,s.p[o]+s.left(h0+total)*0.12*(1 if tap=='l' else -1),w=False)
        s.h=h0+total
    def follow_turn(t0,dirn):
        sv=sl.left()
        side_half(sl,t0,'l',sv); side_half(sf,t0,'r',sv)
        side_half(sl,t0+4,'r',-sv)
        spin_steps(sf,t0+4,['l','r','l'] if dirn<0 else ['r','l','r'],dirn*2*np.pi,-sv*0.42)
        holds.append((t0+3.3,t0+7.6,'open',1.0))
    def lead_turn(t0):
        sv=sl.left()
        side_half(sl,t0,'l',sv); side_half(sf,t0,'r',sv)
        side_half(sf,t0+4,'l',-sv)
        spin_steps(sl,t0+4,['r','l','r'],-2*np.pi,-sv*0.42)
        holds.append((t0+3.3,t0+7.6,'release',0.0))
    L.bounce=0.012; F.bounce=0.012; L.lean=0.03; F.lean=0.03
    figs=[]
    def fig(key,t0,t1): figs.append((key,t0,t1))
    side_basic(0); side_basic(8); fig('b_side',0,16)
    fb_basic(16); fb_basic(24); fig('b_fb',16,32)
    follow_turn(32,1); fig('b_rturn',32,40)
    side_basic(40)
    follow_turn(48,-1); fig('b_lturn',48,56)
    side_basic(56)
    lead_turn(64); fig('b_lead',64,72)
    side_basic(72)
    end=80
    def H(t):
        for a,b,m,r in holds:
            if a<=t<b:
                rr=r*min(1,(t-a)/0.6,(b-t)/0.6)
                return {'mode':m,'raise':rr,'free':'turn'}
        return {'mode':'closed','raise':0}
    A,B=render(L,F,end,bpm,H)
    return A,B,bpm,figs

# ---------------- JIVE ----------------
def jive():
    bpm=172.0
    L=Dancer((-0.4,0),0.0,1.0); F=Dancer((0.4,0),np.pi,0.93)
    sl,sf=S(L,'l'),S(F,'r')
    L.bounce=0.03; F.bounce=0.03; L.lean=0.09; F.lean=0.09
    holds=[]
    D=0.36  # dur for quick steps (beats)
    def chasse(s,t0,first,sv,size=0.12):
        o='r' if first=='l' else 'l'
        s.step(first,t0,s.p[first]+sv*size,dur=D)
        s.step(o,t0+0.75,s.beside(o,first,0.15),dur=0.3)
        s.step(first,t0+1,s.p[first]+sv*size*0.7,dur=0.25)
    def rock(s,t0,first,bv):
        o='r' if first=='l' else 'l'
        s.step(first,t0,s.beside(first,o,0.17)+bv*0.14,dur=D)
        s.step(o,t0+1,s.p[o].copy(),dur=0.3)
        s.step(first,t0+1.9,s.beside(first,o,0.17),dur=0.4,w=False)
    def basic(t0):
        sv=sl.left(); bv=-sl.fwd()
        chasse(sl,t0,'l',sv); chasse(sf,t0,'r',sv)
        chasse(sl,t0+2,'r',-sv); chasse(sf,t0+2,'l',-sv)
        rock(sl,t0+4,'l',bv); rock(sf,t0+4,'r',-bv)
    def place_on_arc(s,t,pivot,h,side,dur=D,w=True):
        sg=1 if side=='l' else -1
        s.step(side,t,pivot+s.left(h)*0.08*sg,dur=dur,w=w)
    def change_places(t0):
        # both travel half a circle around the pair centre; follow adds a full underarm turn
        c=(sl.p['l']+sl.p['r']+sf.p['l']+sf.p['r'])/4
        rl=(sl.p['l']+sl.p['r'])/2-c; rf=(sf.p['l']+sf.p['r'])/2-c
        hl0,hf0=sl.h,sf.h
        chasse(sl,t0,'l',sl.left()*0.5); chasse(sf,t0,'r',sl.left()*0.5)
        def rot(v,a): c_,s_=np.cos(a),np.sin(a); return V(v[0]*c_-v[1]*s_, v[0]*s_+v[1]*c_)
        times=[(t0+2,'r','l'),(t0+2.75,'l','r'),(t0+3,'r','l')]
        for k,(tt,ls,fs) in enumerate(times):
            u=(k+1)/3; a=np.pi*u
            place_on_arc(sl,tt,c+rot(rl,a),hl0+a,ls)
            place_on_arc(sf,tt,c+rot(rf,a),hf0+a+2*np.pi*u,fs)
        sl.turn_to(t0+1.6,t0+3.4,hl0+np.pi); sf.turn_to(t0+1.6,t0+3.4,hf0+3*np.pi)
        rock(sl,t0+4,'l',-sl.fwd()); rock(sf,t0+4,'r',-sf.fwd())
        holds.append((t0+0.8,t0+3.8,'open',1.0))
    def kick_ball_change(s,t0,a,fv):
        b='r' if a=='l' else 'l'
        base=s.beside(a,b,0.17)
        s.air(a,t0,base+fv*0.32,0.16,dur=0.45)
        s.step(a,t0+0.75,base,dur=0.3)
        s.step(b,t0+1,s.p[b].copy(),dur=0.25)
    def flick(s,t0,a,fv):
        b='r' if a=='l' else 'l'; base=s.beside(a,b,0.17)
        s.air(a,t0,base+fv*0.08,0.22,dur=0.4)
        s.air(a,t0+0.5,base+fv*0.36,0.26,dur=0.22)
        s.air(a,t0+1,base+fv*0.08,0.22,dur=0.3)
        s.air(a,t0+1.5,base+fv*0.36,0.26,dur=0.22)
        s.step(a,t0+2,base,dur=0.35)
    def kicks_flicks(t0):
        fl,ff=sl.fwd(),sf.fwd()
        for k in (0,2):
            kick_ball_change(sl,t0+k,'l',fl); kick_ball_change(sf,t0+k,'r',ff)
        flick(sl,t0+4,'l',fl); flick(sf,t0+4,'r',ff)
        sl.step('r',t0+7,sl.p['r'].copy(),dur=0.3); sf.step('l',t0+7,sf.p['l'].copy(),dur=0.3)
    def american_spin(t0):
        sv=sl.left()
        chasse(sl,t0,'l',sv*0.5); chasse(sf,t0,'r',sv*0.5)
        chasse(sl,t0+2,'r',-sv*0.5)
        h0=sf.h; pv=(sf.p['l']+sf.p['r'])/2
        sf.turn_to(t0+1.8,t0+3.6,h0+2*np.pi)
        for tt,side,u in ((t0+2,'l',0.35),(t0+2.75,'r',0.7),(t0+3,'l',1.0)):
            place_on_arc(sf,tt,pv,h0+2*np.pi*u,side)
        rock(sl,t0+4,'l',-sl.fwd()); rock(sf,t0+4,'r',-sf.fwd())
        holds.append((t0+1.6,t0+4.0,'release',1.0))
    figs=[]
    def fig(k,a,b): figs.append((k,a,b))
    basic(0); basic(6); fig('j_basic',0,12)
    change_places(12); fig('j_change',12,18)
    basic(18)
    kicks_flicks(24); fig('j_kicks',24,32)
    basic(32)
    american_spin(38); fig('j_spin',38,44)
    basic(44)
    change_places(50); fig('j_change2',50,56)
    basic(56)
    end=62
    def H(t):
        for a,b,m,r in holds:
            if a<=t<b: return {'mode':m,'raise':r*min(1,(t-a)/0.5,(b-t)/0.5),'free':'jive' if m=='open' else 'turn'}
        return {'mode':'open','raise':0,'free':'jive'}
    A,B=render(L,F,end,bpm,H)
    return A,B,bpm,figs
