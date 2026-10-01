# Practice #03 — Requirements Engineering with AI

**AI-Driven Software Engineering · KBTU SITE · Fall 2026**
In class: 50 minutes · At home: about 60 minutes · Worth 1 point (4 × 0.25)

> ### Your assistant is your choice. The notation is not.
>
> Use **any AI assistant you can access** — ChatGPT, Claude, Gemini, Copilot, DeepSeek, anything.
> Record the tool **and the exact model name**; "ChatGPT" is not a model name. Freeze both for the
> whole lab: three prompts answered by three different models is not an experiment.
>
> There is **no programming language this week** — nothing is implemented. What is fixed for
> everyone is the **notation and the file names**: PlantUML for the diagram, the four files under
> `requirements/`, and the `US-nn` / `AC-nn` / `UC-nn` ID scheme. They are fixed because a checker
> reads them, and because your work has to be comparable with everyone else's.
>
> **No Python?** Both checkers are a convenience, not the grade. Section 9 of `lab-report.md` prints
> the same checks as a list you can walk by hand, and you lose nothing for doing it that way.

---

## 1. The scenario — fixed, and the same for everyone

Do not invent a different system, and do not let the assistant widen this one.

**Smart Campus — study room booking.** The KBTU library has a set of small study rooms that can be
reserved by students through a campus web application.

**Actors — exactly two.**

| Actor | Who it is |
| --- | --- |
| **Student** | A registered KBTU student who reserves rooms for individual or group study. |
| **Administrator** | Library staff who keep rooms usable and watch how they are used. |

**What the system does — exactly six functions.**

| ID | Use case | Notes |
| --- | --- | --- |
| UC-01 | View availability | Which rooms are free, and when. |
| UC-02 | Book room | Reserve a free room for a time slot. |
| UC-03 | Cancel booking | Release a reservation the student made. |
| UC-04 | Block or unblock room | Take a room out of service and put it back. |
| UC-05 | Review usage | See how rooms are being used over a period. |
| UC-06 | Send confirmation | The system confirms a booking or a cancellation. |

**Business rules — four, and they are not negotiable.**

- **R1** A booking must start in the future.
- **R2** A booking lasts at most two hours.
- **R3** Two bookings for the same room may not overlap.
- **R4** A blocked room cannot be booked.

**Out of scope — explicitly.** If any of this appears in your stories, the assistant invented it and
your review missed it:

payments, fees, fines or penalties · check-in, attendance or QR codes · equipment, cleaning or
maintenance requests · SMS, push or reminder notifications of any kind beyond UC-06 · account
registration, passwords or authentication · waiting lists and queues · anything about screens,
colours, databases or servers.

**Two things the scenario deliberately does not settle.** Nobody will answer these for you:

1. A booking that **ends exactly when another begins** — is that an overlap under R3?
2. Is **exactly two hours** allowed under R2, or must a booking be shorter than two hours?

Decide both, write the decision into your assumptions, and declare it in `submission.yml`. **Either
answer is accepted. Not deciding is not.**

---

## 2. What you hand in

```
week-03/
├── README.md                        this file — read-only
├── lab-report.md                    the worksheet you fill in (headings must not be deleted)
├── AI_USAGE.md                      AI disclosure — required every week
├── submission.yml                   the declaration — facts only
├── requirements/
│   ├── user-stories.md              6-8 stories, IDs US-01…
│   ├── acceptance-criteria.md       three stories × 3-5 Given/When/Then criteria
│   ├── use-cases.puml               PlantUML source of the diagram
│   └── traceability.md              the table that ties the three together
└── tests/
    ├── check_requirements.py        23 structural checks — do not edit
    └── validate_submission.py       checks your declaration parses — do not edit
```

---

## 3. Part 1 — Generate the user stories (10 min in class)

Open a **fresh chat**. Paste the scenario from section 1 above, then this prompt **exactly as
written** — do not improve it. Improving prompts was Week 02's experiment; this week the generation
is deliberately unremarkable, because the work being graded is the **review**.

```
You are a requirements analyst. For the Smart Campus study room booking system, identify
Student and Administrator goals. Write 6 to 8 user stories using: As a [role], I want [goal],
so that [reason]. Add a priority and one assumption to each story. Stay within the supplied
scenario.
```

Paste the **original, unedited** output into `lab-report.md` section 2 before you touch it. That
copy is the evidence; without it, the review has nothing to be a review of.

## 4. Part 2 — Review the stories (10 min in class)

Go through every story against this list — it is the deck's list, unchanged:

- Does it name a real stakeholder — **Student or Administrator**, not "System" and not "User"?
- Does it describe one valuable outcome?
- Does the reason explain why the outcome matters?
- Can the team test it?
- Is it small enough for one iteration?
- **Did the AI invent something outside the scenario?** Check it against the out-of-scope list.

Keep **6 to 8 revised stories** in `requirements/user-stories.md`, numbered `US-01`, `US-02`, … Each
story keeps its **priority** (High / Medium / Low) and its **one assumption**.

Every story you deleted, merged or rewrote goes in `lab-report.md` section 3 with the reason. This
is the part that scores.

## 5. Part 3 — Acceptance criteria (15 min, in class or at home)

Select **three** of your stories. Fresh chat, verbatim prompt:

```
For each selected story, write 3 to 5 acceptance criteria in Given, When, Then form. Include
successful behavior, validation, and an error or alternative case. Apply these rules: bookings
must be in the future, maximum duration is two hours, rooms cannot overlap, and blocked rooms
cannot be booked. List assumptions before the criteria.
```

Then review each criterion:

- the starting condition is clear;
- one action triggers one observable result, and that result could become a software test;
- terms and business rules stay consistent with section 1;
- **boundary and invalid cases are covered** — a set of three happy paths is not a set of criteria;
- it says nothing about screens, databases or internal classes.

Write the result into `requirements/acceptance-criteria.md`: assumptions first, then the criteria,
IDs `AC-01`, `AC-02`, … and each block naming the `US-nn` it belongs to. **Your assumptions must
settle the two open questions from section 1.**

## 6. Part 4 — The use-case diagram (15 min, at home)

Fresh chat, verbatim prompt:

```
Create PlantUML code for a UML use-case diagram of the Smart Campus study room booking system.
Place Student and Administrator outside the system boundary. Include View availability, Book
room, Cancel booking, Block or unblock room, Review usage, and Send confirmation. Show only
justified actor associations. Use include or extend only when the relationship is clear. Do not
model screens, databases, or internal classes.
```

Review it before it goes in the file:

- both actors sit **outside** the boundary, and there is no third actor;
- every use-case name is a verb plus a business goal;
- **associations match responsibilities** — look hard at who is connected to *Review usage* and to
  *Send confirmation*, and ask yourself whether a person triggers that function at all;
- no screens, no databases, no internal components;
- every element traces back to a revised story.

Save the source as `requirements/use-cases.puml`. Render it (plantuml.com/plantuml or a local
renderer) and put the image or a link in `lab-report.md` section 6.

## 7. Part 5 — Traceability and the checkers (20 min, at home)

Fill `requirements/traceability.md`: one row per use case, listing the `US-nn` stories behind it and
the `AC-nn` criteria that test it.

**Expect gaps.** The six use cases are fixed; your stories are not. A use case with nothing behind
it is a finding, not a failure — write it down rather than inventing a story to paper over it.

Then run both checkers from inside `week-03/`:

```bash
python tests/check_requirements.py       # 23 structural checks over requirements/
python tests/validate_submission.py      # checks your declaration parses
```

Record the three numbers in `lab-report.md` section 9 **and** in `submission.yml`. They check
**shape, never quality**: a clean run is the floor, not the grade, and an all-green submission with
six unreviewed stories scores badly.

---

## 8. The declaration — `submission.yml`

One extra file, this week and every week from now on. It holds the **facts** of your submission: who
you are, which assistant and which exact model, what your checker run returned and at which commit,
your decision on the two open assumptions, your traceability gaps, and three findings. Explanations
stay in `lab-report.md` — nothing is written twice.

Fill it last, once your checker run is final, then validate it.

Two things decide marks:

- **Your checker numbers are re-run.** `check_requirements.py` is run again at the commit you name
  in `checker.commit`. Numbers that do not match what your repository produces cost the whole
  *workflow & disclosure* criterion. **A FAIL you report and explain costs you nothing.**
- **A finding that names no ID is not a finding.** `review_findings` needs three or more lines, each
  pointing at a `US-nn`, `AC-nn` or `UC-nn`. "The AI made mistakes" is rejected by the validator,
  not by me.

---

## 9. Submitting

```bash
git checkout main && git pull
git checkout -b week-03
# work inside week-03/ only
git add week-03
git commit -m "week-03: <what this commit actually does>"
git push -u origin week-03
```

Then open a pull request **`week-03 → main` in your own repository, and leave it open**. Paste the
**PR link** into the Teams assignment. At least **3 meaningful commits**, all authored by your own
GitHub account. Full workflow rules are in `SETUP.md` — they have not changed.

---

## 10. Grading — 1 point, 4 × 0.25

| Criterion | 0.25 | Full credit | Half credit | No credit |
| --- | --- | --- | --- | --- |
| **Generation evidence** | 0.25 | All three prompts used verbatim, all three original outputs pasted in unedited, tool and exact model named | An output is missing or was cleaned up before pasting | No original outputs, or the prompts were rewritten |
| **Review quality** | 0.25 | Every change to the AI's output is recorded with a reason; scope creep caught against the out-of-scope list; at least one wrong association in the diagram identified | Changes recorded but the reasons are generic ("improved it") | The AI's output was kept as it came |
| **Requirements artifacts** | 0.25 | Four files present and consistent: 6–8 stories with priorities and assumptions, three sets of 3–5 Given/When/Then criteria including invalid cases, a valid diagram, a traceability table whose gaps are named | One artifact incomplete or internally inconsistent | Missing artifacts, or IDs that do not resolve |
| **Workflow & disclosure** | 0.25 | `week-03` branch, ≥3 commits authored by you, open PR with the standard description, `AI_USAGE.md` complete, `submission.yml` filled and validating | One element missing, or the declaration is incomplete | Committed to `main`, PR merged, no disclosure, or declared checker numbers that do not match the re-run |

**The line that matters most this week:** *a FAIL you report and explain costs you nothing; one you
hide costs the whole criterion.* The same goes for a gap in the traceability table.

Your assistant, your model and your working style are never part of the mark.

---

## 11. FAQ

**The assistant asked me a clarifying question.** Answer it from section 1 only. If section 1 does
not answer it, it is one of the two open questions — decide it yourself and declare it.

**My diagram has a "System" actor.** Then the assistant put an internal component outside the
boundary. That is one of the findings this lab is looking for.

**Two of the six use cases have no story behind them.** Normal, and expected. Record the gap in
`traceability.md` and in `submission.yml`; do not invent a story to hide it.

**The checker fails on something I disagree with.** Say so in `lab-report.md` section 9 with your
reasoning. A defended disagreement is worth more than a silent edit to make the checker green.

**Do I submit screenshots by email?** No. The Lesson 03 deck says so; it does not apply to our
groups. **The PR link in Teams is the submission** — that is the only channel.
