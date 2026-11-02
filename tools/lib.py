import sys,json,base64,numpy as np
sys.path.insert(0,'.')
from bvh import parse,fk
CAN=['hips','spine','chest','neck','head','headTop','lSh','lEl','lWr','lHd','rSh','rEl','rWr','rHd','lHip','lKn','lAn','lToe','rHip','rKn','rAn','rToe']
CMU=dict(hips='Hips',spine='Spine',chest='Spine1',neck='Neck1',head='Head',headTop='Head_end',lSh='LeftArm',lEl='LeftForeArm',lWr='LeftHand',lHd='LeftHandIndex1',rSh='RightArm',rEl='RightForeArm',rWr='RightHand',rHd='RightHandIndex1',lHip='LeftUpLeg',lKn='LeftLeg',lAn='LeftFoot',lToe='LeftToeBase_end',rHip='RightUpLeg',rKn='RightLeg',rAn='RightFoot',rToe='RightToeBase_end')
PIR=dict(hips='hip',spine='abdomen',chest='chest',neck='neck',head='head',headTop=None,lSh='lShldr',lEl='lForeArm',lWr='lHand',lHd='lMid2_end',rSh='rShldr',rEl='rForeArm',rWr='rHand',rHd='rMid2_end',lHip='lThigh',lKn='lShin',lAn='lFoot',lToe='lFoot_end',rHip='rThigh',rKn='rShin',rAn='rFoot',rToe='rFoot_end')
def load(path,mp,scale,trim=(0,None)):
    j,ft,d=parse(path); step=max(1,round((1/30)/ft))
    p=fk(j,d,step)*scale
    names=[x['name'] for x in j]
    out=np.zeros((p.shape[0],len(CAN),3))
    for k,c in enumerate(CAN):
        if mp[c] is None: continue
        out[:,k]=p[:,names.index(mp[c])]
    if mp['headTop'] is None:
        h=CAN.index('head');n=CAN.index('neck');out[:,CAN.index('headTop')]=out[:,h]+(out[:,h]-out[:,n])*1.6
    a,b=trim; fps=1/(ft*step)
    s=int(a*fps); e=None if b is None else int(b*fps)
    return out[s:e],fps
CM=0.05644
