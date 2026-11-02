"""Regenerate the base64 asset scripts the page loads (characters and pose model) from the binary files in assets/."""
import base64, os
HERE=os.path.dirname(os.path.abspath(__file__)); WEB=os.path.join(HERE,'..','web')
for src,var,out in [('michelle.glb','MICHELLE_B64','michelle.js'),('readyplayer.me.glb','RPM_B64','rpm.js'),('pose_landmarker_lite.task','POSE_MODEL_B64','pose_model.js')]:
    data=base64.b64encode(open(os.path.join(HERE,'assets',src),'rb').read()).decode()
    open(os.path.join(WEB,out),'w').write(f'window.{var}="{data}";')
    print('wrote',out)
