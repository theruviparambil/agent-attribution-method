#!/usr/bin/env python3
"""Corrected analysis of scan2.jsonl. Applies every fix the adversarial pass demanded:
   - excludes org `plaidev` (Plaid Inc. of Tokyo / KARTE, plaid.co.jp -- NOT the US fintech `plaid`)
   - discloses the 100-PR-per-repo cap and its contribution to each month
   - reports a BALANCED PANEL (repos active in both the first and last windows) as the headline
   - publishes the per-signal monthly decomposition
"""
import json, collections, sys

rows=[json.loads(l) for l in open('scan2.jsonl')]
EXCLUDE_ORGS={'plaidev'}                      # Tokyo CX company, mislabeled as fintech
def org(r): return r['repo'].split('/')[0]
dropped=[r for r in rows if org(r) in EXCLUDE_ORGS]
rows=[r for r in rows if org(r) not in EXCLUDE_ORGS]
print(f"EXCLUDED {len(dropped)} PRs from {len(set(r['repo'] for r in dropped))} `plaidev` repos (Plaid Inc. Tokyo, not the US fintech)")

fin=[r for r in rows if r['seg']=='fintech']
per_repo=collections.Counter(r['repo'] for r in fin)
capped={k for k,v in per_repo.items() if v>=100}
print(f"FINTECH after exclusion: {len(fin):,} PRs across {len(per_repo)} repos")
print(f"REPOS AT THE 100-PR CAP: {len(capped)}  (these contribute only to recent months)\n")

months=sorted({r['month'] for r in fin})
EARLY=set(months[:3]); LATE=set(months[-3:])
by_repo_months=collections.defaultdict(set)
for r in fin: by_repo_months[r['repo']].add(r['month'])
panel={k for k,v in by_repo_months.items() if (v & EARLY) and (v & LATE)}
print(f"BALANCED PANEL: {len(panel)} repos active in BOTH {sorted(EARLY)} and {sorted(LATE)}\n")

def series(sub, label):
    m=collections.defaultdict(lambda:[0,0])
    for r in sub:
        m[r['month']][0]+=1
        if r['anySig']: m[r['month']][1]+=1
    print(f"--- {label} ---")
    print(f"{'month':9s} {'sig':>5s} {'PRs':>6s} {'rate':>7s}   {'capped share of signal':>22s}")
    for k in sorted(m):
        t,g=m[k]
        cs=[r for r in sub if r['month']==k and r['repo'] in capped and r['anySig']]
        cap_share=f"{100*len(cs)/g:.0f}%" if g else "-"
        print(f"{k:9s} {g:5d} {t:6d} {100*g/t if t else 0:6.2f}%   {cap_share:>22s}")
    print()

series(fin, "ALL FINTECH REPOS (biased by the cap: capped repos enter only late)")
series([r for r in fin if r['repo'] in panel], "BALANCED PANEL  <-- THE HEADLINE NUMBER")

print("--- PER-SIGNAL MONTHLY DECOMPOSITION (all fintech) ---")
sigs=sorted({s for r in fin for s in r['sigs']})
print(f"{'month':9s} " + " ".join(f"{s[:11]:>11s}" for s in sigs))
for k in sorted({r['month'] for r in fin}):
    c=collections.Counter(s for r in fin if r['month']==k for s in r['sigs'])
    print(f"{k:9s} " + " ".join(f"{c.get(s,0):>11d}" for s in sigs))

print("\n--- CONCENTRATION: top orgs by signal rate over the whole window ---")
byorg=collections.defaultdict(lambda:[0,0])
for r in fin:
    byorg[org(r)][0]+=1
    if r['anySig']: byorg[org(r)][1]+=1
for k,v in sorted(byorg.items(), key=lambda x:-x[1][1]):
    if v[0]>=25: print(f"  {k:26s} {v[1]:4d}/{v[0]:<5d} {100*v[1]/v[0]:5.1f}%")
