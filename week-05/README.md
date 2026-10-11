# Week 05 — AI-Assisted Coding: `can_book`

**Course:** AI-Driven Software Engineering (Fall 2026, KBTU SITE)
**Practice work #05** · 1 point · AI-use level: **D (AI-integrated, disclosure required)**

> **Your choice this week: the AI assistant, the model, and the implementation language.** Any
> assistant you can access, any language you can run and explain. All three are frozen for the
> whole lab, and the exact model name is recorded. The class demo and the shipped checker are
> Python, so Python is the *recommended* path — not the required one. You lose no marks for
> choosing otherwise (Path B, §6).
>
> **What stays identical for everyone:** the contract and AC1–AC5 in §3, the name `can_book`, the
> order and names of its five parameters, the prompts in §5 (sent unchanged except for the two
> tokens in §4), and the file layout in §2.

---

## 1. The idea of this lab

In Weeks 03 and 04 you wrote requirements and models for the Smart Campus room-booking system.
This week one of those requirements becomes code: a single function that decides whether a booking
request is allowed. An assistant plans it and writes the first version. **You** read it before you
run it, write the tests, find what is wrong, decide which fixes to accept, and explain the result.

The function is about fifteen lines. An assistant will produce it in ten seconds, and it will look
right. Whether it *is* right is decided at four boundaries — the minute a booking starts, the
minute it ends, exactly two hours, and the end of the day — and by one thing that is easy to miss
entirely: what the function does to the list you hand it.

Your tests are graded the way tests are judged in industry: the checker runs **your** suite against
ten deliberately faulty versions of `can_book`. A fault your tests do not notice is a hole in your
suite, whether or not your own function has it.

**Main message:** generated code is a draft. The specification and your tests decide whether it is
correct — not the assistant's explanation of it.

**Time budget:** ~50 min in class + ~70 min at home.

---

## 2. Deliverables

By the deadline, your branch `week-05` must contain:

```
week-05/
├── README.md                  # this file (read-only)
├── lab-report.md              # THE worksheet — fill in all 10 sections
├── AI_USAGE.md                # AI disclosure (every week)
├── submission.yml             # machine-readable declaration — facts only
├── code/
│   ├── booking.py             # your FINAL can_book          (Path B: booking.<ext>)
│   ├── test_booking.py        # your tests, 11 or more        (Path B: your language's test file)
│   └── original/
│       └── booking_v1.py      # the assistant's FIRST version, exactly as returned
└── tests/
    ├── check_booking.py       # provided checker — do not edit
    └── validate_submission.py # provided validator for submission.yml — do not edit
```

---

## 3. The task

Everything in this block comes from the Lesson 05 practice deck, unchanged. **Paste the whole
block as the first message of your chat** (Part 0).

```text
Scenario: Smart Campus study room booking.
User story: As a student, I want to check a room's availability so that I can choose a valid booking time.
Feature: implement can_book(...) for one selected room. Return a decision. The complete system handles saving and confirmation.

Function contract
can_book(start, end, now, blocked, existing)
- Times are integer minutes after midnight on one date. Example: 600 means 10:00.
- now is valid (0-1439). blocked is a Boolean.
- existing contains valid (start, end) tuples for this room's active bookings only.
- Return True or False. Keep all inputs unchanged.

Acceptance criteria
AC1: 0 <= start < end <= 1440, and start > now.
AC2: Duration is at most 120 minutes.
AC3: The room is not blocked.
AC4: No overlap with an existing booking. Touching endpoints are allowed.
AC5: Return True only when AC1-AC4 hold. Return False otherwise and never alter existing.

Intervals include the start and exclude the end.
```

**Overlap, by example.** Existing booking `(600, 660)`, meaning 10:00–11:00:

| New interval | Relationship | Overlap? |
| --- | --- | --- |
| `(630, 690)` | Partial overlap | Yes |
| `(615, 645)` | Inside the existing booking | Yes |
| `(570, 690)` | Contains the existing booking | Yes |
| `(660, 720)` | Starts at the existing end | No |

**Two questions you left open are now answered.** In Weeks 03 and 04 the scenario did not say
whether touching bookings overlap, or whether exactly two hours is allowed; you had to declare an
assumption. AC4 and AC2 settle both: touching is allowed, and 120 minutes is allowed. If your
Week 04 model said otherwise, that is a finding for `lab-report.md` §1 — not a penalty.

**One question is still open**, and it is this week's: the contract says times are integers and
does not say what happens when one is not. You decide, and you declare it (§9.2 of the worksheet).

---

## 4. Your language

The contract is written in neutral words on purpose: integers, a Boolean, a collection of pairs.
Two tokens in the prompts change with your language, and **nothing else does**:

| Token in the prompt | Replace with |
| --- | --- |
| `Python 3` | your language and version |
| `booking.py` | your file name from the table below |

| Your language | The signature to ask for | `existing` becomes | Files in `code/` | Run your tests with |
| --- | --- | --- | --- | --- |
| Python | `def can_book(start, end, now, blocked, existing)` | list of `(start, end)` tuples | `booking.py`, `test_booking.py` | `python -m unittest -v` |
| JavaScript / TypeScript | `function can_book(start, end, now, blocked, existing)` | array of `[start, end]` pairs | `booking.js`, `booking.test.js` (`.ts`) | `node --test` |
| Java | `static boolean can_book(int start, int end, int now, boolean blocked, List<int[]> existing)` in class `Booking` | `List<int[]>` | `Booking.java`, `BookingTest.java` | JUnit, or a `main` that asserts |
| C# | `static bool can_book(int start, int end, int now, bool blocked, List<(int start, int end)> existing)` | `List<(int, int)>` | `Booking.cs`, `BookingTests.cs` | `dotnet test` |
| Go | `func can_book(start, end, now int, blocked bool, existing [][2]int) bool` | `[][2]int` | `booking.go`, `booking_test.go` | `go test -v` |
| C++ | `bool can_book(int start, int end, int now, bool blocked, const std::vector<std::pair<int,int>>& existing)` | vector of pairs | `booking.cpp`, `test_booking.cpp` | a `main` that asserts, or Catch2 |

**What is not substituted, in any language:**

- The name **`can_book`** and the five parameter names in this order, even where your language's
  convention would write `canBook`. Otherwise "the signature changed" means different things for
  different students.
- **Standard library only** for the function. A test framework for your tests is fine.
- The result is your language's Boolean — not `1`/`0`, not a string, not `null`.

**Static typing.** In Java, C#, Go and C++ the compiler already refuses `600.5` or `"600"` as a
time, and `const&` in C++ makes "never alter existing" a compile-time guarantee. That is a real
finding, not a loophole: declare `refused-by-compiler` in `submission.yml` and say in §9.2 what the
compiler gave you that a Python student had to test for.

---

## 5. The lab

### Part 0 — Setup (~4 min, in class)

1. `git checkout main && git pull && git checkout -b week-05` (full steps in `SETUP.md`).
2. Unzip `Week_05.zip` into the root of your repository so that `week-05/` sits next to `week-04/`.
3. Fill in `lab-report.md` §1. Commit: `week-05: setup`.
4. Open **one new chat** in your assistant. Send the block from §3 as the first message, followed
   by this line:

```text
This is the scenario, the function contract and the acceptance criteria. Use only these. Wait for my first request.
```

Tasks 1–5 all happen in this one chat.

### Part 1 — Task 1: plan the feature (~7 min in class)

Send this prompt **unchanged** (apart from the token in §4):

```text
Propose a short implementation plan for can_book. List the checks in order and identify assumptions. Use Python 3 and the supplied rules. Do not write code yet. Suggest boundary cases that could expose an incorrect implementation.
```

1. Paste the plan, unedited, into `lab-report.md` §2.
2. Read every step against the contract and AC1–AC5. For each step ask: **which line of the
   specification asks for this?** A step with no answer is an invented rule.
3. Record every invented or changed rule in the §2 table — and tell the assistant to drop it.
   Typical inventions: a gap between bookings, validation of things the contract already
   guarantees, sorting or storing the bookings.
4. Commit: `week-05: plan reviewed`.

### Part 2 — Task 2: implement with AI (~7 min in class)

Send **unchanged** (apart from the two tokens in §4):

```text
Implement can_book in booking.py using the supplied contract and AC1-AC5. Keep the signature. Use only the standard library. Do not modify existing. Return the function and explain each condition. Keep the feature within the stated scope.
```

1. Save the function **exactly as returned** to `code/original/booking_v1.py`. Do not fix a typo.
   Do not reformat. This file is the evidence of what the assistant actually produced.
2. Copy it to `code/booking.py`. This is the copy you will work on.
3. **Read it before you run it.** Fill in the AC map in `lab-report.md` §3: one row per condition,
   the line quoted, the AC it implements, and whether it is correct *as written*. Write down what
   you expect to fail — you will find out in Part 3 whether you were right.
4. Commit: `week-05: v1 as returned by the assistant`.

### Part 3 — Task 3: test the feature (~12 min in class, finish at home ~25 min)

Base input for every case: `now=540, blocked=False, existing=[(600, 660)]`.

| Case | Change or request (start, end) | Expected |
| --- | --- | --- |
| Touching | `(660, 720)` | True |
| Overlap | `(630, 690)` | False |
| Blocked | `(660, 720)`, `blocked=True` | False |
| Exactly 2 hours | `(720, 840)` | True |
| Over 2 hours | `(720, 841)` | False |
| Starts now | `(540, 570)` | False |

`code/test_booking.py` already holds the first of them:

```python
import unittest
from booking import can_book


class BookingTests(unittest.TestCase):
    def test_touching_end_is_allowed(self):
        result = can_book(660, 720, 540, False, [(600, 660)])
        self.assertIs(result, True)
```

1. Add the other five table cases. Run, from inside `code/`:

```text
python -m unittest -v
```

2. Add tests for the five further kinds the task names — **at least one each, 11 tests or more in
   total**:
   - zero-length and reversed times
   - the day bounds
   - an empty `existing`, and an `existing` with several bookings
   - unchanged input
   - the other overlap relationships in the table in §3
3. **The expected value of every test comes from AC1–AC5, never from running the code.** A test
   whose expected value was copied from the function's output can only agree with the function.
4. **One rule per test.** A request of `(1400, 1600)` is rejected — but by which rule? If two rules
   reject the same input, the test passes even when one of them is missing. Choose inputs that only
   one rule can reject.
5. List every test in `lab-report.md` §4, with its result on v1 and on your final version.
6. From inside `week-05/`, run the checker and read the M lines (§6):

```text
python tests/check_booking.py
```

7. Commit after the table cases, and again after the further kinds:
   `week-05: tests for the six table cases`, `week-05: boundary and input tests`.

### Part 4 — Task 4: debug with evidence (~15 min, at home)

For each failing test or failing F check:

1. Write the evidence row in `lab-report.md` §5 **first**: the full call, the expected result,
   the actual result. No evidence, no fix.
2. Find the line yourself. If you want the assistant's help, send **unchanged**, with the words
   `True` and `False` set to your case:

```text
The expected result is True, but I get False. Here are my code and failing test. Explain the cause and propose the smallest fix without changing the contract.
```

3. Before you accept a fix, check it against the overlap table in §3 by hand. The slide example of
   a faulty check is `if start <= b and end >= a: return False` — work out, on paper, what it does
   to `(660, 720)` against `(600, 660)`.
4. Apply the smallest change to `code/booking.py`, re-run the **whole** suite, commit:
   `week-05: fix <what>`.

**If v1 passes all your tests and every F check:** add a new edge case, and record it in §5 with
expected and actual equal. Then justify in §7 why no change was needed. Report only what you
actually observed — a clean v1 honestly reported scores exactly as well as a broken one honestly
fixed.

### Part 5 — Task 5: review and refine (~15 min, at home)

1. Check, by reading: every condition maps to an AC; every existing booking is examined before
   `True` is returned; the result is a Boolean; the input list is untouched.
2. Ask for a focused critique. This prompt is **ours** (the deck asks for the critique without
   wording it); send it unchanged with your final code pasted below it:

```text
Review this implementation of can_book against the contract and AC1-AC5 only. List at most five concrete issues. For each one, quote the line and name the acceptance criterion or contract line it concerns. Do not rewrite the function.
```

3. Paste the critique into `lab-report.md` §6 and judge **every** point: accept or reject, with
   the AC or contract line that justifies it. "Add input validation" and "raise an exception" are
   suggestions you will probably receive. Read AC5 before you accept either.
4. Re-run the full suite after each accepted change. Fill in the change log, §7.
5. Commit: `week-05: critique handled`.

### Part 6 — Report, declaration, submit (~15 min, at home)

1. Answer §9.2 and §9.3 and write the conclusion, §10 (120–180 words).
2. Paste your suite's final output into §8.1. Run the checker and paste its output into §8.2 —
   **last**. If you edit the report afterwards, run and paste again.
3. Fill in `AI_USAGE.md`.
4. Commit everything, then note the hash: `git rev-parse --short HEAD`.
5. Fill in `submission.yml` (§7 below), run the validator, commit, push, open the PR (§8).

**Optional extension — earns nothing extra.** Return a rejection reason as well as the decision.
Define the new contract first, update its tests first, and put all of it in `code/extension/` so
that `code/booking.py` keeps the contract in §3.

---

## 6. Checking your work

### Verdicts

```
PASS   the check found what it was looking for
FAIL   it runs, but the result is wrong or the content is not there
ERROR  it could not run: a file or the function is missing, the signature is wrong,
       or nothing is implemented yet
```

### Path A — you are using Python

From inside `week-05/`:

```text
python tests/check_booking.py
```

It runs 32 checks:

| Checks | What they look at |
| --- | --- |
| **F1–F10** | Your final `can_book`, called on fixed inputs for AC1–AC5. A FAIL prints the exact call, what came back and what was expected — that line is ready-made evidence for §5. |
| **O1** | `code/original/booking_v1.py` exists. The checker also runs v1 through F1–F10 and prints the result under the table, so you can fill in §4 and §7. |
| **S1–S2** | Your suite has 11 tests or more, and is green on your own code. |
| **M1–M10** | Your suite is run against ten faulty versions of `can_book`, each breaking exactly one AC. **PASS** = at least one of your tests failed on it. **FAIL** = it passed all your tests. |
| **L1–L9** | `lab-report.md` has its sections filled in. |

The M lines tell you **which** acceptance criterion the surviving fault breaks, never **how**.
That is deliberate: you derive the missing test from the AC, not from reading the fault. When a
fault survives, ask: *if this AC were implemented one step wrong, which of my tests would notice?*
On your first run with only the table cases, expect several to survive.

The M checks are not judged until S2 passes — a suite that is red on your own code catches
everything and proves nothing. **Only tests that follow the contract count.** Each of your tests is
also run on a `can_book` that implements AC1–AC5 exactly; a test that fails there — one about what
the contract leaves open, like a non-integer time, or one whose expected value contradicts an AC —
cannot catch a fault, and the checker lists it under the table. Keep your non-integer test: it
documents your §9.2 decision. It just does not count towards M.

The first run on the untouched folder gives `0 PASS · 10 FAIL · 22 ERROR`. That is the intended
start.

### Path B — any other language

The checker cannot call a function written in another language, so it runs 13 checks instead:
P1 (your implementation is in `code/`), P2 (your test file is in `code/`), O1 (v1 is kept in
`code/original/`), P3 and L1–L9. Delete `code/test_booking.py`; leave `code/booking.py` as the
untouched starter or delete it. Then, in place of F, S and M:

1. Your suite covers the six table cases and the five further kinds from Part 3, and you paste its
   **real terminal output** into §8.1. A screenshot of an IDE is not accepted.
2. **You plant three faults yourself** (§8.3). Change one line of your own `can_book` so that it
   breaks one AC, run your suite, record which test failed, restore the line. Three different ACs.
   If a planted fault passes all your tests, you have found a hole — add the test, and say so.
3. Compare Booleans as Booleans. A test that compares `"true"` with `"true"` as strings will pass
   for the wrong reason.

Python still runs the checker and the validator on your folder — both work on a Path B folder.
If you cannot run Python at all, fill in `submission.yml` by hand, leave the three checker numbers
empty, and say so in §9.1. The grader runs the checker for you, and it costs you nothing.

---

## 7. The declaration — `submission.yml`

Facts only. From inside `week-05/`:

```text
python tests/validate_submission.py
```

Three things decide marks:

- **`checker.commit` is the commit you ran the checker at** — normally the one just before the
  commit that adds the declaration. That one-commit gap is expected. It must be a commit on your
  `week-05` branch: a hash that is not on the branch costs marks.
- **Your numbers are re-run at the last commit of your pull request.** We run `check_booking.py`
  there ourselves. Numbers that match are settled automatically. Numbers that do not match cost the
  whole *evidence and honesty* criterion — so if you change anything after your last checker run,
  run it again and update `submission.yml`.
- **A FAIL you report costs you nothing extra.** If M9 survives and you could not find the test,
  list `M9` in `known_fails` and say in §9.1 what you tried. Hiding it is what costs.

---

## 8. Submit

1. Push the branch: `git push -u origin week-05`.
2. Pull Request `week-05 → main` in your own repository. Title: `Week 05 — AI-Assisted Coding`.
   Description in the fixed shape from `SETUP.md` §4.
3. **Leave the PR open — do not merge it.**
4. In the Teams assignment: **+ Add work → Link → paste the pull request URL.**

The practice deck asks you to email screenshots at the end of class. **That does not apply to our
groups** — the PR link in Teams is the only submission, and it contains everything the email would
have: your name, tool and model, both files, the test run, the prompts, the original output, the
final code and the change log.

**Deadline:** before the start of the next practice session. Late submissions per the course
policy; the Teams assignment closes at the end of the following week.

---

## 9. Grading — 1 point, 4 × 0.25

| Criterion | 0.25 when … |
| --- | --- |
| **Code** | Final `can_book` satisfies AC1–AC5 (F1–F10) with the signature unchanged and nothing added beyond the contract; the assistant's v1 is kept unedited in `code/original/`. |
| **Tests** | 11 or more tests of your own, green on your code, covering the six table cases and the five further kinds; expected values traceable to an AC in §4; every fault that survives (M) is either fixed with a new test or explained in §9.1. |
| **Review and debugging** | §2 names what the plan invented; §3 maps v1 to the ACs before running it; §5 has input / expected / actual for every defect; §6 judges every critique point with a reason; §7 logs every change. |
| **Evidence and honesty** | §8 has complete, real output; §9.2, §9.3 and the conclusion are your own; `AI_USAGE.md` complete; `submission.yml` passes the validator and its numbers match the re-run; PR open with 3 or more meaningful commits. |

**A FAIL you report and explain costs you nothing. One you hide costs the whole criterion.**

**Your language is never part of the mark.** A careful Go submission and a careful Python one
score identically; a sloppy Python one does not score better for being Python.

**Not accepted:** `code/original/` edited, empty, or written after the fact · tests whose expected
values contradict AC1–AC5 so that they agree with a faulty function · checker or suite output that
was edited, shortened or does not match your files · a changed signature or a renamed `can_book` ·
placeholder rows left in the worksheet · findings that name no line, no test and no AC ("the AI
made a mistake and I fixed it") · a merged PR, a repo link, or an emailed submission.

---

## 10. FAQ

**My v1 passed everything. Did I do something wrong?** No. Record that honestly (Part 4), add an
edge case, and justify the empty change log. Your tests are still judged by the M checks, and a
correct v1 says nothing about them.

**May the assistant write my tests?** Yes — Level D — and you disclose it in `AI_USAGE.md`. But
check every expected value against the AC yourself. In Week 02 you saw generated tests agree with
generated bugs; the M checks are where that shows up this week.

**A fault survives and I cannot work out what it is.** Re-read the AC it names, word by word, and
the list of five further kinds in Part 3. Then look at your test data, not your assertions: is
there an input that *only* that rule decides? If you still cannot find it, report the ID in
`known_fails` and describe what you tried. That costs nothing.

**Can I use pytest?** Your suite must run with `python -m unittest`, because that is how the
checker runs it. `unittest.TestCase` classes are discovered; bare `test_` functions are not.

**The checker says F9 or F10 fails but all my tests pass.** Then your tests do not test that.
F9 is about the *type* of the result; F10 is about the list after the call.

**Where does the grader run my code?** In a container with **Python 3.13**, no network, 512 MB of
memory and only your `week-05/` folder. Write code and tests that run on Python 3.13 with the
standard library: a test that needs the internet, a file outside `code/`, or a feature newer than
3.13 passes on your machine and errors in the grader. Path B is unaffected — your pasted output is
the evidence.

**I edited the report after pasting the checker output.** Run it again, paste again, and update
`submission.yml`. The declared numbers have to match the final state of the branch.
