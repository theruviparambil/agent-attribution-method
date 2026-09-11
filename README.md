# Measuring AI-agent attribution in merged pull requests

Method, code and data for a measurement of how often merged pull requests carry any signal that an AI agent
wrote the code. Two segments: **regulated fintechs** (15 organizations) and **AI coding-tool vendors**
(4 organizations: Anthropic, Cursor, OpenAI, Sourcegraph).

Published by [Falden](https://falden.ai). Run on 2026-08-21.

**The short version: you cannot tell from the outside.** Across 11,534 merged pull requests in the 501 public
repositories that had merges after the exclusion described below, the share carrying any agent-attribution signal ranged from **0% to 41%** between comparable
companies. That range is a disclosure-policy artifact, not a usage measurement, and public GitHub
organizations are not internal software development.

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

746 active public repositories across 15 organizations were scanned, selected by `pushed_at` within 365 days,
excluding archived repositories and forks. **510 of them had merged pull requests in the window**; the other
236 were pushed to but merged nothing, and a 30-repository sample confirmed those are genuine zeros rather
than collection failures.

**11,922 merged pull requests collected** across those 510 repositories, window 2025-08-19 to 2026-08-19.
After excluding `plaidev` per correction (ii), the study corpus is **11,534 merged pull requests across 501
repositories**. Every figure below uses the 11,534 corpus unless stated otherwise. The corpus splits into two
segments that must not be conflated:

| Segment | Orgs | Repos with merges | Merged PRs |
|---|---|---|---|
| **Regulated fintech** | 15 | 332 | **6,869** |
| AI coding-tool vendors | 4 | 169 | 4,665 |

Any claim about fintechs uses the 6,869 figure. The vendor segment is reported separately and is not
comparable, since those organizations build the agents being detected.

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

Signal instances across the 1,243 signalled pull requests (a pull request can carry more than one
signal; 146 do), recomputed from `scan2.jsonl`:

| Signal | Instances | | Signal | Instances |
|---|---|---|---|---|
| `claude_coauthor` | 740 | | `copilot_coauthor` | 64 |
| `codex` | 216 | | `agent_logs_url` | 16 |
| `cursor_coauthor` | 146 | | `devin` | 15 |
| `generic_ai_coauthor` | 124 | | `claude_session` | 4 |
| `claude_generated` | 73 | | | |

1,398 instances in total. The earlier version of this table was computed from the first scan and
summed to 961; it did not reconcile with the 1,243 signalled pull requests reported below, and has been
replaced. Run `python3 independence.py` to reproduce these counts.


**One vendor's default trailer is a majority of all signal** (740 of 1,398 instances, 52.9%). Any change to that default moves this
measurement independently of how much agent code is actually written.

---

## Independence: who approved the signalled pull requests

The rest of this study asks a disclosure question. This asks a separate one, using the `humanApproved`
field defined above: of the merged pull requests that did carry an agent-authorship signal, how many were
approved by a real person other than the author.

Run `python3 independence.py` to reproduce every figure in this section from `scan2.jsonl`.

| | Signalled PRs | No independent approval | |
|---|---|---|---|
| **All** | **1,243** | **410** | **33.0%** |
| Fintech | 875 | 280 | 32% |
| AI vendors | 368 | 130 | 35% |

Same corpus as the rest of the study: 11,534 merged pull requests across 501 repositories after excluding
`plaidev`, per correction (ii).

### The baseline, which matters more than the headline

Across **all** 11,534 merged pull requests, signal or no signal, **2,789 (24.2%)** had no independent human
approval.

So signalled pull requests are worse (33.0% against 24.2%) but not dramatically, and anyone quoting the 33%
without the 24% is telling half the story. **The finding is not that agent-authored work is reviewed more
carelessly than everything else.** It is that the review control is weak generally, and that on the pull
requests where an agent was disclosed, it is weaker still. The reason that combination is worth measuring is
the one this whole repository exists for: on the pull requests that carried no signal, nobody can tell whether
an agent was involved at all.

### By quarter, signalled pull requests only

| Quarter | No independent approval | Signalled PRs | Rate |
|---|---|---|---|
| 2025Q3 | 0 | 11 | 0% |
| 2025Q4 | 4 | 44 | 9% |
| 2026Q1 | 65 | 162 | 40% |
| 2026Q2 | 201 | 520 | 39% |
| 2026Q3 | 140 | 506 | 28% |

The early quarters carry too few signalled pull requests to read a trend into, and the denominators are given
so that is visible rather than hidden behind a percentage.

### What this measure is, exactly

Conservative in one specific way: approval is compared against the **pull request author only**. A pull
request approved by somebody who wrote commits in it but did not open it still counts as approved here. A
stricter test comparing against every authoring account would find fewer independent approvals, not more.

It also inherits every limit in the section below. In particular a signal is a disclosure artifact and not a
measurement of how much code an agent wrote, so none of these figures says anything about the pull requests
that carried no signal.

## Follow-up: does written policy produce disclosure?

The range above shows disclosure varies. It does not show why. This section measures the mechanism.

### Do these organizations have an attribution policy at all?

We scanned all **746 repositories** collected for the corpus for `AGENTS.md`, `CONTRIBUTING.md`,
`.github/CONTRIBUTING.md`, `CLAUDE.md` and `.github/copilot-instructions.md`, and pattern-matched for rules
about AI attribution, human accountability and agent-authored pull requests. Reported by segment, since the two
are not comparable. The two segment counts below sum to 729 rather than 746 because 17 repositories from one
excluded organization are present in the raw scan output and removed from the reported fintech denominator;
see correction (ii).

| | Fintech (407 repos, 15 orgs) | AI vendors (322 repos, 4 orgs) |
|---|---|---|
| Has an `AGENTS.md` | 32 | 15 |
| Mentions AI, LLM or agent in a policy file | 6 | 0 |
| **Requires an attribution trailer** | **0** | **0** |
| Requires human accountability for AI-assisted work | **0** | 1 |
| Prohibits pure agent-authored pull requests | 0 | 0 |

**No repository in either segment requires an attribution trailer.** The six fintech files that mention AI are
agent *instruction* files, telling an agent how to work in the repository, not governance rules about
disclosure. The single human-accountability hit is `openai/fence`, an AI vendor rather than a regulated firm.

So the low disclosure rates in this corpus are not non-compliance. **There is nothing to comply with.**

### Where a policy does exist: NVIDIA/garak

`NVIDIA/garak`, an open-source LLM vulnerability scanner (9,023 stars), publishes an `AGENTS.md` that applies
"to **all** AI-assisted contributions", states that "pure code-agent PRs are **not allowed**" and that "a human
submitter must understand and defend the change end-to-end", and warns that "breaching these guidelines can
result in automatic banning". It gives literal trailer examples including `Co-authored-by: Claude`.

Measured across its **300 most recent merged pull requests**:

| Trailer | Mechanism | Present |
|---|---|---|
| AI attribution (`Co-authored-by: <agent>`) | written policy, ban threat, **no gate** | **26 / 300 = at least 8.7%** |
| `Signed-off-by` (DCO) | **bot-checked before merge** | **220 / 300 = at least 73.3%** |

Same repository. Same contributors. Same period. The only difference is that one is enforced at the merge gate
and the other is a written rule with a sanction attached.

Monthly, the AI trailer shows a policy landing and then decaying: 0.0% through March 2026, then 8.3%, 6.5%,
11.5%, a spike to 51.9% in July, and 21.1% in August.

### The ladder

| Corpus | Policy | Enforced at a gate | Disclosure |
|---|---|---|---|
| Linux kernel, `Signed-off-by` | yes | yes | **99.8%** |
| NVIDIA/garak, DCO | yes | yes (bot) | **at least 73.3%** |
| NVIDIA/garak, AI attribution | yes, with ban threat | no | **at least 8.7%** |
| Linux kernel, `Assisted-by` | requested | no | **0.64%** |
| This corpus, 746 repos | **none exists** | no | 0% to 41% |
| Six sectors, 730 repos | **5 of 730 (0.68%)** | no | 8.61% |

Two independent corpora, one mechanism. **Enforcement at the gate is the variable that moves disclosure.
Written policy, even with a sanction, is not.**

### Does this hold outside fintech?

The section above measures two segments. If a requirement to attribute agent work exists anywhere as normal
practice, it should be visible in a wider corpus. We scanned **730 repositories across 101 organizations**
in six sectors, sampling **50,093 merged pull requests**, using the same five filenames and the same
pattern-matching as above.

| Sector | Repos | Orgs | Has any policy file | Requires a trailer | Rate | AI-trailer PRs |
|---|---|---|---|---|---|---|
| Healthcare / health IT | 59 | 8 | 19 | **1** | 1.69% | 10.94% |
| Security / OSS security | 143 | 19 | 56 | **2** | 1.40% | 5.14% |
| AI vendors | 124 | 18 | 66 | **1** | 0.81% | 10.83% |
| Big tech | 159 | 19 | 133 | **1** | 0.63% | 12.07% |
| Finance | 191 | 30 | 84 | **0** | 0.00% | 8.20% |
| Government | 54 | 7 | 31 | **0** | 0.00% | 1.06% |
| **All** | **730** | **101** | **389** | **5** | **0.68%** | **8.61%** |

**5 repositories out of 730 require an attribution trailer: 0.68%.** Every one was verified by hand against the
live file, not accepted from the scanner. They are:

- `SAP/sailing-analytics`
- `ggml-org/llama.cpp`
- `openemr/openemr`
- `ossf/best-practices-badge`
- `ossf/scorecard-infra`

All five require **`Assisted-by:`**. Three of them explicitly forbid `Co-authored-by:` for an AI.
`ossf/best-practices-badge` gives the reasoning: do not use `Co-authored-by:` for an AI, because it implies
authorship and copyright requires human creative activity, and only a human adds `Signed-off-by:`, which
certifies the DCO and is a claim an AI cannot make. `ossf/scorecard-infra` goes further and says earlier docs
in that repository specified `Co-Authored-By:` and were wrong. This tracks the Linux kernel's documented
convention, which mandates `Assisted-by: AGENT_NAME:MODEL_VERSION` and states that AI agents must not add
`Signed-off-by` tags.

**That is a problem for this project's own instrument, and it is the most important finding here.** The
dominant signal in the pull-request scan is `claude_coauthor`, a `Co-authored-by:` trailer naming an AI. Every
repository in this corpus that has actually reasoned about the question has decided that trailer is the wrong
one. So the measurement counts a convention that the few informed projects are moving away from, and does not
count `Assisted-by:`, which is what they are moving toward. A rising `Assisted-by:` rate would appear in these
figures as falling disclosure. Any future run of this method should count both and report them separately.

Two things follow, and the second matters more than the first.

**There is no sector ladder.** Every sector sits between 0.00% and 1.69% requiring, and the gaps between
them are one or two repositories. Finance and government are both at zero. Finance is not behind technology on
this. Technology is not ahead. The
variation is noise at this base rate, and any argument of the form "sector X already does this, sector Y should
follow" is unsupported by this corpus in either direction.

**The five are not corporate engineering estates.** They are two OpenSSF repositories, an open-source EHR, a
community LLM runtime, and one vendor side project. Not one is the
internal software development of a regulated institution. So the finding is not that adoption is early. It is
that in this corpus the practice effectively does not exist yet, including in the places most likely to have
invented it.

This does not weaken the enforcement finding above. It generalises the precondition for it: a gate can only
enforce a rule that someone has written, and almost nobody has written one.

### Limits on this section

- garak is a single repository and its subject is AI security, so its contributors are unusually likely to be
  thinking about AI provenance. It is a favourable case for policy, not a random one, which makes the 8.7%
  more striking rather than less.
- The policy scan is pattern-matching over five filenames. A rule stated in a wiki, a PR template or a
  CODEOWNERS convention would be missed. The zero should be read as "no policy in the conventional locations",
  not "no policy anywhere".
- DCO presence is measured from commit messages, not from whether the check actually blocked anything.
- **Correction, 25 Aug (i):** an earlier version of this section reported 55 `AGENTS.md`, 9 AI mentions and
  zero human-accountability rules. Two scanner processes had overlapped and duplicated rows. Deduplicated, the
  figures are 47, 6 and 1. `policy.jsonl` in this repo is the deduplicated output.
- **Correction, 25 Aug (ii):** the fintech policy-scan denominator was published as 424 repositories across 16
  organizations. That count still included 17 repositories from an organization excluded from the pull-request
  measurement earlier for an identity collision: its name resembles a US fintech but it is an unrelated company
  in a different country and industry. It was removed from one denominator and left in the other. Corrected to
  **407 repositories across 15 organizations**, which now matches the corpus used for the PR measurement.
- **Correction, 25 Aug (iii):** the garak table published the DCO trailer as 219/300 = 73.0%. An independent
  second pass, run because a single-pass figure is not a claim under this project's own standard, found
  220/300. The original pass read only the first 20 commits per pull request and 10 of the 300 exceed 30
  commits, so trailer-bearing commits past the cutoff were missed. Both garak figures are now stated as
  floors ("at least"), because commit sets remain truncated at 30 for those 10 pull requests.
- **Correction, 25 Aug (iv):** the six-sector scan first completed with **827 rows**, which was reported
  internally as 827 repositories. It was not. Ninety-seven repositories were scanned twice by overlapping
  worker ranges, exactly the failure recorded in correction (i). Deduplicated by repository name, the corpus is
  **730 repositories**. Every figure in the six-sector section is computed from the deduplicated set, and
  `scale.tsv` is that set. If the figure 827 appears anywhere, it is wrong.
- **Correction, 25 Aug (v):** the six-sector section published **6 repositories / 0.82%**. One of the six,
  `finos/morphir`, is a false positive and says the opposite of what the scanner concluded. Its `CLAUDE.md`
  reads "**DO NOT** add Claude or any AI assistant as a commit co-author under any circumstances", and its
  `AGENTS.md` repeats the prohibition, because an AI co-author breaks the FINOS EasyCLA check. The scanner
  matched the literal `Co-Authored-By: Claude` string that appears inside a block headed "**NEVER include
  lines like:**" and another headed "**INCORRECT approach (WILL BREAK EasyCLA):**". The `requires_trailer`
  pattern has no negation-context check, so a prohibition that quotes the trailer it forbids reads as a
  requirement. Corrected to **5 repositories / 0.68%**, and Finance falls from 1 of 191 to **0 of 191**. All
  five survivors were then verified by hand against the live files rather than accepted from the scanner.
  Read `requires_trailer` in `scale.tsv` as "matched a trailer pattern", not as "requires a trailer": it is
  a screening signal that needs human confirmation, and this repository now treats it that way.
- None of these corrections change the headline: **no repository in either segment requires an attribution trailer.**

---

## Limits, stated plainly

1. **This is a floor on disclosure, not an estimate of usage.** Every trailer is opt-in and removable with one
   line of config. Measured separately: 87% of public files mentioning Copilot CLI's `includeCoAuthoredBy`
   set it to `false`.
2. **Public GitHub organizations are not internal software development.** Several organizations in this corpus
   run their real SDLC on internal GitLab or self-hosted forges and expose only SDKs, samples and plugins.
   A low public rate is not evidence of low agent usage.
3. **No organization should be read as an example.** We deliberately do not name companies or use any single
   organization as an illustration, because per-org rates in a public corpus are not comparable to each other.
4. **Sampling cap.** Up to 100 merged PRs per repository (4 pages of 25). 21 fintech repositories hit that
   ceiling. Capped repositories contribute disproportionately to recent months, which is exactly why the
   balanced panel exists and why the uncapped series is not the headline.
5. **Bot classification is heuristic:** GitHub account type, login pattern, and a known-bot list. Cursor's
   background agent is GitHub type `User`, not `Bot`, so it is caught only by the list.
6. **The window is 365 days** and the final month is partial.
7. **One organization was excluded after collection**, for identity rather than results: **17 repositories**
   under an org whose name collides with a fintech but which is an unrelated company in a different country
   and industry. The exclusion is in the code, not applied by hand. (An earlier version of this line said 9;
   that was wrong. 9 was the count of its repositories that had merged pull requests, 17 is the count in the
   corpus.)

## Reproducing

```
python3 scan2.py corpus.tsv scan2.jsonl 4     # collect (GitHub GraphQL, gh CLI auth)
python3 analyze_corrected.py                   # disclosure figures
python3 independence.py                        # the independence section
```

`scan2.jsonl` is the raw per-PR output: repo, PR number, merge timestamp, author, bot classification,
approval counts, commit count, and which signals matched.

`policy.jsonl` is the policy scan over the two original segments (746 rows, one per repository scanned).

`scale.tsv` is the six-sector scan, one row per repository, deduplicated to 730: sector, stars, whether any
policy file exists and which, whether it requires a trailer or mentions AI, and the sampled PR counts. The
per-sector table is a group-by over this file, so the figures can be checked without re-running collection.

It carries two separate columns for the requirement finding. `requires_trailer` is the raw scanner output and
is a screening signal only; it has no negation-context check and produced at least one false positive, see
correction (v). `verified_requires` is a human reading of the live file: `1` confirmed, `0` confirmed false
positive, empty where nobody has checked. The headline figure of 5 counts `verified_requires`, not
`requires_trailer`.

## Why we published this

We sell an assessment that measures this properly, inside a company's own estate and under authorised access.
It would be inconsistent to sell a measurement while keeping the method private. Everything here is checkable,
including the parts that did not work.

Corrections welcome as issues.

## License

MIT for the code. Data is derived from public GitHub metadata.
