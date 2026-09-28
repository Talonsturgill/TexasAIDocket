"""Pinhole projection matching THREE.PerspectiveCamera lookAt, 1080x1350, vertical fov in degrees."""
import numpy as np, sys
def P(frm, look, fov, pts, W=1080, H=1350):
    f=np.array(frm,float); l=np.array(look,float); z=f-l; z/=np.linalg.norm(z)
    x=np.cross([0,1,0],z); x/=np.linalg.norm(x); y=np.cross(z,x)
    t=np.tan(np.radians(fov)/2); a=W/H; out=[]
    for p in pts:
        d=np.array(p,float)-f; cx,cy,cz=d@x,d@y,d@z
        if cz>=0: out.append(None); continue
        nx=cx/(-cz)/(t*a); ny=cy/(-cz)/t
        out.append((round((nx+1)/2*W),round((1-ny)/2*H)))
    return out
if __name__=='__main__':
    import json; a=json.loads(sys.argv[1]); print(P(a['from'],a['look'],a['fov'],a['pts']))
