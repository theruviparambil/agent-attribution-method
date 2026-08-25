import json, subprocess, sys, datetime, os, re

QUERY = """
query($owner:String!, $name:String!, $cursor:String) {
  repository(owner:$owner, name:$name) {
    pullRequests(states:MERGED, first:25, orderBy:{field:UPDATED_AT, direction:DESC}, after:$cursor) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number mergedAt
        author { login __typename }
        reviews(first:20) { nodes { state author { login __typename } } }
        commits(first:20) { totalCount nodes { commit { message } } }
      }
    }
  }
}
"""
BOT_LOGINS = {'cursoragent','devin-ai-integration','coderabbitai','renovate','dependabot',
 'greenkeeper','snyk-bot','github-actions','copilot','copilot-swe-agent','claude','openai-codex',
 'imgbot','pre-commit-ci','codecov','sonarcloud','stale','mergify','semantic-release-bot','web-flow'}
def is_bot(a):
    if not a: return True
    if a.get('__typename')=='Bot': return True
    l=(a.get('login') or '').lower()
    if l.endswith('[bot]') or l.endswith('-bot') or l.endswith('_bot'): return True
    return (l[:-5] if l.endswith('[bot]') else l) in BOT_LOGINS

# agent attribution signals in commit messages
SIGNALS = [
 ('claude_coauthor', re.compile(r'co-authored-by:\s*claude', re.I)),
 ('claude_generated', re.compile(r'generated with .{0,20}claude code', re.I)),
 ('claude_session', re.compile(r'^claude-session:', re.I|re.M)),
 ('copilot_coauthor', re.compile(r'co-authored-by:\s*copilot', re.I)),
 ('agent_logs_url', re.compile(r'^agent-logs-url:', re.I|re.M)),
 ('amp_thread', re.compile(r'^amp-thread:', re.I|re.M)),
 ('cursor_coauthor', re.compile(r'co-authored-by:\s*cursor', re.I)),
 ('assisted_by', re.compile(r'^assisted-by:', re.I|re.M)),
 ('devin', re.compile(r'co-authored-by:\s*devin', re.I)),
 ('codex', re.compile(r'co-authored-by:\s*.{0,12}codex', re.I)),
 ('aider', re.compile(r'\baider\b.{0,20}(wrote|edit)', re.I)),
 ('generic_ai_coauthor', re.compile(r'co-authored-by:.{0,40}\b(ai|bot|agent|gpt|llm)\b', re.I)),
]
def gql(o,n,c):
    a=['gh','api','graphql','-f',f'query={QUERY}','-F',f'owner={o}','-F',f'name={n}']
    a += ['-F',f'cursor={c}'] if c else ['-F','cursor=']
    p=subprocess.run(a,capture_output=True,text=True)
    if p.returncode!=0: return None,p.stderr[:150]
    try: return json.loads(p.stdout),None
    except Exception as e: return None,str(e)[:150]

CUTOFF=(datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(days=365)).isoformat()
rows=[l.rstrip('\n').split('\t') for l in open(sys.argv[1]) if l.strip()]
OUT=sys.argv[2]; CKPT=OUT+'.done'
done=set(open(CKPT).read().split()) if os.path.exists(CKPT) else set()
out=open(OUT,'a'); ck=open(CKPT,'a')
MAXP=int(sys.argv[3]) if len(sys.argv)>3 else 4
n_pr=0
for i,row in enumerate(rows):
    full=row[0]; seg=row[1] if len(row)>1 else 'x'
    if full in done: continue
    o,nm=full.split('/',1); cur=None; pg=0
    while pg<MAXP:
        d,err=gql(o,nm,cur)
        if err or not d:
            print(f'ERROR {full} page{pg}: {err}',file=sys.stderr,flush=True)
            break
        rp=(d.get('data') or {}).get('repository')
        if not rp: break
        prs=rp['pullRequests']; stop=False
        for pr in prs['nodes']:
            if not pr.get('mergedAt'): continue
            if pr['mergedAt']<CUTOFF: stop=True; continue
            au=pr.get('author') or {}; al=(au.get('login') or '').lower()
            appr=[r for r in pr['reviews']['nodes'] if r.get('state')=='APPROVED']
            hum=[r for r in appr if not is_bot(r.get('author')) and ((r.get('author') or {}).get('login') or '').lower()!=al]
            msgs=' \n'.join((c['commit']['message'] or '') for c in pr['commits']['nodes'])
            sigs=[k for k,rx in SIGNALS if rx.search(msgs)]
            out.write(json.dumps({'repo':full,'seg':seg,'num':pr['number'],'mergedAt':pr['mergedAt'],
              'month':pr['mergedAt'][:7],'authorBot':is_bot(au),'authorLogin':au.get('login'),
              'nApprovals':len(appr),'humanApproved':len(hum)>0,
              'nCommits':pr['commits']['totalCount'],'sigs':sigs,'anySig':bool(sigs)})+'\n')
            n_pr+=1
        pg+=1
        if stop or not prs['pageInfo']['hasNextPage']: break
        cur=prs['pageInfo']['endCursor']
    ck.write(full+'\n'); ck.flush(); out.flush()
    if (i+1)%25==0: print(f"  {i+1}/{len(rows)} repos, {n_pr} PRs",file=sys.stderr,flush=True)
print(f"DONE {len(rows)} repos, {n_pr} PRs",file=sys.stderr)
