"""International ballroom (Standard + Latin) generated from syllabus step timing.
A Couple keeps a shared frame (centre C, heading H = lead's facing). Each event moves the lead's foot and,
by default, the follow's opposite foot by the same world displacement (closed-position opposition)."""
import numpy as np
from gen import Dancer, render

def V(*a): return np.array(a,float)
def rot(h): return V(np.cos(h),np.sin(h)), V(np.sin(h),-np.cos(h))   # forward, left

class Couple:
    def __init__(s,bpm,d=0.17,o=0.06,hold='standard'):
        s.bpm=bpm; s.d=d; s.o=o; s.C=V(0,0); s.H=0.0
        s.L=Dancer(tuple(s.lc(s.C,s.H)),s.H,1.0); s.F=Dancer(tuple(s.fc(s.C,s.H)),s.H+np.pi,0.93)
        s.Lh=s.H; s.Fh=s.H+np.pi
        s.holds=[]; s.default=hold; s.figs=[]; s.t=0.0
    def lc(s,C,H,d=None,o=None):
        f,l=rot(H); return C-f*(s.d if d is None else d)+l*(s.o if o is None else o)
    def fc(s,C,H,d=None,o=None):
        f,l=rot(H); return C+f*(s.d if d is None else d)-l*(s.o if o is None else o)
    def ev(s,t,lf,dC=(0,0),dH=0.0,ex=(0,0),w=True,dur=0.6,ff=None,fex=None,lh=None,fh=None,lpos=None,fpos=None,who='both',spread=0.09):
        """t beats; lf lead foot; dC centre move in couple frame (fwd,left); dH turn of couple (rad, + = counterclockwise seen from above? we use + = right/clockwise)
        ex extra foot offset in couple frame applied to both; lh/fh absolute headings; lpos/fpos absolute body centres"""
        f,l=rot(s.H); s.C=s.C+f*dC[0]+l*dC[1]; s.H=s.H+dH
        f2,l2=rot(s.H); exw=f2*ex[0]+l2*ex[1]
        Lh=s.H if lh is None else lh; Fh=s.H+np.pi if fh is None else fh
        if who in('both','lead'):
            pc=s.lc(s.C,s.H) if lpos is None else lpos
            _,ll=rot(Lh); sg=1 if lf=='l' else -1
            s.L.head.add(t-dur*0.9,[s.Lh]); s.L.head.add(t,[Lh]); s.Lh=Lh
            s.L.step(lf,t,pc+ll*spread*sg+exw,dur=dur,weight=w)
        if who in('both','follow'):
            fo=ff or ('r' if lf=='l' else 'l')
            pc=s.fc(s.C,s.H) if fpos is None else fpos
            _,fl=rot(Fh); sg=1 if fo=='l' else -1
            fx=exw if fex is None else (f2*fex[0]+l2*fex[1])
            s.F.head.add(t-dur*0.9,[s.Fh]); s.F.head.add(t,[Fh]); s.Fh=Fh
            s.F.step(fo,t,pc+fl*spread*sg+fx,dur=dur,weight=w)
    def rise(s,t,v):
        for D in (s.L,s.F): D.rise.add(t,[v])
    def sway(s,t,v):
        s.L.sway.add(t,[v]); s.F.sway.add(t,[-v])
    def hip(s,t,v,back=0.5):
        for D,sg in ((s.L,1),(s.F,-1)): D.hip.add(t,[0.0]); D.hip.add(t+0.01,[v*sg]); D.hip.add(t+back,[0.0])
    def hold(s,a,b,mode,r=0.0,free='jive'): s.holds.append((a,b,mode,r,free))
    def fig(s,key,a,b): s.figs.append((key,a,b))
    def run(s,end):
        def H(t):
            for a,b,m,r,fr in s.holds:
                if a<=t<b: return {'mode':m,'raise':r*min(1,(t-a)/0.5,(b-t)/0.5),'free':fr}
            return {'mode':s.default,'raise':0,'free':'jive'}
        A,B=render(s.L,s.F,end,s.bpm,H)
        return A,B,s.bpm,s.figs

R=np.radians

# ---------------- STANDARD ----------------
def waltz():
    c=Couple(90); t=0.0
    for D in (c.L,c.F): D.lean=0.02
    def closed_change(t,lf):
        o='r' if lf=='l' else 'l'
        c.ev(t,lf,dC=(0.42,0),dur=0.9); c.rise(t+0.6,0.0); c.rise(t+0.95,0.6)
        c.ev(t+1,o,dC=(0.1,(-0.24 if lf=='l' else 0.24)),dur=0.8); c.rise(t+1.6,1.0)
        c.ev(t+2,lf,dur=0.7); c.rise(t+2.9,0.0)
        c.sway(t+1,0.6 if lf=='l' else -0.6); c.sway(t+2.9,0)
    def natural_turn(t):   # right turn, 3/8 per bar, two bars
        c.ev(t,'r',dC=(0.38,0),dH=R(45),dur=0.9); c.rise(t+0.95,0.6)
        c.ev(t+1,'l',dC=(0.05,-0.26),dH=R(60),dur=0.8); c.rise(t+1.6,1.0)
        c.ev(t+2,'r',dH=R(30),dur=0.7); c.rise(t+2.9,0.0)
        c.ev(t+3,'l',dC=(-0.38,0),dH=R(45),dur=0.9); c.rise(t+3.95,0.6)
        c.ev(t+4,'r',dC=(-0.05,0.26),dH=R(60),dur=0.8); c.rise(t+4.6,1.0)
        c.ev(t+5,'l',dH=R(30),dur=0.7); c.rise(t+5.9,0.0)
        c.sway(t+1,-0.6); c.sway(t+2.9,0); c.sway(t+4,0.6); c.sway(t+5.9,0)
    def reverse_turn(t):
        c.ev(t,'l',dC=(0.38,0),dH=-R(45),dur=0.9); c.rise(t+0.95,0.6)
        c.ev(t+1,'r',dC=(0.05,0.26),dH=-R(60),dur=0.8); c.rise(t+1.6,1.0)
        c.ev(t+2,'l',dH=-R(30),dur=0.7); c.rise(t+2.9,0.0)
        c.ev(t+3,'r',dC=(-0.38,0),dH=-R(45),dur=0.9); c.rise(t+3.95,0.6)
        c.ev(t+4,'l',dC=(-0.05,-0.26),dH=-R(60),dur=0.8); c.rise(t+4.6,1.0)
        c.ev(t+5,'r',dH=-R(30),dur=0.7); c.rise(t+5.9,0.0)
        c.sway(t+1,0.6); c.sway(t+2.9,0); c.sway(t+4,-0.6); c.sway(t+5.9,0)
    def box(t):
        c.ev(t,'l',dC=(0.3,0),dur=0.8); c.ev(t+1,'r',dC=(0,-0.22),dur=0.7); c.ev(t+2,'l',dur=0.6)
        c.ev(t+3,'r',dC=(-0.3,0),dur=0.8); c.ev(t+4,'l',dC=(0,0.22),dur=0.7); c.ev(t+5,'r',dur=0.6)
        for k in (0,3): c.rise(t+k+0.9,0.5); c.rise(t+k+1.8,0.9); c.rise(t+k+2.9,0)
    box(0); box(6); c.fig('w_box',0,12)
    closed_change(12,'r'); closed_change(15,'l'); c.fig('w_change',12,18)
    natural_turn(18); c.fig('w_natural',18,24)
    closed_change(24,'l')
    reverse_turn(27); c.fig('w_reverse',27,33)
    closed_change(33,'r')
    return c.run(36.5)

def vwaltz():
    c=Couple(174);
    for D in (c.L,c.F): D.lean=0.03
    def nat(t):
        c.ev(t,'r',dC=(0.3,0),dH=R(60),dur=0.7); c.ev(t+1,'l',dC=(0,-0.2),dH=R(60),dur=0.6); c.ev(t+2,'r',dH=R(60),dur=0.5)
        c.ev(t+3,'l',dC=(-0.3,0),dH=R(60),dur=0.7); c.ev(t+4,'r',dC=(0,0.2),dH=R(60),dur=0.6); c.ev(t+5,'l',dH=R(60),dur=0.5)
        for k in (0,3): c.sway(t+k+1,-0.4 if k==0 else 0.4); c.sway(t+k+2.8,0)
    def rev(t):
        c.ev(t,'l',dC=(0.3,0),dH=-R(60),dur=0.7); c.ev(t+1,'r',dC=(0,0.2),dH=-R(60),dur=0.6); c.ev(t+2,'l',dH=-R(60),dur=0.5)
        c.ev(t+3,'r',dC=(-0.3,0),dH=-R(60),dur=0.7); c.ev(t+4,'l',dC=(0,-0.2),dH=-R(60),dur=0.6); c.ev(t+5,'r',dH=-R(60),dur=0.5)
        for k in (0,3): c.sway(t+k+1,0.4 if k==0 else -0.4); c.sway(t+k+2.8,0)
    def change(t,lf):
        o='r' if lf=='l' else 'l'
        c.ev(t,lf,dC=(0.35,0),dur=0.7); c.ev(t+1,o,dC=(0.05,-0.15 if lf=='l' else 0.15),dur=0.6); c.ev(t+2,lf,dur=0.5)
    nat(0); nat(6); nat(12); c.fig('v_natural',0,18)
    change(18,'l'); change(21,'r'); c.fig('v_change',18,24)
    rev(24); rev(30); rev(36); c.fig('v_reverse',24,42)
    change(42,'r')
    return c.run(45.5)

def tango():
    c=Couple(128,d=0.15,o=0.09)
    for D in (c.L,c.F): D.knee=0.035; D.lean=0.0
    def walk(t,lf):  # slow = 2 beats
        c.ev(t,lf,dC=(0.42,0),dur=0.7)
    def prog_side(t):  # Q Q S: L fwd, R side & slightly back, L fwd
        c.ev(t,'l',dC=(0.3,0),dur=0.45); c.ev(t+1,'r',dC=(0.02,-0.2),dur=0.45); c.ev(t+2,'l',dC=(0.38,0.05),dur=0.6)
    def rock_turn(t):  # R fwd, L back, R back (rocking), turning right
        c.ev(t,'r',dC=(0.35,0),dH=R(30),dur=0.5); c.ev(t+1,'l',dC=(-0.2,0),dH=R(25),dur=0.45); c.ev(t+2,'r',dC=(-0.15,0),dH=R(20),dur=0.6)
        c.ev(t+4,'l',dC=(-0.1,0.2),dH=R(15),dur=0.45); c.ev(t+5,'r',dur=0.4,w=True); c.ev(t+6,'l',dC=(0.3,0),dur=0.6)
    def promenade(t):  # open to promenade: both face lead's left diagonal and travel there
        H=c.H; ang=H+R(70)
        f,l=rot(H)
        lp=c.lc(c.C,H); fp=c.fc(c.C,H)
        for k,(lf,dt,step) in enumerate((('l',0,0.38),('r',2,0.32),('l',3,0.14),('r',4,0.0))):
            c.C=c.C+l*step
            c.ev(t+dt,lf,lh=H-R(55) if k<3 else H,fh=H+np.pi+R(55) if k<3 else H+np.pi,dur=0.5)
        c.hold(t-0.3,t+4.2,'standard')
    walk(0,'l'); walk(2,'r'); walk(4,'l'); walk(6,'r'); c.fig('t_walks',0,8)
    prog_side(8); c.ev(11,'r',dur=0.4,w=False); c.fig('t_pss',8,12)
    walk(12,'l'); walk(14,'r')
    rock_turn(16); c.fig('t_rock',16,23)
    promenade(24); c.fig('t_prom',24,29)
    walk(30,'l'); walk(32,'r')
    return c.run(34.5)

def foxtrot():
    c=Couple(112)
    for D in (c.L,c.F): D.lean=0.02
    def feather(t):  # S Q Q : R fwd, L fwd, R fwd (outside partner)
        c.ev(t,'r',dC=(0.45,0),dur=1.2); c.rise(t+1.6,0.6)
        c.ev(t+2,'l',dC=(0.35,0.03),dur=0.7); c.rise(t+2.5,1.0)
        c.ev(t+3,'r',dC=(0.38,0.0),ex=(0,-0.06),dur=0.7); c.rise(t+3.9,0.0)
        c.sway(t+2,0.4); c.sway(t+3.9,0)
    def three(t):  # L fwd, R fwd, L fwd
        c.ev(t,'l',dC=(0.45,0),dur=1.2); c.rise(t+1.6,0.6)
        c.ev(t+2,'r',dC=(0.38,0),dur=0.7); c.rise(t+2.5,1.0)
        c.ev(t+3,'l',dC=(0.38,0),dur=0.7); c.rise(t+3.9,0)
    def reverse(t):
        c.ev(t,'l',dC=(0.42,0),dH=-R(45),dur=1.2); c.rise(t+1.6,0.6)
        c.ev(t+2,'r',dC=(0.1,0.24),dH=-R(60),dur=0.7); c.rise(t+2.5,1.0)
        c.ev(t+3,'l',dC=(-0.35,0),dH=-R(30),dur=0.7); c.rise(t+3.9,0.0)
        c.ev(t+4,'r',dC=(-0.4,0),dH=-R(30),dur=1.0); c.rise(t+5.6,0.6)
        c.ev(t+6,'l',dC=(0,0.2),dH=-R(45),dur=0.7); c.rise(t+6.5,1)
        c.ev(t+7,'r',dC=(0.4,0),dur=0.7); c.rise(t+7.9,0)
        c.sway(t+2,0.5); c.sway(t+3.9,0)
    feather(0); three(4); c.fig('f_feather',0,4); c.fig('f_three',4,8)
    feather(8); reverse(12); c.fig('f_reverse',12,20)
    feather(20); three(24)
    return c.run(28.5)

def quickstep():
    c=Couple(200)
    for D in (c.L,c.F): D.lean=0.03
    def qturn(t):  # S Q Q S : R fwd turning, L side, R close, L side and slightly back
        c.ev(t,'r',dC=(0.42,0),dH=R(45),dur=1.0); c.rise(t+1.6,0.7)
        c.ev(t+2,'l',dC=(0,-0.25),dH=R(30),dur=0.5); c.ev(t+3,'r',dC=(0,-0.05),dur=0.4); c.rise(t+3,1.0)
        c.ev(t+4,'l',dC=(-0.1,-0.25),dur=0.9); c.rise(t+5.6,0)
    def prog_chasse(t):  # S Q Q S to the side
        c.ev(t,'r',dC=(0.38,0),dur=1.0); c.rise(t+1.6,0.7)
        c.ev(t+2,'l',dC=(0,0.22),dur=0.5); c.ev(t+3,'r',dC=(0,0.04),dur=0.4); c.rise(t+3,1.0)
        c.ev(t+4,'l',dC=(0.05,0.24),dur=0.9); c.rise(t+5.6,0)
    def lock(t):  # S Q Q S forward lock: R fwd, L fwd, R crosses behind L, L fwd
        c.ev(t,'r',dC=(0.45,0),dur=1.0); c.rise(t+1.6,0.8)
        c.ev(t+2,'l',dC=(0.3,0),dur=0.5); c.ev(t+3,'r',dC=(0.06,0),ex=(-0.05,0.12),dur=0.4); c.rise(t+3,1.0)
        c.ev(t+4,'l',dC=(0.38,0),dur=0.8); c.rise(t+5.6,0)
    prog_chasse(0); c.fig('q_chasse',0,6)
    qturn(6); c.fig('q_qturn',6,12)
    prog_chasse(12); lock(18); c.fig('q_lock',18,24)
    lock(24); qturn(30)
    return c.run(36.5)

# ---------------- LATIN ----------------
def chacha():
    c=Couple(120,d=0.38,o=0.0,hold='two')
    for D in (c.L,c.F): D.lean=0.05
    def basic_half(t,lf,dirn):  # 2 rock, 3 replace, 4&1 chassé
        o='r' if lf=='l' else 'l'
        c.ev(t,lf,ex=(0.2*dirn,0),dur=0.4); c.hip(t+0.2,0.8 if lf=='l' else -0.8)
        c.ev(t+1,o,dur=0.4)
        side=0.13 if lf=='l' else -0.13
        c.ev(t+2,lf,dC=(0,side),dur=0.3); c.ev(t+2.5,o,dC=(0,side*0.3),dur=0.25); c.ev(t+3,lf,dC=(0,side),dur=0.3)
        c.hip(t+3.2,0.8 if lf=='l' else -0.8)
    def basic(t): basic_half(t,'l',1); basic_half(t+4,'r',-1)
    def new_york(t, lf):  # turn to side by side, check forward, replace, chassé back to face
        o='r' if lf=='l' else 'l'; H=c.H; turn=R(90) if lf=='r' else -R(90)
        f,l=rot(H)
        c.ev(t,lf,lh=H-turn,fh=H+np.pi+turn,dur=0.45)
        c.ev(t+1,o,lh=H,fh=H+np.pi,dur=0.4)
        side=-0.13 if lf=='r' else 0.13
        c.ev(t+2,lf,dC=(0,side),dur=0.3); c.ev(t+2.5,o,dC=(0,side*0.3),dur=0.25); c.ev(t+3,lf,dC=(0,side),dur=0.3)
        c.hold(t-0.2,t+1.8,'open',0.0,'up')
    def spot_turn(t,lf):  # both turn (lead left, follow right) in place on 2-3, chassé
        o='r' if lf=='l' else 'l'; H=c.H; tr=R(360)
        c.ev(t,lf,lh=H+R(180) if lf=='r' else H-R(180),fh=H+np.pi-R(180) if lf=='r' else H+np.pi+R(180),dur=0.5)
        c.ev(t+1,o,lh=H+tr if lf=='r' else H-tr,fh=H+np.pi-tr if lf=='r' else H+np.pi+tr,dur=0.5)
        c.Lh=H; c.Fh=H+np.pi; c.L.head.add(t+1.01,[H]); c.F.head.add(t+1.01,[H+np.pi])
        side=-0.13 if lf=='r' else 0.13
        c.ev(t+2,lf,dC=(0,side),dur=0.3); c.ev(t+2.5,o,dC=(0,side*0.3),dur=0.25); c.ev(t+3,lf,dC=(0,side),dur=0.3)
        c.hold(t-0.3,t+1.9,'release',0.0,'up')
    basic(0); basic(8); c.fig('c_basic',0,16)
    new_york(16,'r'); new_york(20,'l'); new_york(24,'r'); new_york(28,'l'); c.fig('c_ny',16,32)
    spot_turn(32,'r'); spot_turn(36,'l'); c.fig('c_spot',32,40)
    basic(40)
    return c.run(48.5)

def rumba():
    c=Couple(104,d=0.38,o=0.0,hold='two')
    for D in (c.L,c.F): D.lean=0.05
    def basic(t):  # box-like: 2 fwd,3 replace,4-1 side ; 2 back,3 replace,4-1 side
        c.ev(t,'l',ex=(0.22,0),dur=0.6); c.hip(t+0.3,0.9); c.ev(t+1,'r',dur=0.6); c.hip(t+1.3,-0.9)
        c.ev(t+2,'l',dC=(0,0.18),dur=1.0); c.hip(t+3,0.9,0.9)
        c.ev(t+4,'r',ex=(-0.22,0),dur=0.6); c.hip(t+4.3,-0.9); c.ev(t+5,'l',dur=0.6); c.hip(t+5.3,0.9)
        c.ev(t+6,'r',dC=(0,-0.18),dur=1.0); c.hip(t+7,-0.9,0.9)
    def cucaracha(t,lf):  # side press, replace, close
        o='r' if lf=='l' else 'l'; sg=1 if lf=='l' else -1
        c.ev(t,lf,ex=(0,0.24*sg),dur=0.6); c.hip(t+0.3,0.9*sg)
        c.ev(t+1,o,dur=0.6); c.hip(t+1.3,-0.9*sg)
        c.ev(t+2,lf,dur=1.0); c.hip(t+3,0.5*sg,0.9)
    def alemana(t):  # follow underarm turn to the right over 4 beats while lead does a basic
        H=c.H
        c.ev(t,'l',ex=(0.15,0),who='lead',dur=0.6); c.ev(t+1,'r',who='lead',dur=0.6); c.ev(t+2,'l',who='lead',dur=1.0)
        fc=c.fc(c.C,H)
        for k,(fo,dt) in enumerate((('r',0),('l',1),('r',2))):
            hh=H+np.pi-R(120)*(k+1)
            _,fl=rot(hh); c.F.head.add(t+dt-0.5,[c.Fh]); c.F.head.add(t+dt,[hh]); c.Fh=hh
            c.F.step(fo,t+dt,fc+fl*0.08*(1 if fo=='l' else -1),dur=0.6)
        c.Fh=H+np.pi
        c.hold(t-0.3,t+3.6,'open',1.0,'up')
    basic(0); basic(8); c.fig('r_basic',0,16)
    cucaracha(16,'l'); cucaracha(20,'r'); c.fig('r_cuca',16,24)
    basic(24)
    alemana(32); c.ev(36,'r',ex=(-0.15,0),dur=0.6); c.ev(37,'l',dur=0.6); c.ev(38,'r',dur=1.0); c.fig('r_alemana',32,40)
    basic(40)
    return c.run(48.5)

def paso():
    c=Couple(120,d=0.2,o=0.06,hold='standard')
    for D in (c.L,c.F): D.lean=-0.04; D.knee=0.01
    def sur_place(t,n=8):
        for k in range(n):
            lf='r' if k%2==0 else 'l'; c.ev(t+k,lf,dur=0.35);
            for D in (c.L,c.F): D.rise.add(t+k-0.3,[0.6]); D.rise.add(t+k,[0.0])
    def basic(t):  # march forward 1-2, back 3-4 ...
        for k in range(4): c.ev(t+k,'r' if k%2==0 else 'l',dC=(0.32,0),dur=0.45)
        for k in range(4): c.ev(t+4+k,'r' if k%2==0 else 'l',dC=(-0.32,0),dur=0.45)
    def chasses(t,dirn):
        for k in range(4):
            lf=('l' if dirn>0 else 'r') if k%2==0 else ('r' if dirn>0 else 'l')
            c.ev(t+k,lf,dC=(0,0.2*dirn if k%2==0 else 0.06*dirn),dur=0.4)
            for D in (c.L,c.F): D.rise.add(t+k-0.4,[0.5]); D.rise.add(t+k,[0.1])
    def appel(t):
        c.ev(t,'r',dur=0.25); c.L.knee=0.01
        for D in (c.L,c.F): D.rise.add(t-0.1,[0.0])
        c.ev(t+1,'l',ex=(0.3,0),dur=0.5)
    appel(0); sur_place(2); c.fig('p_sur',0,10)
    basic(10); c.fig('p_basic',10,18)
    appel(18); chasses(20,1); chasses(24,-1); c.fig('p_chasse',18,28)
    appel(28); sur_place(30,6); c.fig('p_appel',28,36)
    return c.run(36.5)

def bsamba():
    c=Couple(100,d=0.18,o=0.06,hold='standard')
    for D in (c.L,c.F): D.bounce=0.03; D.lean=0.06
    def basic(t,lf):  # 1 a 2: fwd, close (ball), replace
        o='r' if lf=='l' else 'l'
        c.ev(t,lf,ex=(0.22,0),dur=0.4); c.ev(t+0.75,o,dur=0.2,w=True); c.ev(t+1,lf,dur=0.25)
    def whisk(t,lf):
        o='r' if lf=='l' else 'l'; sg=1 if lf=='l' else -1
        c.ev(t,lf,ex=(0,0.24*sg),dur=0.4); c.ev(t+0.75,o,ex=(-0.08,0.06*sg),dur=0.2); c.ev(t+1,lf,ex=(0,0.24*sg),dur=0.25)
        c.sway(t+0.1,0.5*sg); c.sway(t+1.6,0)
    def walks(t):  # promenade samba walks, side by side facing lead's left
        H=c.H
        for k in range(6):
            lf='l' if k%2==0 else 'r'
            c.C=c.C+rot(H)[1]*0.12
            c.ev(t+k,lf,lh=H-R(75),fh=H+np.pi+R(75),dur=0.45)
        c.hold(t-0.3,t+6,'open',0.0,'up')
        c.ev(t+6.5,'l',lh=H,fh=H+np.pi,dur=0.5); c.ev(t+7,'r',dur=0.4)
    for k in range(4): basic(k*2,'l' if k%2==0 else 'r')
    c.fig('s_basic',0,8)
    for k in range(4): whisk(8+k*2,'l' if k%2==0 else 'r')
    c.fig('s_whisk',8,16)
    walks(16); c.fig('s_walks',16,24)
    for k in range(4): basic(24+k*2,'l' if k%2==0 else 'r')
    return c.run(32.5)
