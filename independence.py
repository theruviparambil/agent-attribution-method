#!/usr/bin/env python3
"""Independence cut of scan2.jsonl.

The rest of this repository asks a disclosure question: how often does a merged
pull request say an agent was involved. This asks the separate question of who
approved those pull requests, using the `humanApproved` field the scanner
already records.

A pull request counts as human-approved when at least one review in state
APPROVED came from an account that is not a GitHub Bot type, does not match the
bot login patterns, is not on the known-bot list, and is not the pull request
author. That last clause is what makes this an independence measure rather than
an approval count: an author approving their own pull request does not count.

Two things worth stating before anyone reads a number off this.

It is conservative in a specific way. The comparison is against the pull
request author only, so a pull request approved by somebody who wrote commits
in it but did not open it still counts as approved here. A stricter test that
compared against every authoring account would find fewer independent
approvals, not more.

And it inherits every limit in the README, in particular that a signal is a
disclosure artifact rather than a measurement of how much code an agent wrote.
This says nothing about pull requests that carried no signal, because for those
we do not know whether an agent was involved at all.

Usage:  python3 independence.py
"""
import collections
import json
import random

EXCLUDE_ORGS = {"plaidev"}  # Tokyo CX company, mislabeled as fintech. See correction (ii).


def org(row):
    return row["repo"].split("/")[0]


rows = [json.loads(line) for line in open("scan2.jsonl") if line.strip()]
dropped = [r for r in rows if org(r) in EXCLUDE_ORGS]
rows = [r for r in rows if org(r) not in EXCLUDE_ORGS]

print(
    f"EXCLUDED {len(dropped)} PRs from "
    f"{len(set(r['repo'] for r in dropped))} `plaidev` repos "
    f"(Plaid Inc. Tokyo, not the US fintech)"
)
print(f"CORPUS: {len(rows):,} merged PRs across {len(set(r['repo'] for r in rows))} repositories\n")

signaled = [r for r in rows if r.get("anySig")]
unapproved = [r for r in signaled if not r.get("humanApproved")]

print("SIGNALED PULL REQUESTS AND THEIR APPROVALS")
print(f"  carried an agent-authorship signal      {len(signaled):>6,}")
print(
    f"  of those, no independent human approval {len(unapproved):>6,}"
    f"   ({100 * len(unapproved) / len(signaled):.1f}%)\n"
)

print("BY SEGMENT")
for seg in sorted({r["seg"] for r in rows}):
    s = [r for r in signaled if r["seg"] == seg]
    u = [r for r in s if not r.get("humanApproved")]
    if not s:
        continue
    print(f"  {seg:<10} {len(s):>5,} signaled   {len(u):>5,} unapproved   {100 * len(u) / len(s):.1f}%")

# The same cut for everything merged, signal or not, so a reader can see whether
# signaled pull requests are approved any differently from the rest. They are
# not, which is the honest finding: this is not a story about agent work being
# treated worse, it is a story about the control being weak generally and
# nobody being able to see which changes an agent touched.
print("\nCONTROL: all merged PRs regardless of signal")
allun = [r for r in rows if not r.get("humanApproved")]
print(
    f"  no independent human approval           {len(allun):>6,}"
    f"   ({100 * len(allun) / len(rows):.1f}% of {len(rows):,})"
)

print("\nBY QUARTER, signaled PRs only")
by = collections.defaultdict(lambda: [0, 0])
for r in signaled:
    q = f"{r['month'][:4]}Q{(int(r['month'][5:7]) - 1) // 3 + 1}"
    by[q][0] += 1
    if not r.get("humanApproved"):
        by[q][1] += 1
for q in sorted(by):
    total, un = by[q]
    print(f"  {q}   {un:>4} / {total:<5} unapproved   {100 * un / total:.0f}%")

# The signaled rate on its own is a subset rate, not a finding. The comparison
# that matters is against the pull requests that carried no signal, and that
# gap has to be tested at the repository level, because approval practice is a
# property of a repository, not of a pull request.
print("\nSIGNALED AGAINST UNSIGNALED")
unsig = [r for r in rows if not r.get("anySig")]
unsig_un = [r for r in unsig if not r.get("humanApproved")]
rate_sig = 100 * len(unapproved) / len(signaled)
rate_unsig = 100 * len(unsig_un) / len(unsig)
print(f"  signaled     {len(unapproved):>6,} / {len(signaled):<6,} ({rate_sig:.1f}%)")
print(f"  unsignaled   {len(unsig_un):>6,} / {len(unsig):<6,} ({rate_unsig:.1f}%)")
print(f"  gap                                {rate_sig - rate_unsig:+.2f} percentage points")
zero = [r for r in unapproved if r.get("nApprovals", 0) == 0]
print(
    f"  of the {len(unapproved)} signaled PRs without independent approval, "
    f"{len(zero)} had no approving review of any kind"
)

print("\nBASELINE BY SEGMENT, all merged PRs regardless of signal")
for seg in sorted({r["seg"] for r in rows}):
    s = [r for r in rows if r["seg"] == seg]
    u = [r for r in s if not r.get("humanApproved")]
    print(f"  {seg:<10} {len(u):>5,} / {len(s):<6,} ({100 * len(u) / len(s):.1f}%)")

# Repository-clustered bootstrap of the gap. Resample the repositories with
# replacement, keep every pull request of each drawn repository, recompute the
# gap, and read the 2.5th and 97.5th percentiles. The seed is fixed so the
# interval printed here is the interval quoted in the README.
by_repo = collections.defaultdict(list)
for r in rows:
    by_repo[r["repo"]].append(r)
repos = sorted(by_repo)


def gap(sample):
    s = su = u = uu = 0
    for k in sample:
        for r in by_repo[k]:
            if r.get("anySig"):
                s += 1
                su += not r.get("humanApproved")
            else:
                u += 1
                uu += not r.get("humanApproved")
    return 100 * su / s - 100 * uu / u


RESAMPLES, SEED = 2000, 0
rng = random.Random(SEED)
gaps = sorted(gap([rng.choice(repos) for _ in repos]) for _ in range(RESAMPLES))
lo, hi = gaps[int(0.025 * RESAMPLES)], gaps[int(0.975 * RESAMPLES)]
print(f"\nREPOSITORY-CLUSTERED BOOTSTRAP OF THE GAP ({RESAMPLES:,} resamples of {len(repos)} repos, seed {SEED})")
print(f"  95% interval   [{lo:+.1f}, {hi:+.1f}] percentage points")
print(f"  resamples at or below zero   {100 * sum(g <= 0 for g in gaps) / RESAMPLES:.1f}%")

print("\nCONCENTRATION: organizations supplying the most signaled PRs without independent approval")
for o, n in collections.Counter(org(r) for r in unapproved).most_common(3):
    n_repos = len({r["repo"] for r in unapproved if org(r) == o})
    print(f"  {o:<22} {n:>4} of {len(unapproved)}   across {n_repos} repos")

# Where review is practiced at all, the two rates converge. "Practiced" here
# means at least half of the repository's merged pull requests had an
# independent approval.
reviewed = {k for k, v in by_repo.items() if sum(bool(r.get("humanApproved")) for r in v) / len(v) >= 0.5}
rs = [r for r in rows if r["repo"] in reviewed]
r_sig = [r for r in rs if r.get("anySig")]
r_unsig = [r for r in rs if not r.get("anySig")]
r_sig_un = [r for r in r_sig if not r.get("humanApproved")]
r_unsig_un = [r for r in r_unsig if not r.get("humanApproved")]
print(f"\nREPOS WHERE AT LEAST HALF OF MERGED PRS HAD INDEPENDENT APPROVAL: {len(reviewed)} of {len(repos)}, {len(rs):,} PRs")
print(f"  signaled     {len(r_sig_un):>5} / {len(r_sig):<6,} ({100 * len(r_sig_un) / len(r_sig):.1f}%)")
print(f"  unsignaled   {len(r_unsig_un):>5} / {len(r_unsig):<6,} ({100 * len(r_unsig_un) / len(r_unsig):.1f}%)")
