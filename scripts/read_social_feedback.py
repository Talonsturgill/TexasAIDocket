#!/usr/bin/env python3
"""Optional private presentation hints. Never blocks or publishes private evidence."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

TARGETS={'texas_carousel':('Talonsturgill/TexasAIDocket','default'),'texas_video':('Talonsturgill/TexasAIDispatch','default'),'alaska_carousel':('Talonsturgill/alaskaaicarousels','alaska_ai'),'alaska_video':('Talonsturgill/alaska-ai-weekly','alaska_ai')}
ACTIONS={'hook':{'lead_with_question','lead_with_concrete_benefit'},'cover':{'reduce_headline_length','increase_title_contrast'},'caption':{'shorten_intro','use_short_paragraphs'},'CTA':{'ask_one_relevant_question','use_one_existing_cta'},'pacing':{'shorten_intro','add_section_pause'}}
PRIVATE_REMOTE='https://github.com/Talonsturgill/social-content-feedback.git'

def check(value):
 if not value: raise ValueError('invalid advice')

def git(directory,*args,timeout=15):
 p=subprocess.run(['git','-c','credential.interactive=never','-c','core.askPass=/usr/bin/false','-C',str(directory),*args],capture_output=True,timeout=timeout,env={**os.environ,'GIT_TERMINAL_PROMPT':'0'})
 check(p.returncode==0)
 return p.stdout

def remote_repo(remote):
 for prefix in ('https://github.com/','git@github.com:','ssh://git@github.com/'):
  if remote.startswith(prefix):
   repo=remote[len(prefix):].removesuffix('.git')
   # GitHub owner/repository names are case-insensitive; return the bound canonical ID.
   if repo.isascii():
    for canonical,_ in TARGETS.values():
     if repo.lower()==canonical.lower(): return canonical
 return None

def validate(b,g,today):
 check(type(b) is dict and set(b)=={'schema_version','generator','repository','profile','week','created_on','expires_on','actions'})
 check(type(b['schema_version']) is int and b['schema_version']==1)
 check((b['generator'],b['repository'],b['profile'])==(g,*TARGETS[g]))
 created=dt.date.fromisoformat(b['created_on']); expires=dt.date.fromisoformat(b['expires_on'])
 check(created<=today<=expires and 0<=(expires-created).days<=14)
 check(b['week']==today.strftime('%G-W%V')==created.strftime('%G-W%V'))
 check(type(b['actions']) is list and len(b['actions'])<=1)
 for a in b['actions']:
  check(type(a) is dict and set(a)=={'field','change','evidence_post_ids','sample_size','confidence'})
  check(a['field'] in ACTIONS and a['change'] in ACTIONS[a['field']])
  check(a['field']!='pacing' or g.endswith('_video'))
  ids=a['evidence_post_ids']; check(type(ids) is list and 5<=len(ids)<=20)
  check(all(type(p) is str and re.fullmatch(r'[A-Za-z0-9_.:-]{1,200}',p) for p in ids))
  check(len(set(ids))==len(ids) and type(a['sample_size']) is int and a['sample_size']==len(ids))
  check(a['confidence'] in ('low','medium'))
 return b

def scratch_root(repo_dir):
 root=Path(repo_dir).resolve(strict=True)
 current=root
 for component in ('out','social-feedback','tmp'):
  current=current/component
  check(not current.is_symlink())
  current.mkdir(exist_ok=True)
  check(current.resolve(strict=True).is_relative_to(root))
 # Refuse to leave private checkout scratch in a tracked/public path.
 git(root,'check-ignore','--quiet','--no-index',str(current.relative_to(root))+'/')
 return current

def read(g,repo_dir,today=None):
 today=today or dt.date.today()
 check(remote_repo(git(repo_dir,'remote','get-url','origin').decode().strip())==TARGETS[g][0])
 with tempfile.TemporaryDirectory(prefix='read-',dir=scratch_root(repo_dir)) as scratch:
  git(scratch,'init','--quiet')
  git(scratch,'fetch','--quiet','--depth=1','--no-tags',PRIVATE_REMOTE,'main',timeout=45)
  raw=git(scratch,'show',f'FETCH_HEAD:briefs/latest/{g}.json')
  check(len(raw)<=8192)
  b=validate(json.loads(raw),g,today)
  digest=hashlib.sha256(raw).hexdigest()
  return [{'field':a['field'],'change':a['change'],'week':b['week'],'brief_sha256':digest} for a in b['actions']]

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--generator',choices=TARGETS,required=True)
 parser.add_argument('--repo-dir',required=True,help='Explicit source working tree whose origin must match generator')
 args=parser.parse_args()
 try: result=read(args.generator,Path(args.repo_dir))
 except (OSError,ValueError,KeyError,TypeError,UnicodeError,subprocess.TimeoutExpired):
  print('Optional social feedback unavailable; continuing without advice.',file=sys.stderr)
  result=[]
 print(json.dumps(result))
 return 0
if __name__=='__main__': sys.exit(main())
