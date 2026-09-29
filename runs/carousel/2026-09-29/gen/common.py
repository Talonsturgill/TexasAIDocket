import json
FIG = json.load(open('/home/user/TexasAIDocket/out/2026-09-29/figures.json'))
def figs(*keys):
    return 'const FIG = ' + json.dumps({k: FIG[k]['value'] for k in keys}) + ';\n'
SITE = r'''
  const S = F.site(FIG.acres);
  const yard = F.yard(K, THREE, TXT, { count: FIG.units });
  yard.position.set(S.yard[0], 0, S.yard[2]); TXT.add(R, yard);
  F.pad(K, THREE, TXT, R, S.side);
'''
LAB_CSS = '''  .lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.04em; color:#F1ECE3; z-index:12; white-space:nowrap; text-shadow:0 0 4px rgba(12,12,14,0.6), 0 1px 8px rgba(12,12,14,0.35); }
  svg#lead { position:absolute; left:0; top:0; width:1080px; height:1350px; z-index:11; overflow:visible; }'''
LEAD_HTML = '<svg id="lead" width="1080" height="1350" viewBox="0 0 1080 1350"></svg>\n'
