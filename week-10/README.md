# Week 10 — Risk Review and Refactor: Audit Your Project Before an Agent Touches It

**Course:** AI-Driven Software Engineering (Fall 2026, KBTU SITE)
**Practice work #10** · 1 point · AI-use level: **D (AI-integrated, disclosure required)**
**Deadline:** Sunday 22 November 2026, 23:59 (Almaty)

> **This week continues your Smart Campus project** from Weeks 07–08, the one-room checker with
> AC1–AC6 and your Vitest suite. You do not build a feature. You **audit** the project: what could go
> wrong, what an AI reviewer claims could go wrong, which of those claims are true, and whether the
> repository is ready for an agent to work in at all. Then you fix two real risks and make a release
> decision you can defend.
>
> **Two practices in one.** This week covers Practice #09 (repository
> instructions and one justified refactor) and Practice #10 (risk review). It is one assignment,
> one mark.
>
> **We give you the agent playbook.** `provided/AGENTS.md` is the instructions file an earlier
> exercise left in the project. It is written the way such files usually are: in a hurry, and partly
> wrong. Auditing it is Task 6.
>
> **Your choice:** the assistant, as long as it can read your project: **Bolt.new** (the deck's
> tool), Claude Code, Cursor, Copilot, or a chat assistant you paste the files into. Freeze it for
> the whole lab and record its exact model.
>
> **Identical for everyone:** `provided/AGENTS.md`, the decks' five prompts (Parts 1, 2, 6, 8 and 9),
> the scoring scale, the readiness rows in lecture terms (§6), and the file layout (§2).

---

## 1. The idea of this lab

An agent working in your repository believes what the repository tells it. If the README is out of
date, the agent follows it. If the test command in `AGENTS.md` does not exist, the agent cannot
check its own work, and it may tell you that it did. In the lecture this was the list of
**what breaks agents**: no tests, no docs or standards, an unreliable build, no observability, a
complicated setup and no security checks. A human works around all of these. An agent does not.

The second idea is the deck's main message:

> **A risk claim requires evidence; an AI suggestion is not proof.**

An AI reviewer will give you a long, confident list of risks. Some are real. Some are true of
*some* project, but not of yours. Some cite a file that does not exist. Your job is to sort them
by looking at the code yourself, and to keep the three words apart:

| Word | Means | Example |
| --- | --- | --- |
| **Risk** | a plausible event with a potential adverse consequence | "an agent deploys an unreviewed build" |
| **Finding** | observed evidence | "`AGENTS.md` line 38 tells the agent to run `netlify deploy --prod`" |
| **Mitigation** | a focused change that reduces likelihood or impact | the line replaced by "never deploy" |
| **Residual risk** | what remains after the mitigation is verified | 1 × 3 = 3: a human could still deploy by hand |

**Time budget:** ~30 min in class, where the instructor walks through the parts (no live demo this
week), + ~3 h at home. Do Parts 0–3 first: they need nothing from the later parts.

---

## 2. Deliverables

By the deadline, your branch `week-10` must contain:

```
week-10/
├── README.md                  # this file (read-only)
├── lab-report.md              # THE worksheet — fill in all 10 sections
├── AI_USAGE.md                # AI disclosure (every week)
├── submission.yml             # machine-readable declaration — facts only
├── app/                       # your Week 08 project, brought over in Part 0
│   ├── AGENTS.md              #   copied from provided/, then patched in Part 6
│   ├── package.json
│   └── src/
│       ├── booking.ts         #   canBook        (or booking.js)
│       ├── booking.test.ts    #   your suite + one regression test named after a risk (Part 7)
│       └── App.tsx …
├── provided/
│   └── AGENTS.md              # provided — the playbook as it was. Do not edit.
├── evidence/
│   ├── ui-desktop.png         # manual UI check, desktop width (Part 7)
│   └── ui-mobile.png          # manual UI check, phone width (Part 7)
└── tests/
    ├── check_audit.py         # provided checker — do not edit
    └── validate_submission.py # provided validator for submission.yml — do not edit
```

**Never commit `node_modules/`, a `.env` file, or any real key, password or personal data.**

---

## 3. The project and its contract

The scope from the practice deck (slide 12), unchanged:

```text
Continue the Room Availability Checker. One room, fictional bookings, no login and no database.
Retain the existing acceptance contract and repository instructions.
Do not introduce real personal information, secrets or external production services.
```

The acceptance contract you must preserve (slide 13; the same AC1–AC6 as Weeks 07–08):

```text
AC1 Reject start ≥ end and requests in the past.
AC2 Enforce the maximum allowed duration (120 minutes).
AC3 Reject a blocked room.
AC4 Reject overlaps; allow bookings that only touch at endpoints.
AC5 Return Available / Unavailable without changing booking data.
AC6 Preserve clear UI feedback on desktop and mobile.
```

**Your starting point** is your Week 08 project (`week-08/app/`), with BUG-A and BUG-B fixed. If
you did not finish Week 08, use your Week 07 project (`week-07/app/`) and declare it in
`submission.yml`. The starting point never affects the mark; what you find in it does.

---

## 4. Before class

- Your **Week 08** branch with `week-08/app/` and its suite passing (or Week 07, see §3).
- Somewhere to run Vitest, as in Weeks 07–08: your computer, Bolt's terminal, or a Codespace.
- An assistant that can read the whole project (see the callout at the top).
- Python 3.8+ for the checker.

---

## 5. The lab

### Part 0 — Setup and a checkpoint (~5 min)

1. `git checkout main && git pull && git checkout -b week-10`.
2. Bring your project over **before** you unzip anything:
   ```text
   mkdir week-10
   git checkout week-08 -- week-08/app
   git mv week-08/app week-10/app
   ```
   (From Week 07: replace `week-08` with `week-07` in both lines.)
3. Unzip `Week_10.zip` into the root of your repository, so that `week-10/README.md` sits next to
   `week-10/app/`.
4. Copy the playbook into the project: `cp week-10/provided/AGENTS.md week-10/app/AGENTS.md`
   (Windows: copy and paste it in File Explorer). Change nothing in it yet.
5. Commit: `week-10: baseline from week 08`. **This commit is your checkpoint** (deck: "save a copy
   before any agent-assisted changes"). Record its hash (`git rev-parse --short HEAD`) in §1.
   If an agent breaks something later, `git checkout <hash> -- week-10/app` brings the project back.

If you work in Bolt.new, import or push this branch so that Bolt sees `AGENTS.md` at the
project root.

### Part 1 — Task 1: the baseline (~10 min)

1. Find the project's README, `AGENTS.md`, the tests and the `scripts` in `package.json`.
2. In `week-10/app/`, run `npm install`, then each command of §2.1 of the worksheet, **including the
   test command that `AGENTS.md` names**. Record for each one whether it exists and what happened:
   `pass`, `fail`, `missing` (no such script) or `not run` (say why).
3. Paste the real Vitest output into §2.2. It should be green.
4. **Make the agent read the playbook** (Practice #09). Do not assume your tool loads `AGENTS.md`
   by itself; Bolt.new may not. Send this prompt, **exactly as written**, and paste it with the
   answer into §2.3:

```text
Read the root AGENTS.md before making changes. Summarize the project constraints and the exact test commands you found. Do not edit anything yet. If you cannot read AGENTS.md, tell me, and I will paste its content. Do not claim that AGENTS.md was automatically loaded.
```

   Then write in §2.3 which rules in its summary are wrong for this project. An agent repeats
   what the file says, including the mistakes. That is why Part 6 audits the file.

A command that does not exist is a **finding**, not a failure of yours. Write it down. You will
need it in Parts 4 and 5.

### Part 2 — Task 2: a read-only AI review (~10 min)

1. Make sure the assistant **cannot edit**. In Bolt.new, use **Plan** mode (the button beside the
   send arrow). In Claude Code, use plan mode. In a chat assistant, paste the files and nothing can
   change. Afterwards, `git status` must show no change in `app/`.
2. Send the deck's prompt, **exactly as written**:

```text
Act as a cautious software reviewer. Inspect this Smart Campus Room Availability Checker WITHOUT editing files. Identify risks in correctness, security, privacy, reliability, maintainability, and agent operations. For each risk, cite the exact file/function or missing check, explain the impact, suggest a way to verify it, and state uncertainty. Do not invent test results.
```

3. Paste what you sent and the whole answer, unedited, into §3.1.

### Part 3 — Task 3: challenge the AI's findings (~10 min)

Pick **at least five** of the risks the assistant proposed, across **at least three** categories.
For each one, **open the file or function it cites and look for yourself**. Then label it in §3.2:

| Label | When |
| --- | --- |
| `confirmed` | you found the evidence in the code, the files or a run you made |
| `plausible` | it could be true, but you have not been able to verify it (deck: "plausible / unverified") |
| `unsupported` | the cited file, function or behaviour is not there, or the claim contradicts what you see |

**Do not present an unexecuted test as a passed test.** If the assistant says "the tests pass" and
you did not run them, that claim is `unsupported` until you do.

### Part 4 — Task 4: the risk register (~20 min, at home)

Build the register in §4.1. **At least five risks**, each one `confirmed` or `plausible`. At least
**two must be confirmed**, because you will mitigate two in Part 8. Unsupported claims stay in §3.2.
You may add risks the assistant missed. Those are often the best ones.

| Column | What goes in it |
| --- | --- |
| **ID** | `R1`, `R2`, … |
| **Category** | `Correctness`, `Security`, `Privacy`, `Reliability`, `Maintainability` or `Agent operations` (the prompt's six). At least three different ones across the register. |
| **Cause → event → consequence** | one line: what causes it, what happens, what it costs |
| **Component** | the exact file or function, as a path inside `app/` (`src/App.tsx`, `src/booking.ts canBook`, `AGENTS.md`, `package.json`), **or** `missing: <the check that does not exist>` |
| **Evidence** | what you saw: a line, a run, a missing file |
| **Status** | `confirmed` or `plausible` |
| **L**, **I**, **Score** | likelihood 1–3 × impact 1–3 = score 1–9 (the deck's scale, below) |
| **Mitigation**, **Owner**, **Verification** | the focused change, who does it, and how you will know it worked |

```text
Likelihood: 1 unlikely, 2 possible, 3 likely.
Impact:     1 minor,    2 moderate, 3 serious.
Risk score = likelihood × impact (range 1–9).
```

Then, in §4.2, **rank the top two for action**: two confirmed risks, highest score first. No
confirmed risk left out may score higher than the second of your two. **Justify each score with
evidence**, not with how worried you feel.

### Part 5 — Task 5: the agent-readiness audit (~15 min, at home)

The lecture's readiness levels, used as an audit rubric (deck: "not an automatic certification").
Fill in §5.1, one row each, `yes` or `no`, and the evidence: the file or the script that shows it.

| Row | Level | `yes` when `app/` has … |
| --- | --- | --- |
| 1a | 1 Baseline | a **formatter**: a Prettier config, or `prettier` in `package.json` |
| 1b | 1 Baseline | a **linter**: an ESLint config, or `eslint` in `package.json` |
| 1c | 1 Baseline | **type checks**: a `tsconfig.json` and `typescript` in `package.json` |
| 1d | 1 Baseline | **unit tests**: test files and `vitest` in `package.json` |
| 1e | 1 Baseline | **pinned dependencies**: a committed lockfile (`package-lock.json`, `pnpm-lock.yaml` or `yarn.lock`) |
| 2a | 2 Documented | a **`.env.example`** |
| 2b | 2 Documented | **architecture notes**: a README or doc that says which module does what |
| 2c | 2 Documented | an **`AGENTS.md`** |
| 3a | 3 Agent-ready | **CI**: a workflow that runs the checks on every push (`.github/workflows/`) |
| 3b | 3 Agent-ready | **hooks**: pre-commit hooks (`.husky/`, `lint-staged`, `simple-git-hooks` or `.pre-commit-config.yaml`) |
| 3c | 3 Agent-ready | **integration checks**: a test of the page or of more than one module together |
| 3d | 3 Agent-ready | **reviewable evidence**: test output an agent's change must attach (a CI log, a PR template) |

**The level** (§5.2) uses the lecture's 80% threshold: a level is reached when at least 80% of its
rows are `yes` **and** every level below it is reached. That is 4 of 5 at Level 1, 3 of 3 at
Level 2 and 4 of 4 at Level 3. If Level 1 is not reached, the level is **0**. Then list the
missing evidence: what would have to exist to reach the next level.

The checker compares rows 1a–1e, 2a, 2c and 3b with the files in `app/`, and your level with
your rows. A `yes` with no file behind it is exactly the kind of claim this lab is about.

Also note in §5.2 whether the README is accurate and the folder layout is clear. If there is no
README, that is the finding.

### Part 6 — Task 6: audit the agent playbook (~15 min, at home)

1. Send the deck's prompt, **exactly as written**, with the assistant able to read `app/AGENTS.md`
   and the project:

```text
Review AGENTS.md and project documentation only. Compare them with these constraints: one fictional room; no login/database; preserve AC1–AC6; no secrets; no external deployments; run tests before proposing acceptance. Report missing or conflicting rules. Draft a minimal patch to AGENTS.md, but wait for my approval before applying it.
```

2. Paste what you sent and the answer into §6.1.
3. **Check every rule yourself** against the six constraints and against `package.json`. Record
   each finding in §6.2 with your decision: `approve`, `reject` or `modify`, and why. Do not
   approve a change you have not read.
4. Apply **only what you approved** to `app/AGENTS.md`. Paste `git diff app/AGENTS.md` into §6.3.
   Commit: `week-10: AGENTS.md patch, approved`.

**What the checker reads in your final `app/AGENTS.md`:**

- **The six constraints.** Each one is stated as a rule (C1–C6), and no line contradicts it. A
  line that mentions a database, a login, a deployment or secrets must forbid it, not permit it.
  AC1–AC6 are all listed, and AC4 says what the contract says.
- **Every command it names exists.** `npm run <x>` needs a script `<x>` in `app/package.json`,
  `npm test` needs a `test` script, and `npx vitest` needs `vitest` in `package.json` (A3).
- **The patch is minimal.** The same headings as `provided/AGENTS.md`, and between 1 and 14 lines
  changed (A2). "Minimal" is the prompt's word. A rewritten file is not a patch.

### Part 7 — Task 7: verify safely (~15 min, at home)

1. Choose a **confirmed risk in the code** (`src/`) that a test can show. Add a **regression test**
   whose title starts with the risk's ID, for example `test('R3 AC1: …', …)`, to
   `app/src/booking.test.ts`. Run it **before** you mitigate anything. It must fail, and that
   failure is your evidence that the risk is real. Paste the run into §7.1.
2. Run the page and **check the UI by hand**, at desktop width and at phone width (the browser's
   device toolbar, or your phone). Check that the feedback is clear (AC6) and that nothing is cut
   off or overlapping. Take two screenshots: `evidence/ui-desktop.png` and
   `evidence/ui-mobile.png`. Record what you checked in §7.2.
3. In §7.3, **list explicitly the tests and checks you did not run**, and why. "None" is an answer,
   if it is true.

*Optional* (Practice #09, Task 6): if your suite lacks any of these cases, ask the agent for them
with the deck's prompt, and review every assertion it writes:

```text
Create or update regression tests for: past time, reversed interval, 121-minute duration, blocked room, overlap, touching endpoints, and unchanged fixtures. Explain each expected result from AC1-AC6. Do not weaken or delete existing assertions.
```

Commit: `week-10: regression test for R<n> fails before the fix`.

### Part 8 — Task 8: mitigate two risks (~20 min, at home)

1. Choose **two confirmed, meaningful risks** from the register (normally your top two). One of
   them must be the risk from Part 7, the one with the regression test. **That one is mitigated by
   a refactor** (Practice #09): send the deck's prompt, exactly as written, and paste it in that
   mitigation's section of §8:

```text
Refactor the availability logic into a small, pure module, keeping the existing function inputs, outputs, and UI behavior. Use a pattern only if the identified design problem justifies it. Do not add new features or dependencies. Show the files you plan to edit before making changes.
```

   Then write the **problem → pattern → benefit** line in two sentences: the design problem, the
   pattern you used (an extracted pure function or module is enough; Adapter or Strategy **only**
   when there really are two data shapes or two policies; "no pattern" is a valid answer), and what
   it bought. Behaviour must not change: the whole suite stays green before and after.
2. For each one, ask the agent for a **minimal patch** and **review the diff before you accept
   it**. Approve only changes within scope. **Reject unrelated refactoring**, renamed variables
   and "improvements" you did not ask for. Write down what you rejected.
3. Apply it, rerun the tests, and commit each mitigation separately
   (`week-10: mitigate R<n> — <what>`). Paste each diff into §8.1 and §8.2.
4. **Revise the residual risk** in §8.3: the likelihood and impact after the mitigation, with
   evidence. The score after may not be higher than before.
5. Paste the **full final run** into §8.4. Every test must pass.

The patched `AGENTS.md` from Part 6 may count as one of your two mitigations if your register has
it as a confirmed `Agent operations` risk. The other must then be the code risk from Part 7.

*Optional, not graded* (Practice #09): the same refactor request once **without** `AGENTS.md` in a
fresh conversation, once with it supplied explicitly. Compare scope, unneeded patterns, test
quality. A difference does not prove your tool loads the file automatically.

### Part 9 — Task 9: the background-agent thought experiment (~10 min, at home)

Assume an agent works on this project **asynchronously, on a separate branch, while you are away**
(lecture: background coding agents). In §9.1 write the rules for it, one row each: **isolation**,
**permitted files**, **commands**, **prohibited actions**, **required evidence** (a diff, test
output, build result, a review note), and **what must happen before merging or deploying**. Be
specific to this project: name its files and its commands.

*Optional, not graded:* the deck's checklist prompt. Send it, paste the answer into §9.2, and
compare it with your own rules:

```text
Design a read-only review checklist for a background coding agent working on Smart Campus. Include: isolated branch/worktree; no credentials; no deployment; test and build commands; risk register updates; evidence for each claim; a summary of changed files; and an explicit human approval gate before merge. Do not claim the agent ran unless a real tool execution is recorded.
```

### Part 10 — The release decision, declaration, submit (~15 min, at home)

1. **Decide** in §10 (deck, slide 32):
   - **GO**: key checks pass and no unacceptable unresolved risks remain.
   - **CONDITIONAL**: known limitations have documented owners and controls.
   - **NO-GO**: serious unmitigated risks or missing critical verification.

   **GO is not allowed while any confirmed risk still scores 6 or more** (its §8.3 score if you
   mitigated it, its §4.1 score if not). Then justify it in 80–150 words, from the register, the
   tests and what you are still unsure about. Name at least two risk IDs.
2. From inside `week-10/`, run `python tests/check_audit.py`. Every FAIL or ERROR you keep goes in
   §9.3 with the reason.
3. Fill in `AI_USAGE.md`.
4. Commit, note the hash with `git rev-parse --short HEAD`, fill in `submission.yml`, run the
   validator, commit, push, and open the PR (§9).

---

## 6. Verdicts

```
PASS   the check found what it was looking for
FAIL   the content is there but wrong, or not enough of it
ERROR  it could not check: a file, a folder or a section is missing
```

The register's labels are yours (`confirmed` / `plausible` / `unsupported`). The checker's
verdicts are about your files, never about your project's quality: a Level 0 project audited
honestly passes every check.

---

## 7. Checking your work

From inside `week-10/`:

```text
python tests/check_audit.py
```

It runs 31 checks:

| Checks | What they look at |
| --- | --- |
| **B1–B2** | `app/`: a `package.json` and a booking module with `canBook` (B1); no `node_modules/`, no `.env`, under 5 MB (B2). |
| **S1–S2** | Your suite: imports `vitest` and the real `./booking`, nothing mocked, skipped or focused (S1); a regression test whose title starts with the ID of a risk you mitigated in §8 (S2). |
| **A1–A3** | `app/AGENTS.md`: present (A1); a minimal patch of `provided/AGENTS.md`, with the same headings and 1–14 lines changed (A2); every command it names exists in `package.json` (A3). |
| **C1–C6** | `app/AGENTS.md` states each of the six constraints from Part 6 and contradicts none: one fictional room (C1), no login or database (C2), AC1–AC6 with AC4 as the contract says (C3), no secrets (C4), no external deployments (C5), tests before acceptance (C6). |
| **E1–E2** | `evidence/ui-desktop.png` and `evidence/ui-mobile.png`. |
| **R1–R3** | §2.2 a real Vitest run (R1); §7.1 the regression test failing before the mitigation (R2); §8.4 the final run, all passing, with **the same number of tests as your committed files** (R3). |
| **L1–L13** | The worksheet: setup (L1), the baseline commands and the read-the-playbook prompt with its answer (L2), the review prompt as sent and its answer (L3), five or more claims challenged across three categories (L4), the register (L5), the top two (L6), the audit rows against your files (L7), the level by the 80% rule with the missing evidence (L8), the playbook prompt, findings, decisions and diff (L9), the UI check and the tests not run (L10), two mitigations with residual scores, one of them the refactor prompt with its problem → pattern → benefit line (L11), the background-agent rules (L12), the decision and the conclusion (L13). |

**The checker never runs your tests and never talks to an assistant.** It reads files. The grader
re-runs your suite. Pasted output that the committed suite cannot produce costs the whole
*Evidence and honesty* criterion.

The first run on the untouched folder gives `0 PASS · 16 FAIL · 15 ERROR`. That is the intended
start.

---

## 8. The declaration — `submission.yml`

Facts only. From inside `week-10/`:

```text
python tests/validate_submission.py
```

- **`checker.commit` is the commit you ran the checker at**, on your `week-10` branch.
- **Your numbers are re-run at the last commit of your pull request.** Numbers that do not match cost
  the whole *Evidence and honesty* criterion, so run the checker again after any change.
- **`project.baseline_commit`** is the checkpoint from Part 0.
- **A FAIL you report costs you nothing extra.** List it in `known_fails` and say why in §9.3.

---

## 9. Submit

1. Push the branch with `git push -u origin week-10`.
2. Open a Pull Request `week-10 → main` in your own repository. Title: `Week 10 — Risk Review and
   Refactor`. Write the description in the fixed shape from `SETUP.md` §4.
3. **Leave the PR open. Do not merge it.**
4. In the Teams assignment *Practice 10*: **+ Add work → Link → paste the pull request URL.**

The deck asks you to email screenshots to the main lecturer. **That does not apply to our
groups.** The PR already holds the project, the register, the audit, the `AGENTS.md` review, both
mitigations, the test output and the release decision.

**Deadline:** Sunday 22 November 2026, 23:59 (Almaty). Late submissions follow the course policy.

---

## 10. Grading — 1 point, 4 × 0.25

| Criterion | Complete (0.25) when … | Checks it needs |
| --- | --- | --- |
| **Risk review and release** | The review prompt was sent as written to an assistant that could not edit; five or more AI claims checked against the code yourself, with honest labels; a register of five or more risks with real components, evidence and correct scores; the top two justified; six specific background-agent rules; a release decision that follows from the register | L3 L4 L5 L6 L12 L13 |
| **Readiness and playbook** | Every audit row matches your files, the level follows the 80% rule, and the gaps are named; every finding in `AGENTS.md` decided by you; a minimal, approved patch that meets the six constraints with commands that exist | A1–A3 C1–C6 L7 L8 L9 |
| **Verification and mitigation** | A baseline run and the agent's summary of the playbook; a regression test that fails before and passes after; the UI checked at two widths; tests not run listed; two confirmed risks mitigated with reviewed diffs, one by the refactor prompt with a justified (or no) pattern, rejected changes named, and residual scores revised; the final suite green | B1 S1 S2 E1 E2 R1 R2 R3 L2 L10 L11 |
| **Evidence and honesty** | §1 complete; no secrets or `node_modules`; §9.3 and §10 your own; `AI_USAGE.md` complete; `submission.yml` passes the validator and its numbers match the re-run; the PR is open with 3 or more meaningful commits | B2 L1 |

**A FAIL you report and explain costs you nothing extra; one you hide costs the whole criterion.**
A criterion is Complete when the checks it names pass. A failing check you report and explain in
§9.3 can lower its own criterion to Partial, and never anything else.

**Not accepted:** an AI review that edited files · a pattern added with no problem it solves · labels copied from the assistant without looking ·
"the tests pass" without pasted output · a register of generic risks with no file, function or missing
check · an `AGENTS.md` rewritten from scratch · a GO with a confirmed risk still at 6 or more ·
real names, keys or personal data anywhere · a merged PR, a repo link, or an emailed submission.

---

## 11. FAQ

**The assistant edited my files during the review.** Undo it (`git checkout -- app`), note it in
§3.1 as a finding about the assistant, and send the prompt again in a read-only mode. An
assistant that ignores "WITHOUT editing files" is itself an `Agent operations` risk.

**My project has no README.** Then row 2b is `no`, and "no README" belongs in §5.2 and probably in
the register. You do not have to write one, but you may, as a mitigation.

**My `package.json` has no `test` script.** Then `npm test` and `npm run test:unit` are both
`missing` in §2.1. Run `npx vitest run` instead. Whether `AGENTS.md` should name `npx vitest run` or
you should add a `test` script is your decision in Part 6. Either way, A3 checks that the command
exists.

**Every risk I find is minor.** Then score them honestly. A register full of 1s and 2s, each with
evidence, is better than invented 9s. Your release decision will follow from it.

**The AI's list has no `unsupported` claim.** That happens. Look harder at the files it cites and
at any "the tests pass" or "this is vulnerable to SQL injection" line. If all five really check
out, say so in §3.2.

**Can the `AGENTS.md` patch be one of my two mitigations?** Yes, if your register has it as a
confirmed risk. The other mitigation must be the code risk with the regression test (Part 7).

**Can I use my SIS #04 project instead?** No. It has several rooms, and the scope here is one room.
Use Week 08 (or Week 07).

**Where does the grader run my files?** The checker reads them and runs nothing. The grader runs your
suite in `app/` in an isolated container, without network access.
