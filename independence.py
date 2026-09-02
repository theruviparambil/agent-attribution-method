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

EXCLUDE_ORGS = {"plaidev"}  # Tokyo CX company, mislabelled as fintech. See correction (ii).


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

signalled = [r for r in rows if r.get("anySig")]
unapproved = [r for r in signalled if not r.get("humanApproved")]

print("SIGNALLED PULL REQUESTS AND THEIR APPROVALS")
print(f"  carried an agent-authorship signal      {len(signalled):>6,}")
print(
    f"  of those, no independent human approval {len(unapproved):>6,}"
    f"   ({100 * len(unapproved) / len(signalled):.1f}%)\n"
)

print("BY SEGMENT")
for seg in sorted({r["seg"] for r in rows}):
    s = [r for r in signalled if r["seg"] == seg]
    u = [r for r in s if not r.get("humanApproved")]
    if not s:
        continue
    print(f"  {seg:<10} {len(s):>5,} signalled   {len(u):>5,} unapproved   {100 * len(u) / len(s):.0f}%")

# The same cut for everything merged, signal or not, so a reader can see whether
# signalled pull requests are approved any differently from the rest. They are
# not, which is the honest finding: this is not a story about agent work being
# treated worse, it is a story about the control being weak generally and
# nobody being able to see which changes an agent touched.
print("\nCONTROL: all merged PRs regardless of signal")
allun = [r for r in rows if not r.get("humanApproved")]
print(
    f"  no independent human approval           {len(allun):>6,}"
    f"   ({100 * len(allun) / len(rows):.1f}% of {len(rows):,})"
)

print("\nBY QUARTER, signalled PRs only")
by = collections.defaultdict(lambda: [0, 0])
for r in signalled:
    q = f"{r['month'][:4]}Q{(int(r['month'][5:7]) - 1) // 3 + 1}"
    by[q][0] += 1
    if not r.get("humanApproved"):
        by[q][1] += 1
for q in sorted(by):
    total, un = by[q]
    print(f"  {q}   {un:>4} / {total:<5} unapproved   {100 * un / total:.0f}%")
