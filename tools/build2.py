import sys,json,base64,numpy as np
sys.path.insert(0,'.')
from lib import load,CMU,PIR,CAN
from tempo import tempo
import os
HERE=os.path.dirname(os.path.abspath(__file__))
CM=0.05644; D=os.environ.get('CMU_DIR',os.path.join(HERE,'cmu','data'))+'/'
PIR_BVH=os.path.join(HERE,'assets','pirouette.bvh')
OUT=os.environ.get('OUT_DIR',os.path.join(HERE,'..','web'))
J={n:i for i,n in enumerate(CAN)}
BANDS={'salsa':(150,215,180),'swing':(150,220,190),'lambada':(110,140,124),'ballet':(60,96,76),'indian':(84,130,100),'break':(85,115,96)}
def prep(arrs):
    n=min(len(a) for a in arrs); arrs=[a[:n].copy() for a in arrs]
    allp=np.concatenate(arrs,1)
    feet=allp[:,[J[x] for x in ['lAn','lToe','rAn','rToe']]][:,:,1]
    floor=np.percentile(feet.min(1),3); ctr=allp[:,0,[0,2]].mean(0)
    for a in arrs: a[:,:,1]-=floor; a[:,:,0]-=ctr[0]; a[:,:,2]-=ctr[1]
    return arrs,n
def enc(a): return base64.b64encode(np.clip(np.round(a*1000),-32767,32767).astype('<i2').tobytes()).decode()
def clip(srcs,style):
    arrs=[];roles=[]
    for s,role in srcs:
        if s=='PIR': a,fps=load(PIR_BVH,PIR,0.01)
        else: a,fps=load(D+s+'.bvh',CMU,CM)
        arrs.append(a);roles.append(role)
    arrs,n=prep(arrs)
    lo,hi,dflt=BANDS[style]
    try: bpm,off=tempo(arrs,fps,lo,hi)
    except Exception: bpm,off=dflt,0
    if not(lo<bpm<hi): bpm,off=dflt,0.0
    return dict(fps=round(fps,3),frames=n,bpm=bpm,off=off,actors=[dict(role=r,data=enc(a)) for a,r in zip(arrs,roles)]),arrs,fps
def heading(p):
    s=p[:,J['lSh']]-p[:,J['rSh']]; return np.unwrap(np.arctan2(s[:,0],-s[:,2]))
def sm(x,k=5): return np.convolve(np.pad(x,(k,k),mode='edge'),np.ones(2*k+1)/(2*k+1),'valid')
def salsa_events(A,B,fps):
    n=len(A); hA=sm(heading(A)); hB=sm(heading(B))
    rel=B[:,0,[0,2]]-A[:,0,[0,2]]; rA=sm(np.unwrap(np.arctan2(rel[:,1],rel[:,0])))
    ev=[]; W=int(2.2*fps)
    def spins(h,who):
        t=int(.5*fps)
        while t<n-W:
            d=h[t:t+W]-h[t]; k=np.argmax(np.abs(d))
            if abs(d[k])>np.radians(300):
                e=t+k
                while e<n-3 and abs(h[e+3]-h[e])>np.radians(20): e+=3
                ev.append(dict(w=who,a=t/fps,b=e/fps,deg=float(np.degrees(abs(h[e]-h[t]))),cw=bool(h[e]>h[t]))); t=e+int(.5*fps)
            else: t+=3
    spins(hB,'F'); spins(hA,'L')
    W2=int(3*fps); t=int(.5*fps)
    while t<n-W2:
        d=rA[t:t+W2]-rA[t]; k=np.argmax(np.abs(d))
        if abs(d[k])>np.radians(150) and abs(d[k])<np.radians(230):
            ev.append(dict(w='X',a=t/fps,b=(t+k)/fps,deg=float(np.degrees(abs(d[k]))))); t+=k+int(fps)
        else: t+=3
    # calm windows (basic)
    busy=np.zeros(n,bool)
    for e in ev: busy[int(e['a']*fps):int(e['b']*fps)+1]=True
    t=int(.8*fps)
    while t<n:
        if not busy[t]:
            e=t
            while e<n and not busy[e]: e+=1
            if (e-t)/fps>=2.6: ev.append(dict(w='B',a=t/fps,b=min(e,t+int(4*fps))/fps,deg=0))
            t=e
        t+=1
    return ev
def ov(a,b): return min(a['b'],b['b'])-max(a['a'],b['a'])>0.6
def build():
    out={}; clips={}
    # ---------- salsa ----------
    takes=[];cands={}
    for i in range(1,16):
        key=f'sal{i:02d}'
        c,(A,B),fps=clip([(f'060/60_{i:02d}','lead'),(f'061/61_{i:02d}','follow')],'salsa'); clips[key]=c
        takes.append(dict(clip=key,name=f'第 {i} 段'))
        ev=salsa_events(A,B,fps)
        Fs=[e for e in ev if e['w']=='F'];Ls=[e for e in ev if e['w']=='L'];Xs=[e for e in ev if e['w']=='X']
        dur=c['frames']/c['fps']
        def add(cat,e,score):
            a=max(0,e['a']-0.6); b=min(dur,e['b']+0.6)
            cands.setdefault(cat,[]).append(dict(clip=key,a=round(a,2),b=round(b,2),s=score))
        for e in Fs:
            if any(ov(e,l) for l in Ls): continue
            if any(ov(e,x) for x in Xs): continue
            if e['deg']>=880: add('multi',e,e['deg'])
            elif e['deg']>=560: add('double',e,-abs(e['deg']-720))
            else: add('rturn' if e['cw'] else 'lturn',e,-abs(e['deg']-360))
        for e in Ls:
            if any(ov(e,f) for f in Fs): 
                f=[f for f in Fs if ov(e,f)][0]; add('both',dict(a=min(e['a'],f['a']),b=max(e['b'],f['b'])),e['deg']+f['deg'])
            else: add('lead',e,-abs(e['deg']-360))
        for x in Xs:
            fs=[f for f in Fs if ov(x,f)]
            if fs: add('cbl_turn',dict(a=min(x['a'],fs[0]['a']),b=max(x['b'],fs[0]['b'])),fs[0]['deg'])
            else: add('cbl',x,-abs(x['deg']-180))
        for e in ev:
            if e['w']=='B': add('basic',e,e['b']-e['a'])
    FIG=[('basic','基本步','Basic Step','兩人面對面原地踩 1-2-3、5-6-7，沒有轉圈'),
         ('cbl','交叉換位','Cross Body Lead','男方讓出一條路，女方從他面前走過去，兩人交換位置'),
         ('cbl_turn','換位接轉圈','Cross Body Lead with Turn','交叉換位的同時女方在中途轉一圈'),
         ('rturn','女方右轉','Right Turn','男方舉手帶女方順時針轉一圈'),
         ('lturn','女方左轉','Left Turn','男方舉手帶女方逆時針轉一圈'),
         ('double','女方雙圈轉','Double Spin','女方連續轉兩圈'),
         ('multi','女方多圈轉','Multiple Spins','女方連續轉三圈以上，表演型舞步'),
         ('lead','男方轉身','Lead Spin','男方自己轉一圈，女方原地等待'),
         ('both','雙人同時轉','Simultaneous Turn','兩人同時各自轉圈再接回')]
    figs=[]
    for k,zh,en,desc in FIG:
        L=sorted(cands.get(k,[]),key=lambda d:-d['s'])
        # avoid duplicates in same clip overlapping
        pick=[]
        for d in L:
            if any(p['clip']==d['clip'] and min(p['b'],d['b'])-max(p['a'],d['a'])>0 for p in pick): continue
            pick.append(d)
            if len(pick)>=3: break
        for j,d in enumerate(pick):
            figs.append(dict(name=zh,en=en,desc=desc,ex=j+1,of=len(pick),clip=d['clip'],a=d['a'],b=d['b']))
    out['salsa']=dict(name='薩爾薩',en='Salsa',cat='社交舞',style='salsa',takes=takes,figs=figs,
        src='CMU 受試者 60（男）＋61（女），同場錄製；舞步名稱由程式依兩人的轉向與換位自動辨識')
    # ---------- swing ----------
    sw=[('swc','093/93_03',None,'查爾斯頓基本步','Charleston Basic','前踢後點，身體隨重心上下彈'),
        ('sws',['093/93_05','093/93_04'],None,'並排查爾斯頓','Side-by-Side Charleston','兩人並肩同步跳查爾斯頓'),
        ('swl','093/93_06',None,'林迪舞步','Lindy Hop','搖擺舞的招牌跑跳步'),
        ('swf','093/93_08',None,'花式查爾斯頓','Fancy Charleston','加上手部與交叉腿的花式變化')]
    figs=[];takes=[]
    for key,src,_,zh,en,desc in sw:
        srcs=[(src[0],'lead'),(src[1],'follow')] if isinstance(src,list) else [(src,'solo')]
        c,_,_=clip(srcs,'swing'); clips[key]=c; d=c['frames']/c['fps']
        takes.append(dict(clip=key,name=zh)); figs.append(dict(name=zh,en=en,desc=desc,clip=key,a=0,b=round(d,2)))
    out['swing']=dict(name='搖擺舞',en='Swing',cat='社交舞',style='swing',takes=takes,figs=figs,src='CMU 受試者 93')
    # ---------- lambada ----------
    figs=[];takes=[]
    for key,src,zh,en,desc in [('lam1','055/55_02','黃金舞段落','Lambada','臀部畫圈搖擺、重心左右交換'),('lam2','055/55_01','旋轉舞動','Whirl','邊走邊大幅度旋轉')]:
        c,_,_=clip([(src,'solo')],'lambada'); clips[key]=c; d=c['frames']/c['fps']
        takes.append(dict(clip=key,name=zh)); figs.append(dict(name=zh,en=en,desc=desc,clip=key,a=0,b=round(d,2)))
    out['lambada']=dict(name='黃金舞',en='Lambada',cat='社交舞',style='lambada',takes=takes,figs=figs,src='CMU 受試者 55')
    # ---------- ballet ----------
    BL=[('05_02','手臂表現接單足旋轉','Port de bras · Pirouette','手臂流動延展後接單足旋轉'),
        ('PIR','單足旋轉','Pirouette','單腳立起，另一腳收在膝旁快速旋轉'),
        ('05_03','側向阿拉貝斯克','Arabesque · Turn step','一腳向側後延伸成一直線，接轉步'),
        ('05_05','旋轉跳','Jeté en tournant','高抬腿後騰空邊轉邊跳'),
        ('05_06','連續旋轉與大跳','Pirouettes · Jeté','側翻起手，接連續旋轉與跳躍'),
        ('05_07','小跳與阿提丟','Petits jetés · Attitude','輕巧小跳，接彎膝抬腿的阿提丟姿勢'),
        ('05_08','空中畫圈','Rond de jambe en l’air','抬起的腳在空中畫圓'),
        ('05_09','滑步','Glissade','前後滑步移動，接阿拉貝斯克'),
        ('05_11','側步接旋轉','Sideways steps · Pirouette','向旁移動後接單足旋轉'),
        ('05_12','點地與上身轉動','Tendu à terre','手臂高舉、腳尖點地，上身扭轉'),
        ('05_13','小跳接旋轉','Petits jetés · Pirouette','連續小跳後收在旋轉上'),
        ('05_17','大跳旋轉','Grand jeté en tournant','助跑後大幅度騰空旋轉跳'),
        ('05_18','阿拉貝斯克後彎','Arabesque · Cambré','阿拉貝斯克接旋轉跳與上身後彎')]
    figs=[];takes=[]
    for s,zh,en,desc in BL:
        key='bal'+s.replace('05_','')
        c,_,_=clip([('PIR' if s=='PIR' else '005/'+s,'solo')],'ballet'); clips[key]=c; d=c['frames']/c['fps']
        takes.append(dict(clip=key,name=zh)); figs.append(dict(name=zh,en=en,desc=desc,clip=key,a=0,b=round(d,2)))
    out['ballet']=dict(name='芭蕾',en='Ballet',cat='表演舞',style='ballet',takes=takes,figs=figs,src='CMU 受試者 5（動作名稱來自 CMU 的錄製說明），單足旋轉來自 three.js 範例')
    # ---------- indian ----------
    figs=[];takes=[]
    for j,s in enumerate(['01','02','03','04','06']):
        key='ind'+s; c,_,_=clip([('094/94_'+s,'solo')],'indian'); clips[key]=c; d=c['frames']/c['fps']
        takes.append(dict(clip=key,name=f'第 {j+1} 套')); figs.append(dict(name=f'組合 {j+1}',en=f'Sequence {j+1}',desc='CMU 沒有標註這套動作的名稱',clip=key,a=0,b=round(d,2)))
    out['indian']=dict(name='印度舞',en='Indian Dance',cat='表演舞',style='indian',takes=takes,figs=figs,src='CMU 受試者 94（原始資料未標註舞步名稱）')
    # ---------- break ----------
    BR=[('085/85_03','站立舞步','Toprock','站著跳的開場步，帶出節奏'),('085/85_04','地板步','Footwork','手撐地、雙腳在地上繞圈移動'),
        ('085/85_01','跳躍轉體','Jump Twist','原地起跳在空中扭轉'),('085/85_05','倒立踢腿','Handstand Kicks','倒立後雙腿踢擺'),
        ('085/85_06','踢翻','Kick Flip','踢腿帶動身體翻轉'),('085/85_08','直升機','Helicopter','蹲低、一腳掃過地面帶身體旋轉'),
        ('085/85_10','收尾定格','Freeze','結束時停在定格姿勢'),('090/90_28','地板組合','Floor combo','連續的地板動作'),
        ('085/85_12','長段組合','Long Set','站立、地板、定格串成一整段'),('085/85_14','空翻組合','Set with Flips','加入空翻的整段表演')]
    figs=[];takes=[]
    for s,zh,en,desc in BR:
        key='brk'+s[-5:].replace('_','')
        c,_,_=clip([(s,'solo')],'break'); clips[key]=c; d=c['frames']/c['fps']
        takes.append(dict(clip=key,name=zh)); figs.append(dict(name=zh,en=en,desc=desc,clip=key,a=0,b=round(d,2)))
    out['break']=dict(name='霹靂舞',en='Breaking',cat='街舞',style='break',takes=takes,figs=figs,src='CMU 受試者 85、90（動作名稱來自 CMU 的錄製說明）')
    from choreo import bachata,jive
    SYN={'bachata':(bachata,'巴恰塔','Bachata','社交舞',{
          'b_side':('左右基本步','Side Basic','往旁三步加一個點地，第四拍頂出臀部','Three steps to the side and a tap, with a hip pop on 4'),
          'b_fb':('前後基本步','Forward & Back Basic','男進女退、再男退女進，第四拍點地','Lead steps forward while the follow steps back, then reverse, tapping on 4'),
          'b_rturn':('女方右轉','Follow Right Turn','5 到 7 拍女方在男方舉起的手下順時針轉一圈','On 5 to 7 the follow turns clockwise under the lead\'s raised hand'),
          'b_lturn':('女方左轉','Follow Left Turn','5 到 7 拍女方逆時針轉一圈','On 5 to 7 the follow turns counterclockwise'),
          'b_lead':('男方轉身','Lead Turn','放開抱握，男方自己轉一圈再接回','The lead lets go, turns once on his own, and reconnects')}),
         'jive':(jive,'吉魯巴','Jive','社交舞',{
          'j_basic':('基本步','Basic (Chassé · Rock)','左右兩個併步 1a2、3a4，再往後搖擺 5、6','Two chassés, 1a2 and 3a4, then a rock step back on 5 and 6'),
          'j_change':('換位（右到左）','Change of Places R to L','女方在舉起的手下轉一圈，兩人交換位置','The follow turns under the raised hand and the couple swap sides'),
          'j_kicks':('踢腿與彈腿（花步）','Kicks & Flicks','兩次踢腿換重心，接兩次提膝彈小腿','Two kick-ball-changes, then two flicks from the knee'),
          'j_spin':('美式旋轉','American Spin','男方推出，女方原地自轉一圈','The lead sends the follow into a spin on the spot'),
          'j_change2':('換位（再一次）','Change of Places again','再做一次換位回到原本位置','Change places again to return to the starting sides')})}
    import ballroom as BR
    SYN.update({
     'waltz':(BR.waltz,'華爾滋','Waltz','標準舞',{
        'w_box':('方塊步','Box Step','前、旁、併，後、旁、併，每小節三拍','Forward, side, close; back, side, close, three beats a bar'),
        'w_change':('閉式換步','Closed Change','前進中換腳，第一拍下沉、二三拍升起','Change feet while travelling: lower on 1, rise through 2 and 3'),
        'w_natural':('右轉步','Natural Turn','兩小節向右轉，配合升降與傾斜','Two bars turning right, with rise and fall and sway'),
        'w_reverse':('左轉步','Reverse Turn','兩小節向左轉','Two bars turning left')}),
     'tango':(BR.tango,'探戈','Tango','標準舞',{
        't_walks':('行進步','Walks','膝蓋微彎、不升降，每步兩拍','Knees soft, no rise and fall, each step two beats'),
        't_pss':('前進側行步','Progressive Side Step','快、快、慢的節奏往前推進','Quick, quick, slow, travelling forward'),
        't_rock':('右搖轉步','Natural Rock Turn','前後搖擺重心同時向右轉','Rocking forward and back while turning right'),
        't_prom':('閉式並進步','Closed Promenade','兩人打開成 V 字並肩前進，再合起','The couple opens into a V, travels side by side, then closes')}),
     'vwaltz':(BR.vwaltz,'維也納華爾滋','Viennese Waltz','標準舞',{
        'v_natural':('右旋轉','Natural Turn','快速連續向右旋轉，每小節半圈','Fast continuous turning to the right, half a turn per bar'),
        'v_change':('換步','Change Step','在左右旋轉之間換方向','Switches between right and left turns'),
        'v_reverse':('左旋轉','Reverse Turn','快速連續向左旋轉','Fast continuous turning to the left')}),
     'foxtrot':(BR.foxtrot,'狐步','Slow Foxtrot','標準舞',{
        'f_feather':('羽毛步','Feather Step','慢、快、快，男方第三步走到女方外側','Slow, quick, quick; the lead finishes outside his partner'),
        'f_three':('三步','Three Step','慢、快、快連續前進','Slow, quick, quick, travelling straight'),
        'f_reverse':('左轉步','Reverse Turn','兩組慢快快向左轉','Two slow-quick-quick groups turning left')}),
     'quickstep':(BR.quickstep,'快步舞','Quickstep','標準舞',{
        'q_chasse':('前進併步','Progressive Chassé','慢、快、快、慢，往旁併步','Slow, quick, quick, slow, chasséing to the side'),
        'q_qturn':('右四分之一轉','Quarter Turn to Right','轉四分之一圈接併步','A quarter turn with a chassé'),
        'q_lock':('前進鎖步','Forward Lock Step','後腳交叉鎖在前腳後面快速前進','The back foot crosses behind to lock while travelling fast')}),
     'chacha':(BR.chacha,'恰恰','Cha Cha','拉丁舞',{
        'c_basic':('基本步','Basic Movement','2 前搖、3 回、4&1 恰恰恰併步','Rock on 2, replace on 3, chassé on 4-and-1'),
        'c_ny':('紐約步','New York','兩人轉成並肩朝同方向踩出，左右交替','Turn side by side and check forward, alternating sides'),
        'c_spot':('原地轉','Spot Turn','放開手各自原地轉一圈','Let go and each turn once on the spot')}),
     'rumba':(BR.rumba,'倫巴','Rumba','拉丁舞',{
        'r_basic':('基本步','Basic Movement','慢節奏的前後方塊，配合古巴臀部動作','A slow forward and back box with Cuban hip action'),
        'r_cuca':('蟑螂步','Cucarachas','往旁壓步再收回，左右交替','Press to the side and return, alternating sides'),
        'r_alemana':('阿勒曼娜轉','Alemana Turn','女方在舉起的手下向右轉一圈','The follow turns right under the raised hand')}),
     'paso':(BR.paso,'鬥牛舞','Paso Doble','拉丁舞',{
        'p_sur':('原地踏步','Sur Place','挺胸，原地快速踏步','Chest up, quick marching on the spot'),
        'p_basic':('基本行進','Basic Movement','如同行軍般前進後退','Marching forward and back'),
        'p_chasse':('左右併步','Chassés','往旁快速併步，左右各一次','Quick chassés to one side and back'),
        'p_appel':('踏地起步','Appel','重踏一腳作為起步訊號，接原地踏步','A stamp to start, then marching on the spot')}),
     'bsamba':(BR.bsamba,'森巴（國標）','Samba (Ballroom)','拉丁舞',{
        's_basic':('基本步','Natural Basic','1a2 節奏前後彈動','Forward and back with the 1-a-2 bounce'),
        's_whisk':('旁掃步','Whisks','左右旁步，後腳在後方點地','Side steps with the other foot crossing behind'),
        's_walks':('森巴走步','Samba Walks','打開並肩向前走，帶彈動','Opened out side by side, walking with bounce')}),
    })
    SYN['jive']=(SYN['jive'][0],SYN['jive'][1],SYN['jive'][2],'拉丁舞',SYN['jive'][4])
    for did,(fn,zh,en,cat,FN) in SYN.items():
        A,B,bpm,fg=fn(); arrs,n=prep([A,B]); key='syn_'+did
        clips[key]=dict(fps=30,frames=n,bpm=bpm,off=0.0,actors=[dict(role='lead',data=enc(arrs[0])),dict(role='follow',data=enc(arrs[1]))])
        spb=60/bpm; figs=[]
        for k,a,b in fg:
            z,e,dz,de=FN[k]; figs.append(dict(name=z,en=e,desc=dz,den=de,clip=key,a=round(a*spb,2),b=round(min(b*spb+0.3,n/30),2)))
        out[did]=dict(name=zh,en=en,cat=cat,style=did,synth=True,takes=[dict(clip=key,name='完整套路',name_en='Full routine')],figs=figs,
            src='依標準舞步教學的拍數規則生成，不是真人錄製',src_en='Generated from standard syllabus step counts, not a real recording',bpm=bpm)
    out['samba']=dict(name='森巴',en='Samba',cat='表演舞',style='samba',skinned=True,takes=[dict(clip='samba',name='森巴')],figs=[],src='Mixamo 動作捕捉，擬真角色')
    return out,clips
if __name__=='__main__':
    dances,clips=build()
    import os
    EN={'Basic Step':'Face to face, stepping 1-2-3, 5-6-7 in place with no turns',
     'Cross Body Lead':'The lead opens a lane and the follow walks across in front of him; they swap places',
     'Cross Body Lead with Turn':'A cross body lead where the follow turns once on the way across',
     'Right Turn':'The lead raises his hand and turns the follow clockwise once','Left Turn':'The lead raises his hand and turns the follow counterclockwise once',
     'Double Spin':'The follow spins twice in a row','Multiple Spins':'The follow spins three or more times, a showcase move',
     'Lead Spin':'The lead turns on his own while the follow waits','Simultaneous Turn':'Both partners turn at the same time, then reconnect',
     'Charleston Basic':'Kick forward, tap back, with a bounce through the body','Side-by-Side Charleston':'Two dancers doing the Charleston in sync, side by side',
     'Lindy Hop':'The signature running, bouncing step of swing dance','Fancy Charleston':'Charleston with arm styling and crossed-leg variations',
     'Lambada':'Hip circles and side-to-side weight changes','Whirl':'Big travelling turns',
     'Port de bras · Pirouette':'Flowing arms, then a pirouette','Pirouette':'Up on one leg with the other foot at the knee, turning fast',
     'Arabesque · Turn step':'One leg extended behind in a long line, then a turning step','Jeté en tournant':'A high leg lift into a turning leap',
     'Pirouettes · Jeté':'Cartwheel-like start, linked pirouettes and leaps','Petits jetés · Attitude':'Small light leaps, then a bent-knee attitude',
     'Rond de jambe en l’air':'The raised leg draws circles in the air','Glissade':'Gliding steps forward and back, then an arabesque',
     'Sideways steps · Pirouette':'Travelling sideways into a pirouette','Tendu à terre':'Arms high, toe pointed on the floor, upper body twisting',
     'Petits jetés · Pirouette':'Small leaps that finish in a pirouette','Grand jeté en tournant':'A running start into a big turning leap',
     'Arabesque · Cambré':'Arabesque into a turning leap and a back bend',
     'Toprock':'Standing steps that set the rhythm before going down','Footwork':'Hands on the floor while the legs circle around',
     'Jump Twist':'A jump with a twist in the air','Handstand Kicks':'A handstand with swinging leg kicks','Kick Flip':'A kick that flips the body over',
     'Helicopter':'Low to the ground, one leg sweeps around to spin the body','Freeze':'Ending by holding a frozen pose','Floor combo':'A run of floor moves',
     'Long Set':'Toprock, floor work and freezes in one long set','Set with Flips':'A full set that includes flips'}
    SRC_EN={'salsa':'CMU subjects 60 (lead) and 61 (follow), recorded together; figure names detected automatically from the couple\'s turns and position swaps',
     'swing':'CMU subject 93','lambada':'CMU subject 55','ballet':'CMU subject 5 (move names from CMU\'s recording notes); pirouette from the three.js examples',
     'indian':'CMU subject 94 (the original data has no move names)','break':'CMU subjects 85 and 90 (move names from CMU\'s recording notes)','samba':'Mixamo motion capture, realistic character'}
    import re
    for did,d in dances.items():
        d.setdefault('src_en',SRC_EN.get(did,''))
        for t in d['takes']:
            if 'name_en' not in t:
                m=re.match(r'第 (\d+) (段|套)',t['name'])
                t['name_en']=(f'Take {m.group(1)}' if m.group(2)=='段' else f'Set {m.group(1)}') if m else next((f['en'] for f in d['figs'] if f['clip']==t['clip']),d['en'])
        for f in d['figs']:
            if 'den' not in f:
                f['den']=EN.get(f['en'],'The original data has no name for this sequence' if f['en'].startswith('Sequence') else '')
    meta={k:{kk:vv for kk,vv in v.items()} for k,v in dances.items()}
    # per-dance data files
    files={}
    for did,d in dances.items():
        if d.get('skinned'): continue
        ks=sorted({t['clip'] for t in d['takes']}|{f['clip'] for f in d['figs']})
        payload={k:clips[k] for k in ks}
        fn=f'data_{did}.js'; open(os.path.join(OUT,fn),'w').write(f'window.__DATA=window.__DATA||{{}};Object.assign(window.__DATA,{json.dumps(payload)});')
        d['file']=fn; files[fn]=os.path.getsize(os.path.join(OUT,fn))//1024
        for k in ks: pass
    # clip meta (bpm etc) also in index
    cm={k:dict(fps=v['fps'],frames=v['frames'],bpm=v['bpm'],off=v['off'],pair=len(v['actors'])>1) for k,v in clips.items()}
    open(os.path.join(OUT,'meta.js'),'w').write('window.DANCES='+json.dumps(dances,ensure_ascii=False)+';window.CLIPMETA='+json.dumps(cm)+';window.JOINTS='+json.dumps(CAN)+';')
    print(files)
    for did,d in dances.items():
        print(did,len(d['figs']),'figs'); 
        for f in d['figs'][:30]: print('   ',f['name'],f.get('ex',''),f['clip'],f['a'],f['b'],cm.get(f['clip'],{}).get('bpm'))
