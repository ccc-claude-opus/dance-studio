import numpy as np, re, sys
from scipy.spatial.transform import Rotation as R
def parse(path):
    txt=open(path).read().split('MOTION')
    toks=txt[0].split()
    joints=[];stack=[];i=0
    while i<len(toks):
        t=toks[i]
        if t in('ROOT','JOINT'):
            joints.append(dict(name=toks[i+1],parent=stack[-1] if stack else -1,ch=[],end=False));i+=2;continue
        if t=='End':
            joints.append(dict(name=joints[stack[-1]]['name']+'_end',parent=stack[-1],ch=[],end=True));i+=2;continue
        if t=='{': stack.append(len(joints)-1)
        elif t=='}': stack.pop()
        elif t=='OFFSET': joints[stack[-1]]['off']=np.array(list(map(float,toks[i+1:i+4])));i+=4;continue
        elif t=='CHANNELS':
            n=int(toks[i+1]);joints[stack[-1]]['ch']=toks[i+2:i+2+n];i+=2+n;continue
        i+=1
    m=txt[1].strip().split('\n')
    ft=float(m[1].split()[-1])
    data=np.array([list(map(float,l.split())) for l in m[2:] if l.strip()])
    return joints,ft,data
def fk(joints,data,step):
    data=data[::step]; F=len(data); J=len(joints)
    pos=np.zeros((F,J,3)); rot=[None]*J
    c=0
    for j,jt in enumerate(joints):
        chs=jt['ch']; vals=data[:,c:c+len(chs)]; c+=len(chs)
        p=jt['parent']
        tr=np.tile(jt['off'],(F,1)); rchs=''
        rv=[]
        for k,ch in enumerate(chs):
            if ch.endswith('position'): tr[:,'XYZ'.index(ch[0])]=vals[:,k]
            else: rchs+=ch[0]; rv.append(vals[:,k])
        loc=R.from_euler(rchs,np.stack(rv,1),degrees=True) if rchs else R.identity(F)
        if p<0: pos[:,j]=tr; rot[j]=loc
        else:
            pos[:,j]=pos[:,p]+rot[p].apply(tr); rot[j]=rot[p]*loc
    return pos
