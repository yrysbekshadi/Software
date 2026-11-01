# SIS #03 — AI-Assisted Coding, Vibe Coding and Prototype Cleanup

**AI-Driven Software Engineering · KBTU SITE · Fall 2026**
**SIS #03 · 2 points · individual · deadline Sunday 1 November 2026, 23:59**
**AI use: required** — Level D, and the working process below is built around it.

> **You have done most of the building already, and you may reuse it.** This assignment combines
> the `can_book` function from **Practice #05** with the Bolt.new page from **Practice #06**, under
> the same acceptance criteria AC1–AC6. If you did those practices, **bring their first versions
> (v1) in unchanged** and declare it (§3). What is new is the evidence: one test table covering
> both artifacts, traceability, an issue log, the AI's critique checked claim by claim, an
> analysis of the agent loop, and a reflection. If you missed a practice, generate that v1 fresh.
>
> **Your choices, frozen once made:** the coding assistant for the Python part (any you have —
> record the **exact model**; "ChatGPT" is a tool, not a model; `not displayed` is accepted when
> the tool hides it) and **the language** of the function. Python is recommended because the
> checker runs Python code (Path A); any other language is Path B and loses no marks (§5).
> The web prototype is **Bolt.new** for everyone, as in Practice #06.
>
> **What stays identical for everyone:** the scenario, AC1–AC6, the contract
> `can_book(start, end, now, blocked, existing)`, the twelve cases T1–T12, the word limits, the
> file and folder names below.

This is **Assignment #03** of the course — the same scenario, criteria, tasks and evidence that
every group receives. The report is a Markdown file in your repository; you get a checker you can
run yourself, and the rubric is written below.

**The submission is the link to your open pull request, pasted into the Teams assignment** — not a
file upload, not an e-mail.

---

## What you hand in

```
sis-03/
├── README.md                 this file — read-only
├── report.md                 ← the ONLY file you write prose in: 13 numbered sections
├── AI_USAGE.md               ← your AI disclosure
├── submission.yml            ← the declaration: facts only, filled in last (§13)
├── code/
│   ├── booking.py            ← your FINAL can_book            (Path B: booking.<ext>)
│   ├── test_booking.py       ← your FINAL tests               (Path B: your test file)
│   └── original/
│       └── booking_v1.py     ← the assistant's FIRST version, unedited
├── web/
│   ├── original/             ← Bolt's FIRST version, downloaded and unzipped, unedited
│   └── final/                ← your FINAL Bolt project, downloaded and unzipped
├── evidence/
│   ├── web-v1.png            ← the first usable preview
│   ├── before-1.png          ← one meaningful improvement: before …
│   ├── after-1.png           ← … and after
│   └── final-narrow.png      ← the final page at phone width (portrait)
└── tests/
    ├── check_sis.py              checks behaviour and shape — do not edit
    └── validate_submission.py    checks submission.yml against it — do not edit
```

Screenshots may be `.png` or `.jpg`, with exactly these names. No `node_modules/`, no `.env`.

**Time:** about 4–5 hours if you reuse your practice work, 6–7 if you start fresh. Spread it over
at least two days; the test table (§7) and the agent analysis (§10) take longer than the prompts.

---

## 1. The system

> **User story:** As a student, I want to check a room's availability so that I can choose a
> valid booking time.
>
> One responsive page for **one selected room**, with **fictional** booking data. The page
> **checks availability only**; it does not create or confirm bookings. Exclude login, database,
> backend, external API, payments and unrelated features.

| | Required rule |
| --- | --- |
| **AC1** | Candidate times are integer minutes after midnight: `0 <= start < end <= 1440`; start must be **strictly after** now. |
| **AC2** | Duration must not exceed 120 minutes. Exactly 120 minutes is permitted. |
| **AC3** | Reject every request when the selected room is blocked. |
| **AC4** | Reject overlap with any existing booking. Intervals **touching at an endpoint do not overlap**. |
| **AC5** | Display an unambiguous Available / Unavailable result; **do not mutate** existing bookings. |
| **AC6** | Provide understandable validation feedback and a usable narrow/mobile layout. |

Assume `now` is valid (0–1439). **Treat these criteria as fixed: reject AI suggestions that change
their meaning** — a cleaning buffer, a 90-minute limit, a Book button. Intervals include their
start and exclude their end.

**The contract** (unchanged since Practice #05): `can_book(start, end, now, blocked, existing)` —
`existing` is a collection of `(start, end)` pairs. Return `True` only when AC1–AC4 all hold,
`False` otherwise, and never alter `existing`.

## 2. The working process

| Stage | You do | The AI does | Evidence | Where |
| --- | --- | --- | --- | --- |
| 0. Before AI | Scope, criteria, failure points, contract, assumptions — **in your own words** | — | first commit, pushed | §2 |
| A. Plan | Approve the plan yourself | Proposes checks, assumptions, boundary tests | exchange | §11 |
| B. Generate | Save Python v1 and web v1 **before fixing anything** | Writes `can_book`; Bolt builds the page | `code/original/`, `web/original/`, exchanges | §3, §4, §11 |
| — Test | Run T1–T12 on **both** v1s and both finals | — | test table, suite output | §5, §6, §12 |
| C. Critique | Verify every claim independently | Reviews against AC1–AC6 | exchange, decisions | §8, §11 |
| D. Repair | Small, targeted prompts; record exactly what changed | Applies them | issue log, before/after, exchange | §7, §11 |
| E. Verify | Rerun the complete case set; state what remains | — | final columns, limitations | §5, §13 |
| Write | Agent analysis, reflection | — | | §9, §10 |

**At least four exchanges** saved in section 11, with the exact prompts and complete responses —
at least one each for Plan, Generate, Critique and Repair.

**Commit as you go — three commits minimum; this is the order we expect to see:**

```
git commit -m "sis-03: baseline in my own words, before any new AI exchange"
git commit -m "sis-03: v1 of the function and of the page, as generated"
git commit -m "sis-03: tests, cleanup, final versions and report"
git commit -m "sis-03: declaration"
```

## 3. Reusing Practice #05 and #06

If you reuse, copy these **unchanged** — they are your v1s, and v1 must be the AI's output:

| From | To |
| --- | --- |
| `week-05/code/original/booking_v1.py` (your language's v1 on Path B) | `sis-03/code/original/` |
| `week-06/original/` — the whole folder | `sis-03/web/original/` |
| `week-06/evidence/v1.png` | `sis-03/evidence/web-v1.png` |
| the plan and generate exchanges from your Week 05 / 06 lab reports | `report.md` §11, with **Source:** week-05 / week-06 and their original dates |

You may also start `code/booking.py` and `code/test_booking.py` from your Week 05 finals and
`web/final/` from your Week 06 final — then keep improving them here. Record the choice in report
§1 (`Python v1 from`, `Web v1 from`) and in `submission.yml` (`reuse:`).

**Not reusable:** section 2 (the baseline is new and comes first), the twelve-case table (T7–T12
are new, and both artifacts are tested in one table), sections 6–10, and the Critique and Repair
exchanges, which happen in this assignment.

Your Week 06 Bolt prompt forbade "authentication, backend services" in the practice's own words;
the checker accepts that sentence for X4. A fresh prompt must forbid **login, backend and
database** explicitly.

## 4. Task 1 — baseline and plan → `report.md` §2

Before any new AI exchange of this assignment, fill section 2 **yourself**: the scope in your own
words (15 words or more), AC1–AC6 rephrased, **at least two likely failure points** (the brief's
examples: endpoint overlap and starts-now), the contract row by row, at least two initial
assumptions, and what you will verify by hand. **Commit and push.** That commit is your evidence
that the baseline was yours.

## 5. Task 2 — the function, AI-assisted → `code/`, `report.md` §3

1. Ask your assistant for a short **plan** — checks, assumptions, boundary tests — and approve it
   yourself (stage A). Then have it generate `can_book` using **only the standard library**.
2. **Save the first generated implementation as `code/original/booking_v1.py` before fixing any
   error.** Its exchange goes in §11 with **Stage:** Generate, and v1 must appear in that response
   exactly as you saved it (X5).
3. **Review every conditional branch** of v1 in section 3: quote the condition, name its AC, say
   whether it satisfies it and why. AC1–AC4 must all appear.
4. Your final `code/booking.py` keeps the signature and adds nothing beyond the contract.
5. **Tests — `code/test_booking.py`, 10 or more**, green on your final: the six cases from the
   brief (T1–T6 in §7) **plus** reversed times, the day bounds (ending at 1440 and after it),
   multiple bookings, and unchanged inputs. Expected values come from AC1–AC5, never from what the
   code returns.

**Path B — any other language.** Use the Week 05 substitution table: the same name `can_book`,
the same five parameters in this order, standard library only, your language's Boolean.

| Your language | `existing` becomes | Files in `code/` | Run your tests with |
| --- | --- | --- | --- |
| JavaScript / TypeScript | array of `[start, end]` pairs | `booking.js`, `booking.test.js` | `node --test` |
| Java | `List<int[]>` | `Booking.java`, `BookingTest.java` | JUnit, or a `main` that asserts |
| C# | `List<(int, int)>` | `Booking.cs`, `BookingTests.cs` | `dotnet test` |
| Go | `[][2]int` | `booking.go`, `booking_test.go` | `go test -v` |
| C++ | vector of pairs | `booking.cpp`, `test_booking.cpp` | a `main` that asserts, or Catch2 |

Leave the starter `booking.py` untouched on Path B — that is how the checker knows. You then
**plant three faults yourself** (§12.2): break one line, name the AC, name the test that failed,
restore it.

## 6. Task 3 — the prototype v1 in Bolt.new → `web/original/`, `report.md` §4

1. Prompt Bolt.new to build the one-page **Smart Campus Room Availability Checker**. Include
   AC1–AC6 and **explicitly forbid login, backend and database**. Paste the exact prompt under
   **Prompt as sent:** in section 4 (X4).
2. Save the first usable preview as `evidence/web-v1.png`, and Bolt's download of the project,
   unzipped, in `web/original/` (`package.json` or `index.html` inside; one folder deeper is fine).
   Record the model if Bolt shows it.
3. In section 4, name **at least two** main generated files or components by their path inside
   `web/original/` (for example `src/App.tsx`) and their role (G1), and say what v1 does.

**Do not treat v1 as the final submission.** `web/final/` must differ from it (W5).

## 7. Task 4 — execute the test cases → `report.md` §5, §6, §12

**One table, both artifacts, twelve cases.** Base data for every case unless the row says
otherwise: `now = 540`, `blocked = False`, `existing = [(600, 660)]`. The first four columns are
filled in for you — do not change them (C1).

| Case | | Input | Expected |
| --- | --- | --- | --- |
| T1 | Touching | 660–720 | Available |
| T2 | Overlap | 630–690 | Unavailable |
| T3 | Blocked | 660–720, blocked | Unavailable |
| T4 | Exactly 120 min | 720–840 | Available |
| T5 | 121 min | 720–841 | Unavailable |
| T6 | Starts now | 540–570 | Unavailable |
| T7 | Reversed | 720–660 | Unavailable |
| T8 | Ends at midnight | 1380–1440 | Available |
| T9 | Past midnight | 1380–1441 | Unavailable |
| T10 | Second booking | 720–780, existing (600–660), (700–760) | Unavailable |
| T11 | Same check twice | 660–720, twice | Available |
| T12 | Narrow screen | T1 at ~375 px wide | Available |

- **Python columns:** `True`, `False` or `Error` (it raised) — what the call **actually returned**,
  for v1 and for your final. T11 is the result of the second call; T12 is `n/a`.
  **On Path A the checker runs both of your files on T1–T11 and compares (C2, C3).** It prints what
  each one returns; that run counts as executing them.
- **Page columns:** `Available`, `Unavailable` or `Not testable` — what the page **actually
  showed**, for v1 and for the final. T8 and T9 may be `Not testable` on the page — a time input
  stops at 23:59 — and C4 accepts that; any other case that is not as expected is a FAIL you
  declare and explain in §13.
- **Never claim a test passed unless it was actually executed.** That sentence is the brief's.

**Section 6 — traceability**, his table: for each of AC1–AC6, the implementation (file, line or
component), the test input (case IDs), the expected result, the v1 actual and the final actual.

**Section 12** holds the complete terminal output of your final suite — Path A: the part of
`python -m unittest -v` ending in `Ran N tests` and `OK` (K1).

## 8. Task 5 — cleanup and retest → `web/final/`, `report.md` §7, `evidence/`

1. Log **at least two concrete findings** from v1 in section 7 — a **functional defect** and a
   **usability or code-quality issue** where you have them. If every case passed on v1, log the
   preventive cleanup you did and why.
2. For each issue: **evidence → focused AI prompt → change → retest.** The reproduction names a
   case or an AC; the priority is High, Medium or Low; the prompt names the behaviour to change.
3. **No generic prompts and no unrequested features.** The checker refuses "make it better",
   "improve the code" and their relatives (I2).

   | Worthless | Worth something |
   | --- | --- |
   | "make it better" | "Choosing 11:00–12:00 and pressing Check twice gives Available, then Unavailable; AC5 says the data stays unchanged. Make the smallest change that fixes this." |

4. **Before/after screenshots** of one meaningful improvement: `evidence/before-1.png` and
   `evidence/after-1.png`, and the line under the table says which issue they show (E2, I2).
5. Download the final project into `web/final/`, take `evidence/final-narrow.png` at phone width in
   portrait (E3), and **run the complete case set again** on both finals.

The final page must stay in scope: no network call, storage, backend, login or analytics in its
source (W3).

## 9. Critique → `report.md` §8

Ask an assistant to **review your function and your page against AC1–AC6** (stage C) — a new chat
is better than the one that wrote the code. Then take its answer claim by claim: how you verified
it (a case, a test, a run), and your decision — accept, reject or modify — with the AC or case
behind it. At least three rows, **at least one rejected or modified** (V2).

**The critique is another claim to evaluate, not a verdict.**

## 10. Task 6 — coding-agent analysis → `report.md` §9

This is Lecture #07 applied to your own work.

- **9.1 — the loop.** One real pass from this assignment, step by step: user goal → model / plan →
  tool call → observation → next step → human review (A1).
- **9.2 — context, tools, permissions.** What your assistant and Bolt.new used or appeared to use.
  The last column says **Observed** (you saw it happen: a file list, a terminal, an install) or
  **Assumed** (you infer it about the internals). Use both (A2). Distinguishing them is the point.
- **9.3 — one safety checkpoint** before executing or accepting AI-generated changes (25 words or
  more), and how this workflow relates to **reliability, security and human responsibility** (40
  words or more) (A3).

## 11. Reflection → `report.md` §10 — 100–200 words, your own words

Compare **AI-assisted coding** (the function) with **vibe coding** (the page) in this assignment;
give one example each of a **reliability**, an **availability/usability** and a **security** risk;
explain why code review, tool permissions and tests remain human responsibilities; name **one AI
recommendation you rejected or modified**, and why; say what you would improve next **without
expanding the scope** (Q1).

**How words are counted:** every whitespace-separated token with a letter or digit in it,
`<!-- comments -->` excluded. The checker prints the count; trust it over your editor.

## 12. Check your work

The checker runs **55 checks on Path A** and **36 on Path B**:

| Checks | What they look at |
| --- | --- |
| **R1–R3, B1** | report.md structure, no template markers, the setup table, your baseline |
| **F1–F10** | Path A: your final `can_book` on fixed inputs for AC1–AC5 |
| **O1, U1–U2** | v1 kept; your suite has 10 tests or more and is green |
| **M1–M10** | Path A: your suite against ten faulty versions of `can_book`, one broken AC each — **PASS** = your tests caught it |
| **P1–P3** | Path B: your implementation, your tests, three planted faults |
| **V1–V2** | v1 reviewed branch by branch; the critique decisions |
| **W1–W5, G1** | the Bolt exports: final and v1 present, clean, in scope, different; generated files named |
| **E1–E3** | the four screenshots |
| **C1–C4** | the twelve cases — and on Path A, whether your Python results are what your files return |
| **TR1, I1–I2** | traceability; the issue log |
| **A1–A3** | the agent analysis |
| **X1–X5** | the exchanges; the Bolt prompt; your v1 inside its Generate response |
| **K1, Q1** | your suite's output; the reflection's word count |

**It checks behaviour and shape, never quality.** 55 PASS means your submission can be graded —
not that your review is good. Your review, decisions and reflection are read by a person.

```
PASS   the check is satisfied
FAIL   it runs, but the result is wrong or the content is not there
ERROR  it could not run: a file, a folder, a section or the function is missing
```

**Path A — Python 3.8 or newer:**

```
cd sis-03
python tests/check_sis.py
```

**No Python on your machine?** On GitHub open your repository → **Code → Codespaces → Create
codespace on sis-03**; the terminal there has Python. Path B students run the checker the same way
— it reads your files and your report, it does not need your language.

The shipped template gives `pass=1 fail=21 error=33` on the first run. That is the intended start.

## 13. The declaration — `submission.yml` (≈ 5 min, last)

Facts only — who you are, the assistant and model, Bolt, your language and path, what you reused,
your checker numbers, your counts, your case results, and the IDs of any check still failing.

```
python tests/check_sis.py             # the final run — copy its three numbers
git add . && git commit -m "sis-03: final versions and report"
git rev-parse --short HEAD            # this hash goes in checker.commit
python tests/validate_submission.py   # then fix anything it flags
git add submission.yml && git commit -m "sis-03: declaration" && git push
```

Two things that decide marks:

- **Your numbers are re-run at the head of your pull request.** We run `check_sis.py` on the
  commit you submit. Numbers that match are settled automatically. Numbers that do not match cost
  the whole workflow criterion — so after your final run, **change nothing** in `report.md`,
  `code/`, `web/` or `evidence/`. If you do, run the checker again and update the declaration.
- **A FAIL you report costs you nothing extra.** If T6 still fails on your final page, list `C4`
  under `known_fails` and explain it in a row of section 13. Hiding it is what costs.

## 14. Submit

```
git checkout main
git pull
git checkout -b sis-03
# unzip SIS_03.zip into the root of your se-practice repository, copy your v1s in (§3), then work and commit
git push -u origin sis-03
```

1. Branch **`sis-03`** off `main`, folder **`sis-03/`** at the top of your `se-practice`
   repository. Never commit to `main`.
2. At least **3 meaningful commits**, authored by your own GitHub account; the first one is your
   baseline (§2 shows the order).
3. Open **one pull request `sis-03 → main`** in your own repository.
   Title: `SIS 03 - Room availability - <Surname Name>`.
   Description: the five-section shape from `SETUP.md` §4 — What I built · AI tools used · What the
   AI got wrong · Time spent · What I would do differently. **All five headings are checked.**
4. **Leave the PR open. Do not merge it.**
5. In the Teams assignment: **+ Add work → Link → paste the pull request URL.**
   It looks like `https://github.com/<you>/se-practice/pull/N`. Not the repository URL.

**Deadline: Sunday 1 November 2026, 23:59 (Almaty).** Lateness is read from GitHub's server-side
push time, not from commit dates. Late work follows the course policy.

## 15. Grading — 2 points, 8 criteria × 0.25

| # | Criterion | Full 0.25 | Half 0.125 | Zero |
| --- | --- | --- | --- | --- |
| 1 | **Baseline & contract** | Scope, AC1–AC6 and the contract in your own words, two real failure points and assumptions — committed before the first new AI exchange | Thin or generic, or a failure point with no way to check it | Missing, or written by the assistant |
| 2 | **Function & tests** | Final `can_book` satisfies AC1–AC5 with the signature unchanged; v1 kept unedited and reviewed branch by branch; 10+ tests covering the six cases and the four further kinds, green; every surviving fault caught or explained | One element missing, or a surviving fault neither caught nor explained | No function, no tests, or v1 missing or edited |
| 3 | **Prototype & cleanup** | Bolt prompt with AC1–AC6 and the exclusions; v1 and final exported; generated files named and explained; final differs, stays in scope and is usable at phone width | One element missing, or out-of-scope code left in the final | No export, or v1 submitted as the final |
| 4 | **Test execution & traceability** | All twelve cases run on both artifacts, v1 and final, with results that are actually observed; traceability for AC1–AC6 complete; real suite output | A column or a traceability row incomplete | Results not executed, or contradicted by your own code |
| 5 | **Issues & critique** | Two or more issues, each evidence → focused prompt → change → retest, with before/after screenshots; three critique claims verified independently, one rejected or modified | Generic reproductions, or claims judged without verification | No issue log, AI advice accepted wholesale, or a defect invented to fill the log |
| 6 | **Coding-agent analysis** | One real pass through the loop; context, tools and permissions with observed and assumed kept apart; a concrete safety checkpoint; dependability argued | Generic, or observed and assumed mixed | Missing, or not about this assignment |
| 7 | **Reflection** | 100–200 words in your own words: the comparison, three risks, human responsibility, one rejected recommendation, a next step within scope | Generic, or a required point missing | Missing, or written by the assistant |
| 8 | **AI evidence & workflow** | Four or more complete exchanges covering Plan, Generate, Critique and Repair with tool, model, date, source; reuse declared; `sis-03` branch, 3+ own commits; open PR in the standard shape; `AI_USAGE.md`; `submission.yml` validating | One element missing | Committed to `main`, PR merged, no disclosure, **or declared checker numbers that don't match the re-run** |

**A FAIL you report and explain costs you nothing; one you hide costs the whole criterion.** The
language and the assistant you chose never affect the mark. Reusing your practice work never
affects the mark either way.

**Not accepted (0 for the SIS):** a file upload or an e-mail instead of a pull-request link · a
report that is not in `sis-03/report.md` · a merged PR, a repository link or a branch with no PR ·
fabricated prompts, responses, results or screenshots.

## 16. FAQ

**Can I e-mail a PDF instead, as the original brief says?** No. In our groups everything is in the
pull request; the only thing you paste into Teams is its link.

**I reused my Week 05 v1. Does section 3 need a new review?** Yes — section 3 is new. If your Week
05 lab report already mapped v1 to the ACs, the same thinking applies; write it in this table.

**I did not do Practice #05 (or #06).** Generate that v1 fresh, declare `fresh`, and save it
before fixing anything. Nothing is graded differently.

**My final Python and v1 give the same results.** Allowed, if v1 was already correct — say so in
section 3. The page is different: the final must differ from v1 (W5).

**T8 and T9 cannot be entered on my page.** Write `Not testable` in the page columns; C4 accepts it
for those two cases. Say in §13 what the page would need.

**The checker says C2: you wrote True, it returns False.** The table must say what your code does,
not what it should do. Copy the result the checker printed for that file — and if it is wrong,
that is a finding for §7.

**My Bolt prompt is from Practice #06 and has no "login" or "database".** The checker accepts the
practice prompt's own sentence ("Do not add authentication, backend services …"). A new prompt must
forbid login, backend and database explicitly.

**My tool does not show the model.** Write `not displayed` in §1, §11 and `submission.yml`.

**Can I delete the `<!-- -->` guidance comments?** Yes. Never delete the numbered headings, the
`### 2.1`–`### 9.3` and `### B1`… sub-headings, or the **Label:** words.
