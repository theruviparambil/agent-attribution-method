import json, subprocess, sys, re, os, time

CAND = ["AGENTS.md","CONTRIBUTING.md",".github/CONTRIBUTING.md","CLAUDE.md",
        ".github/AGENTS.md","docs/CONTRIBUTING.md",".github/copilot-instructions.md"]

PAT = {
 'requires_trailer'  : re.compile(r'co-?authored-by\s*:\s*(claude|copilot|cursor|ai|agent|gpt)|assisted-by\s*:', re.I),
 'forbids_trailer'   : re.compile(r'(not allowed|do not|don\'t|never|prohibit)[^.\n]{0,80}(co-?authored-by|assisted-by|ai (tool|agent) as (a )?co-?author)', re.I),
 'mentions_ai_policy': re.compile(r'\b(ai-?assisted|ai-?generated|llm|coding agent|ai tool)\b', re.I),
 'human_accountable' : re.compile(r'(human (submitter|author|contributor)|understand and defend|must be able to explain)', re.I),
 'bans_pure_agent_pr': re.compile(r'(pure )?(code-?agent|ai-?generated) prs? (are )?not allowed|automatic ban', re.I),
 'dco_signoff'       : re.compile(r'signed-off-by|developer certificate of origin|\bDCO\b'),
}

def gh(path):
    p = subprocess.run(['gh','api',path],capture_output=True,text=True)
    if p.returncode!=0: return None
    try: return json.loads(p.stdout)
    except Exception: return None

repos=[l.split('\t')[0].strip() for l in open(sys.argv[1]) if l.strip()]
segs={l.split('\t')[0].strip():(l.split('\t')[1].strip() if '\t' in l else '?') for l in open(sys.argv[1]) if l.strip()}
out=open(sys.argv[2],'a'); done=set()
if os.path.exists(sys.argv[2]):
    for l in open(sys.argv[2]):
        try: done.add(json.loads(l)['repo'])
        except Exception: pass

for i,full in enumerate(repos):
    if full in done: continue
    o,n=full.split('/',1)
    root=gh(f"repos/{o}/{n}/contents/")
    names={x['name'] for x in root} if isinstance(root,list) else set()
    found={}
    for cand in CAND:
        base=cand.split('/')[-1]
        if '/' not in cand and base not in names: continue
        d=gh(f"repos/{o}/{n}/contents/{cand}")
        if not isinstance(d,dict) or 'content' not in d: continue
        import base64
        try: txt=base64.b64decode(d['content']).decode('utf-8','replace')
        except Exception: continue
        hits={k:bool(rx.search(txt)) for k,rx in PAT.items()}
        if any(hits.values()) or cand.endswith('AGENTS.md'):
            found[cand]={'len':len(txt),**hits}
    out.write(json.dumps({'repo':full,'seg':segs.get(full,'?'),'policies':found})+'\n'); out.flush()
    if (i+1)%50==0: print(f"  {i+1}/{len(repos)}",file=sys.stderr,flush=True)
print("DONE",file=sys.stderr)
