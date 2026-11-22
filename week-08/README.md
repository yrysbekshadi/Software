# Week 08 — Fix and Improve a Buggy Codebase, with an Agent Skill

**Course:** AI-Driven Software Engineering (Fall 2026, KBTU SITE)
**Practice work #08** · 1 point · AI-use level: **D (AI-integrated, disclosure required)**
**Deadline:** Sunday 8 November 2026, 23:59 (Almaty)

> **This week continues Week 07.** You bring your project and your Week 07 suite over, then drop
> in a `canBook` that **we** broke on purpose, with two bugs. You reproduce each bug with a
> failing test before you touch anything. Then you write an **Agent Skill** by hand, a small
> `SKILL.md` that tells an assistant how to debug, and compare its diagnosis with a plain prompt
> on exactly the same input. You make the fix yourself: one minimal change per bug.
>
> **You need Practice #07 first.** This lab runs your Week 07 suite. Finish Week 07 Parts 0–5
> before you start here.
>
> **Your choice:** the assistant. The deck names **ChatGPT** and **Claude**, which both accept
> uploaded skills on some plans. Claude Code reads a skill from a folder. If none of these lets
> you install a skill, run the deck's **prompt-only simulation** (Part 2, step 6) and declare it.
> That costs you nothing. Freeze the assistant and record its exact model.
>
> **Identical for everyone:** the provided `canBook` in `buggy/`, the skill text (§4), the deck's
> two questions (§5, Parts 3–4), and the file layout (§2).

---

## 1. The idea of this lab

Last week you asked whether the tests deserve your trust. This week the code is the suspect, and you
already know it is broken. You do not know how badly, or whether your Week 07 suite can see it.

Debugging has a fixed order, and the deck puts it in one line:

```text
REPRODUCE → LOCALIZE → EXPLAIN → PATCH → VERIFY → IMPROVE
```

Most people skip straight to PATCH: they paste the error into a chatbot and accept whatever it
rewrites. This lab does the steps in order. You reproduce each bug with a test that fails. You form
your own hypothesis before you ask. You ask for an **explanation, not an unreviewed rewrite**. You
change one line. Then you run the test that failed and the whole suite.

Writing the procedure into a skill is the second idea. An **Agent Skill** is a folder with a
`SKILL.md`: YAML frontmatter with a name and a description of *when* to use it, then instructions.
The assistant loads only the description at first, and the full file when your request matches it.
A skill does not retrain the model, and it does not give it access to your code. It is a procedure
the model is told to follow. Whether that procedure makes the answer better is something you
measure here, not something you assume.

**Main message (the deck's own rule):** "an AI claim of 'tests passed' is not evidence". Neither is
an AI claim of "root cause found".

**Time budget:** ~20 min in class (Parts 0–2, after the Week 07 part of the session) + ~90 min at
home.

---

## 2. Deliverables

By the deadline, your branch `week-08` must contain:

```
week-08/
├── README.md                  # this file (read-only)
├── lab-report.md              # THE worksheet — fill in all 10 sections
├── AI_USAGE.md                # AI disclosure (every week)
├── submission.yml             # machine-readable declaration — facts only
├── app/                       # your Week 07 project, brought over in Part 0
│   └── src/
│       ├── booking.ts         #   the PROVIDED canBook, repaired by you   (or booking.js)
│       ├── booking.test.ts    #   your Week 07 suite + tests BUG-A and BUG-B
│       └── App.tsx …          #   the page, still calling canBook
├── buggy/
│   ├── booking.ts             # provided — the broken canBook (TypeScript). Do not edit.
│   └── booking.js             # provided — the same, JavaScript. Do not edit.
├── skills/
│   ├── bug-detector/
│   │   └── SKILL.md           # written by hand (Part 2)
│   └── bug-detector.zip       # the package you uploaded
├── evidence/
│   └── install.png            # the skill installed and enabled (or the simulation)
└── tests/
    ├── check_debugging.py     # provided checker — do not edit
    └── validate_submission.py # provided validator for submission.yml — do not edit
```

**Never commit `node_modules/` or a `.env` file.**

---

## 3. The task

The repair contract from the Lesson 08 practice deck. It restates AC1–AC6 from Weeks 06–07:

```text
Scenario: Smart Campus room availability. Continue the Smart Campus project from Practice #06 and the tests from Practice #07.
User story: As a student, I want to check a room's availability so that I can choose a valid booking time.
Use one room, fictional bookings, fixed time, and a Boolean availability decision. No login or database.

AC1 Reject start ≥ end and requests in the past.
AC2 Enforce the maximum allowed duration (120 minutes).
AC3 Reject a blocked room.
AC4 Reject overlaps; allow bookings that only touch at endpoints.
AC5 Return Available / Unavailable without changing booking data.
AC6 Preserve clear UI feedback on desktop and mobile.
```

**The controlled buggy-code challenge** (deck): the provided `canBook` has two bugs.

- **BUG-A:** the overlap logic treats touching endpoints as conflicts.
- **BUG-B:** the availability function changes the original bookings array.

You know *what* is wrong. Finding *where* it is, *why*, and *which test proves it* is the work.

**Two rules from the deck carry the whole lab:**

- **For each bug, show a failing test before fixing it.**
- **Review the proposed patch yourself, and implement only one minimal change** per bug.

---

## 4. Before class

- Your **Week 07** work: the `week-07` branch, with `week-07/app/` and its suite passing.
- Somewhere to run Vitest: the same setup as Week 07 (your computer, Bolt's terminal, or a
  Codespace).
- An assistant account where you can try to add a skill (ChatGPT or Claude), or a plan to run
  the prompt-only simulation.
- Python 3.8+ for the checker, or a Codespace.

---

## 5. The lab

### Part 0 — Setup (~5 min, in class)

1. `git checkout main && git pull && git checkout -b week-08`.
2. Bring your Week 07 project over **before** you unzip anything:
   ```text
   mkdir week-08
   git checkout week-07 -- week-07/app
   git mv week-07/app week-08/app
   ```
3. Unzip `Week_08.zip` into the root of your repository, so that `week-08/README.md` sits next to
   `week-08/app/`.
4. In `week-08/app/`: `npm install`, then `npx vitest run`. Paste the **real** output into §2.1
   of the worksheet. It should be green, because this is your Week 07 suite on your own code.
5. Fill in §1. Commit: `week-08: baseline from week 07`.

### Part 1 — Task 1: reproduce both bugs (~15 min, in class)

1. Open `buggy/booking.ts` (or `buggy/booking.js` if your project is JavaScript). Copy the **whole**
   `canBook` function, from `export function canBook` to its closing `}`, over the `canBook` in
   **your** `app/src/booking.ts`. Keep everything else in your file. **Change nothing in the
   function.**
2. Run your suite. Paste the real output into §2.2. Commit: `week-08: provided buggy canBook`.
3. Read the failures. For each one, write your **own** hypothesis in §3 **before** you ask any
   assistant: the test ID, input, expected, actual, and the line you suspect, with the reason.
4. **One bug can hide another.** Look at which tests failed and ask *why* each one failed. A test
   can fail for a different reason than its title says. If your AC5 test uses a touching request,
   which bug rejected it first?
5. Add **two regression tests** to `app/src/booking.test.ts`, with the bug's name in the title:
   - `BUG-A …`: a request that touches existing bookings and must be Available, with an exact
     `.toBe(true)`. Choose one your suite does not already have, for example a request that
     touches a booking on **both** sides.
   - `BUG-B …`: an **Available** request that touches **nothing**, such as 720–780, with
     `.toBe(true)`, followed by `bookings` compared with a copy taken before the call. It must touch
     nothing so that BUG-A cannot hide BUG-B.
6. Run the suite **on the buggy code**. Both new tests must fail. Paste the run into §2.3. Commit:
   `week-08: regression tests fail on the buggy code`.

### Part 2 — Tasks 2–3: write the skill by hand (~15 min, in class or at home)

1. Make the folder `week-08/skills/bug-detector/`. **Windows 11** (deck): File Explorer → your repo
   → `week-08/skills` → New folder `bug-detector`. **macOS / Linux:** `mkdir -p
   week-08/skills/bug-detector`.
2. Create a plain-text file `SKILL.md` in it. Use **Notepad**, choose "All files (\*.\*)" so
   it is not saved as `SKILL.md.txt`, and switch on View → Show → File name extensions to check.
   You can also use **VS Code**. On macOS, TextEdit needs Format → Make Plain Text.
3. **Type** it, do not paste a generated one. The text comes from the deck:

```text
---
name: bug-detector
description: Diagnose bugs in existing code using acceptance criteria and failing tests. Use when reviewing the Smart Campus booking application.
---
# Bug Detector

## Procedure
1. Read acceptance criteria, code, and observed failure.
2. Reproduce with the smallest deterministic input.
3. Identify the likely root cause and relevant lines.
4. Separate confirmed defects from hypotheses.
5. Suggest a minimal fix, but do not edit code yet.
6. Propose a regression test and expected result.
7. Output: defect | evidence | root cause | fix | test.
```

4. **Validate it** (deck, Task #03) and answer the four checks in §4 of the worksheet: plain UTF-8,
   named exactly `SKILL.md`; the first and closing delimiters are exactly `---`; `name` is
   lowercase with hyphens and `description` says **when** to use it; no passwords, API keys or
   private student data. `python tests/check_debugging.py` checks K1–K6 for you.
5. **Make the ZIP.** Go to the parent folder, `week-08/skills/`. On Windows, right-click
   `bug-detector` → Compress to → ZIP file. On macOS, right-click → Compress. On Linux, run
   `cd week-08/skills && zip -r bug-detector.zip bug-detector`. Name it `bug-detector.zip`, open it
   and check that `bug-detector/SKILL.md` is inside. Paste the listing into §4.
   *(The deck mentions `bug-detector/agents/openai.yaml` for ChatGPT. Add it only if ChatGPT's
   upload asks for it, following ChatGPT's own instructions. The checker ignores it.)*
6. **Install it**, and take a screenshot → `evidence/install.png`:
   - **Claude** (where Skills upload is available): Settings / Customize → Skills (labels vary) →
     Add / Upload skill → the ZIP → enable it, and check for errors.
   - **ChatGPT:** the Skills library (`/skills`), if available → Create / Upload skill → the ZIP →
     read any validation messages and fix the files if needed.
   - **Claude Code:** put the folder at `.claude/skills/bug-detector/SKILL.md` inside a project and
     check the current Claude Code documentation for how skills are triggered.
   - **If none of these works:** the deck's fallback. Paste the text of `SKILL.md` into a fresh
     chat as the first message and say it is a **prompt-only simulation, not an installed skill**.
     Take the screenshot of that, and declare `skill.environment: prompt-only`.
7. Write in §4 what happened. Commit: `week-08: bug-detector skill`.

### Part 3 — Task 4: diagnose without the skill (~10 min, at home)

1. Start a **fresh chat with no skill enabled**.
2. Prepare **one input** and save it in a text file, because you will send it twice, unchanged:
   AC1–AC6 from §3, the failing output of **one** test from §2.2, and the code of `canBook` as
   provided.
3. Send the deck's question, then the input:

```text
Find the root cause of the failed room-booking test. Propose minimal patch and regression test. Do not edit code.
```

4. Paste what you sent and the answer, unedited, into §5. Note the defects it found, any
   unsupported claims, and how good its proposed test is.

### Part 4 — Task 5: diagnose with the skill (~10 min, at home)

1. Start **another fresh chat**, this time with `bug-detector` enabled (or the simulation).
2. Send **exactly the same input**. Only the question changes, to the deck's:

```text
Use the bug-detector skill to diagnose the failed room-booking test.
```

3. Paste what you sent and the answer into §6. If the environment shows that the skill was invoked
   (a badge, a "using bug-detector" line), say so.

**Do not change the input between the two chats.** The checker compares the two inputs (L5).
They must be at least 90% alike once the question is removed.

### Part 5 — Compare fairly (~10 min, at home)

Fill in the deck's table in §7. **Judge both answers against the actual code and your tests, not
against each other**, and do not assume the skill did better. A wrong claim made confidently in a
nice table is still wrong.

### Part 6 — Task 6: repair and regression (~15 min, at home)

1. Review the proposed patches **yourself**. Then make **one minimal change for BUG-A**, the
   smallest edit to `canBook` that makes the touching cases Available. Run the test that was
   failing first (`npx vitest run -t "BUG-A"`), then the full suite. Paste the diff
   (`git diff app/src/booking.ts`) and the run into §8.1. Commit: `week-08: fix BUG-A`.
2. Do the same for **BUG-B**: the smallest edit that leaves the bookings unchanged. Paste the diff
   and the **full** run into §8.2. Every test must pass. Commit: `week-08: fix BUG-B`.
3. Check what the deck asks: booking data stays unchanged, and the endpoint-touch cases pass.
   **Capture the real terminal output. An AI saying "tests passed" is not evidence.**

The checker compares your `canBook` with the provided one: **at most 4 lines of its body may
differ** (B3). Two bugs need about two lines. A rewritten function is not a minimal change, even
if it passes.

### Part 7 — Optional, not graded (~ whatever you have left)

- **A second skill, `regression-tester`** (deck): a folder with a `SKILL.md` that tells the
  assistant to derive tests from acceptance criteria, use a fixed clock and fresh fixtures, assert
  exact results and non-mutation, run tests only if a terminal tool is available, and report tests
  it did not run honestly. Compare its proposed coverage with your Week 07 suite.
- **MCP** (deck): a skill tells the assistant *how* to debug, and MCP can give it controlled access
  to code or repository information. In a supported environment, connect an instructor-approved
  **read-only** repository or filesystem MCP server. Never grant write permissions you do not need,
  and never expose secrets.

Put anything you try here in `AI_USAGE.md`. It changes no check and no mark.

### Part 8 — Report, declaration, submit (~15 min, at home)

1. Write §9.2 (one limitation, from what actually happened) and the conclusion in §10, 80–150
   words, the deck's 3–5 sentences: *Did the skill help? What did the tests actually prove?*
2. From inside `week-08/`, run the checker with `python tests/check_debugging.py`. Every FAIL or
   ERROR you keep goes in §9.1 with the reason.
3. Fill in `AI_USAGE.md`.
4. Commit, note the hash with `git rev-parse --short HEAD`, fill in `submission.yml`, run the
   validator, commit, push, and open the PR (§9).

---

## 6. What "minimal" and "fixed" mean here

| Bug | Fixed when | Proved by |
| --- | --- | --- |
| BUG-A | a request that only touches a booking is Available; overlaps are still rejected | T01, T08, your `BUG-A` test, and T09–T12 still passing |
| BUG-B | `canBook` changes nothing in `bookings`: no `push`, `splice`, `sort`, and no assignment | your `BUG-B` test and the Week 07 AC5 test |

**One minimal change per bug** means one edited or deleted line each, in two separate commits. Do
not rename variables, reformat the function or "improve" it on the way. A diff a reviewer can read
in five seconds is the goal.

---

## 7. Checking your work

### Verdicts

```
PASS   the check found what it was looking for
FAIL   the content is there but wrong, or not enough of it
ERROR  it could not check: a file, a folder or a section is missing
```

From inside `week-08/`:

```text
python tests/check_debugging.py
```

It runs 31 checks:

| Checks | What they look at |
| --- | --- |
| **B1–B6** | `app/`: the booking module has `function canBook` (B1), the page still calls it (B2); the body differs from the provided one in **1 to 4 lines** (B3); the overlap test is strict, so touching is not a conflict (B4); nothing in `canBook` changes `bookings` (B5); no `node_modules/` or `.env` (B6). |
| **S1–S5** | Your suite: imports `vitest` and the real `./booking` (S1); nothing mocked or skipped (S2); T01–T14 still there, 19 tests or more (S3); a `BUG-A` test asserting `.toBe(true)` (S4); a `BUG-B` test on an Available request that compares `bookings` (S5). |
| **K1–K7** | The skill: `SKILL.md` named exactly (K1); frontmatter between `---` lines (K2); `name: bug-detector` (K3); a description that says when (K4); the deck's seven steps (K5); nothing that looks like a key or password (K6); the ZIP holds `bug-detector/SKILL.md`, identical to the committed one (K7). |
| **E1** | `evidence/install.png`. |
| **R1–R3** | §2.1 green on your own code (R1); §2.2 failing on the buggy code, and in §2.3 `BUG-A` and `BUG-B` among the failures (R2); §8.2 all passing, with **the same number of tests as your committed files** (R3). |
| **L1–L9** | The worksheet: setup (L1), defect log (L2), the four checks + ZIP listing + installation (L3), the question without the skill as sent, with its input and the answer (L4), the skill question with **the same input** and the answer (L5), the comparison (L6), one diff per bug (L7), one limitation (L8), the conclusion (L9). |

**The checker never runs your tests and never talks to an assistant.** It reads files. The grader
can run your suite, and pasted output that the committed suite cannot produce costs the whole
*Evidence and honesty* criterion.

The first run on the untouched folder gives `0 PASS · 12 FAIL · 19 ERROR`. That is the intended
start.

---

## 8. The declaration — `submission.yml`

Facts only. From inside `week-08/`:

```text
python tests/validate_submission.py
```

- **`checker.commit` is the commit you ran the checker at**, on your `week-08` branch.
- **Your numbers are re-run at the last commit of your pull request.** Numbers that do not match cost
  the whole *Evidence and honesty* criterion, so run the checker again after any change.
- **`counts.lines_changed`** is the number the checker prints under B3.
- **A FAIL you report costs you nothing extra.** If the upload refused your skill and you could not
  get a screenshot of the simulation either, list `E1` in `known_fails` and say why in §9.1.

---

## 9. Submit

1. Push the branch with `git push -u origin week-08`.
2. Open a Pull Request `week-08 → main` in your own repository. Title: `Week 08 — Fix and Improve a
   Buggy Codebase`. Write the description in the fixed shape from `SETUP.md` §4.
3. **Leave the PR open. Do not merge it.**
4. In the Teams assignment *Practice #08*: **+ Add work → Link → paste the pull request URL.**

The deck asks you to email screenshots to the main lecturer. **That does not apply to our
groups.** The PR already holds the project, `SKILL.md`, the ZIP, the installation screenshot or
fallback note, both responses, the defect log, the diffs and the real test output.

**Deadline:** Sunday 8 November 2026, 23:59 (Almaty). Late submissions follow the course policy.

---

## 10. Grading — 1 point, 4 × 0.25

| Criterion | 0.25 when … |
| --- | --- |
| **Reproduction and repair** | Both bugs are reproduced by a failing test before any fix (§2.3); the defect log has your own hypotheses; each bug is fixed with one minimal change in its own commit (B3–B5); the final suite is green and still holds T01–T14 plus `BUG-A` and `BUG-B`. |
| **The skill** | `SKILL.md` is typed by hand, valid and identical to the one in the ZIP; the installation was attempted and evidenced, or the prompt-only simulation was run and declared. |
| **Comparison and judgement** | Both chats received the same input (§5, §6); both questions were sent as written; §7 judges every criterion against the actual code; the limitation in §9.2 comes from what happened. |
| **Evidence and honesty** | §9 and §10 are your own; `AI_USAGE.md` is complete; `submission.yml` passes the validator and its numbers match the re-run; the PR is open with 3 or more meaningful commits. |

**A FAIL you report and explain costs you nothing. One you hide costs the whole criterion.**

**Not accepted:** a fix applied before any failing test · `canBook` rewritten instead of repaired ·
a generated `SKILL.md` presented as typed · a ZIP of an empty folder or of `SKILL.md.txt` ·
different input in the two chats · "tests passed" without pasted output · findings that name no
bug, no test and no AC ("the skill was better") · a merged PR, a repo link, or an emailed
submission.

---

## 11. FAQ

**My project is JavaScript.** Copy the function from `buggy/booking.js`. Everything else is the
same.

**My Week 07 `canBook` used `export const canBook = (…) =>`.** Replace it with the provided
`export function canBook`. Keep the rest of the file. The page's import does not change.

**TypeScript complains about `bookings.push` in the provided function.** Interesting. Your Week 07
type was probably `readonly Interval[]`, and the compiler sees BUG-B before any test does. Write
that in §3. Vitest does not type-check, so the tests still run.

**My Week 07 AC5 test already fails on the buggy code. Do I still need `BUG-B`?** Yes. Check *why*
it fails. If its request touches the booking, BUG-A rejects it before the push ever happens. It
fails for the wrong reason, and it would still fail after a wrong fix. `BUG-B` must fail for the
right reason.

**The assistant edited my code although the question said "Do not edit code".** Do not use what it
wrote. Note it in §7 under *Unsupported claims* or *Minimal proposed patch*. It is a finding about
the assistant.

**Neither answer found BUG-B.** Then say so in §7. Your `BUG-B` test found it, and that is the
point of §10's question "what did the tests actually prove?".

**The skill upload is not available on my plan.** Run the prompt-only simulation (Part 2, step 6),
declare `skill.environment: prompt-only`, and screenshot the chat. It costs nothing.

**Where does the grader run my files?** The checker reads them and runs nothing. The grader can run
your suite in `app/`.
