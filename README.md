# Measuring AI-agent attribution in merged pull requests

Method, code and data for a measurement of how often merged pull requests carry any signal that an AI agent
wrote the code. Two segments: **regulated fintechs** (15 organisations) and **AI coding-tool vendors**
(4 organisations: Anthropic, Cursor, OpenAI, Sourcegraph).

Published by [Falden](https://falden.ai). Run on 2026-08-21.

**The short version: you cannot tell from the outside.** Across 11,534 merged pull requests in 510 public
repositories that had merges, the share carrying any agent-attribution signal ranged from **0% to 41%** between comparable
companies. That range is a disclosure-policy artifact, not a usage measurement, and public GitHub
organisations are not internal software development.

---

## What was measured

For every merged pull request in the window, every commit message in that PR was checked against twelve
agent-attribution signals:

| Signal | Pattern |
|---|---|
| `claude_coauthor` | `Co-authored-by: Claude` |
| `claude_generated` | `Generated with ... Claude Code` |
| `claude_session` | `Claude-Session:` trailer |
| `copilot_coauthor` | `Co-authored-by: Copilot` |
| `agent_logs_url` | `Agent-Logs-Url:` trailer |
| `amp_thread` | `Amp-Thread:` trailer |
| `cursor_coauthor` | `Co-authored-by: Cursor` |
| `assisted_by` | `Assisted-by:` trailer |
| `devin` | `Co-authored-by: Devin` |
| `codex` | `Co-authored-by: ...codex` |
| `aider` | aider edit markers |
| `generic_ai_coauthor` | `Co-authored-by:` naming ai/bot/agent/gpt/llm |

A PR counts as carrying a signal if **any** commit in it matches **any** pattern.

Approval was measured separately: a PR has human approval if at least one review in state `APPROVED` came
from an account that is not a GitHub Bot type, does not match bot login patterns, is not on a known-bot list,
and is not the PR author.

## Corpus

746 active public repositories across 15 organisations were scanned, selected by `pushed_at` within 365 days,
excluding archived repositories and forks. **510 of them had merged pull requests in the window**; the other
236 were pushed to but merged nothing, and a 30-repository sample confirmed those are genuine zeros rather
than collection failures.

**11,534 merged pull requests total**, window 2025-08-19 to 2026-08-19, split into two segments that must not
be conflated:

| Segment | Orgs | Repos with merges | Merged PRs |
|---|---|---|---|
| **Regulated fintech** | 15 | 332 | **6,869** |
| AI coding-tool vendors | 4 | 169 | 4,665 |

Any claim about fintechs uses the 6,869 figure. The vendor segment is reported separately and is not
comparable, since those organisations build the agents being detected.

`corpus.tsv` lists all 746 repositories scanned. Nothing was excluded after seeing its result.

## Results

### Headline

**0% to 41%** signal rate across comparable regulated fintechs, whole-window, on the 6,869-PR fintech segment.

### Balanced panel

The 81 repositories active in **both** the first and last three-month windows. This controls for repositories
entering the sample late, which is the main source of spurious slope.

| Month | Signals / PRs | Rate | | Month | Signals / PRs | Rate |
|---|---|---|---|---|---|---|
| 2025-08 | 0 / 61 | 0.00% | | 2026-03 | 11 / 255 | 4.31% |
| 2025-09 | 2 / 218 | 0.92% | | 2026-04 | 22 / 300 | 7.33% |
| 2025-10 | 2 / 294 | 0.68% | | 2026-05 | 23 / 175 | 13.14% |
| 2025-11 | 0 / 140 | 0.00% | | **2026-06** | 43 / 246 | **17.48%** |
| 2025-12 | 3 / 178 | 1.69% | | 2026-07 | 19 / 262 | 7.25% |
| 2026-01 | 6 / 238 | 2.52% | | 2026-08 | 9 / 133 | 6.77% |
| 2026-02 | 3 / 162 | 1.85% | | | | |

The panel **peaks in June and falls back below 7%.** We do not present this as growth. It is a short, noisy
series on a defeasible signal and we do not think it supports a trend claim.

### Signal distribution

| Signal | PRs | | Signal | PRs |
|---|---|---|---|---|
| `claude_coauthor` | 556 | | `claude_generated` | 22 |
| `codex` | 145 | | `devin` | 15 |
| `generic_ai_coauthor` | 94 | | `agent_logs_url` | 3 |
| `cursor_coauthor` | 91 | | `claude_session` | 2 |
| `copilot_coauthor` | 33 | | | |

**One vendor's default trailer is a majority of all signal.** Any change to that default moves this
measurement independently of how much agent code is actually written.

---

## Limits, stated plainly

1. **This is a floor on disclosure, not an estimate of usage.** Every trailer is opt-in and removable with one
   line of config. Measured separately: 87% of public files mentioning Copilot CLI's `includeCoAuthoredBy`
   set it to `false`.
2. **Public GitHub organisations are not internal software development.** Several organisations in this corpus
   run their real SDLC on internal GitLab or self-hosted forges and expose only SDKs, samples and plugins.
   A low public rate is not evidence of low agent usage.
3. **No organisation should be read as an example.** We deliberately do not name companies or use any single
   organisation as an illustration, because per-org rates in a public corpus are not comparable to each other.
4. **Sampling cap.** Up to 100 merged PRs per repository (4 pages of 25). 21 fintech repositories hit that
   ceiling. Capped repositories contribute disproportionately to recent months, which is exactly why the
   balanced panel exists and why the uncapped series is not the headline.
5. **Bot classification is heuristic:** GitHub account type, login pattern, and a known-bot list. Cursor's
   background agent is GitHub type `User`, not `Bot`, so it is caught only by the list.
6. **The window is 365 days** and the final month is partial.
7. **One organisation was excluded after collection**, for identity rather than results: 9 repositories under
   an org whose name collides with a fintech but which is an unrelated company in a different country and
   industry. The exclusion is in the code, not applied by hand.

## Reproducing

```
python3 scan2.py corpus.tsv scan2.jsonl 4     # collect (GitHub GraphQL, gh CLI auth)
python3 analyze_corrected.py                   # all figures in this README
```

`scan2.jsonl` is the raw per-PR output: repo, PR number, merge timestamp, author, bot classification,
approval counts, commit count, and which signals matched.

## Why we published this

We sell an assessment that measures this properly, inside a company's own estate and under authorised access.
It would be inconsistent to sell a measurement while keeping the method private. Everything here is checkable,
including the parts that did not work.

Corrections welcome as issues.

## Licence

MIT for the code. Data is derived from public GitHub metadata.
