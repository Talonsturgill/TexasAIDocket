import json
FIG = json.load(open('/home/user/TexasAIDocket/out/2026-09-30/figures.json'))
def figs(*keys):
    return 'const FIG = ' + json.dumps({k: FIG[k]['value'] for k in keys}) + ';\n'

CAM = r'''
  /* THE HOME CAMERA, shared exactly by frames 1, 7 and 9: seated eye behind the desk's empty seat,
   * looking north over it to the laptop and past it to the school wing 92 m out. */
  const HOME = { from: [-0.9, 1.02, 3.3], look: [0.1, 1.8, -8] };
  const DESK = { at: [-0.45, -2.35], rotY: 0.55 };
'''
