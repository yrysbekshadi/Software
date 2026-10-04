# Week 04 — Modeling the System with UML

**Course:** AI-Driven Software Engineering (Fall 2026, KBTU SITE)
**Practice work #04** · 1 point · AI-use level: **D (AI-integrated, disclosure required)**

> **Your choice this week: the AI assistant and the model — nothing else.** Any assistant you can
> access (Claude, ChatGPT, Gemini, DeepSeek, Grok, …), frozen for the whole lab, with the exact
> model name recorded. There is no implementation language: the notation is **PlantUML** for
> everyone, because the checker reads it and because everyone's diagrams have to be comparable.
> Python runs the two checkers — on your machine (Path A) or in a GitHub Codespace in the browser
> (Path B). Both are equal; see Part 5.
>
> **What stays identical for everyone:** the scenario and rules R1–R4, the four prompts below
> (sent unchanged), the file names, and the PlantUML conventions in §4.

---

## 1. The idea of this lab

Last week you turned a scenario into user stories, acceptance criteria and a use-case diagram.
This week you model the **same Smart Campus system** from four angles — who needs what (use case),
what exists (class), and how one request flows (sequence **or** activity) — with an AI drafting
every diagram and **you reviewing, correcting and defending** every element.

The drafting is fast. The review is the lab. An assistant will happily draw a confirmation as
something a student "does", a service class in a domain model, and a booking that is saved before
anything is validated. Your job is to find those, cite the rule that proves each one is wrong, and
fix it — and then to check the AI's critique of your work instead of believing it.

**Main message:** a diagram is a claim about the system. If you cannot say which rule or story each
element comes from, it is decoration.

**Time budget:** ~50 min in class + ~60 min at home.

---

## 2. Deliverables

By the deadline, your branch `week-04` must contain:

```
week-04/
├── README.md                 # this file (read-only)
├── lab-report.md             # THE worksheet — fill in all 10 sections
├── AI_USAGE.md               # AI disclosure (every week)
├── submission.yml            # machine-readable declaration — facts only
├── models/
│   ├── approved-stories.md   # your reviewed week-03 stories, or the reference set
│   ├── use-case.puml         # Task 1 — your REVISED use-case diagram
│   ├── class.puml            # Task 2 — your revised class diagram
│   ├── sequence.puml         # Task 3A — OR —
│   ├── activity.puml         # Task 3B  (both = optional extension)
│   ├── original/             # the AI's FIRST output for each diagram, unedited, same file names
│   └── img/                  # a rendered .png or .svg of each revised diagram, same stem
└── tests/
    ├── check_models.py       # provided checker — do not edit
    └── validate_submission.py # provided validator for submission.yml — do not edit
```

---

## 3. The scenario and the stories

The scenario, rules R1–R4 and the reference story set are in **`models/approved-stories.md`**.

- **If you completed Week 03:** replace the reference set with your own stories from
  `week-03/requirements/user-stories.md`, **as revised after your Week 03 review**, keeping their
  IDs. Those are your "approved stories".
- **If you did not, or your set failed review:** keep the reference set (US-01 … US-06) and say so
  in `lab-report.md` §1.

Two things carried over from Week 03 are still undecided by the scenario, and you will meet both:

- **Touching bookings.** Do 10:00–12:00 and 12:00–13:00 overlap under R2?
- **Blocking a booked room.** R3 stops *new* bookings. What happens to the existing ones?

Neither is tested. Both must be **declared** as assumptions (§4.3 of the worksheet) the moment a
diagram depends on them. Note that R1 now settles the other Week 03 question: *at most* 2 hours,
so exactly 2 hours is allowed.

---

## 4. PlantUML conventions (everyone, every diagram)

Render with the PlantUML web server (`https://www.plantuml.com/plantuml`), or an IDE extension if you
already have one working. Export each revised diagram to `models/img/<same-name>.png` (or `.svg`).

| Rule | Why |
| --- | --- |
| File names exactly as in §2. | The checker and the grader open them by name. |
| Every `<<include>>`, `<<extend>>`, inheritance (`<\|--`), composition (`*--`) or aggregation (`o--`) has a comment **on the line directly above** it: `' why: <reason>` | The prompts say "only with a clear reason". This is where the reason lives. |
| Sequence guards **without** square brackets: `alt created` … `else unavailable` … `end` | PlantUML adds the brackets itself; typed brackets are read as a hyperlink and eat a word. |
| Activity guards **with** brackets inside parentheses: `if (Room blocked? (R3)) then ([no])` … `else ([yes])` | Every branch must be labelled. |
| R2 goes in a `note` on `Booking` in the class diagram. | Multiplicity cannot say "no overlap". |
| Use only the fictional scenario. No real names, no real rooms. | Slide 8. |

---

## 5. The lab

### Part 0 — Setup (~4 min, in class)

1. `git checkout main && git pull && git checkout -b week-04` (full steps in `SETUP.md`).
2. Copy this `week-04/` folder into your repository.
3. Fill in `models/approved-stories.md` (§3 above). Commit: `week-04: approved stories`.
4. Open **one new chat** in your assistant. Send, as the first message, the whole of
   `models/approved-stories.md` and this line:

```text
This is the Smart Campus scenario, its rules R1-R4 and my approved user stories. I will ask you for several UML diagrams in PlantUML. Use only this scenario. Wait for my first request.
```

Tasks 1–3 all happen in this one chat, so names stay consistent across diagrams.

### Part 1 — Task 1: use-case diagram (~7 min in class, finish at home)

Send this prompt **unchanged**:

```text
Using the supplied scenario and approved stories, generate PlantUML for a use-case diagram. Include Student and Administrator outside a named system boundary. Model their goals, show justified associations, and list assumptions. Use include or extend only with a clear reason.
```

1. Save the AI's PlantUML **exactly as returned** to `models/original/use-case.puml`. Render it.
2. Review it against the scenario. Ask, for every element:
   - Is each actor linked only to goals the scenario gives that actor?
   - Does each use case trace to a story? Which one?
   - Is it a user goal, or a screen, a component or a system action?
   - Is every include/extend justified — and is the reason written down?
3. Write at least **two findings** in `lab-report.md` §3.
4. Write your corrected version to `models/use-case.puml`. Render it to `models/img/use-case.png`.
5. Commit: `week-04: use-case diagram - original and revised`.

### Part 2 — Task 2: class diagram (~8 min in class, finish at home)

Send **unchanged**:

```text
Create a UML domain class diagram in PlantUML for Smart Campus. Start with Student, Room, and Booking. Add attributes, appropriate operations, and association multiplicities. Add other classes only when requirements justify them. Explain each relationship and list assumptions. Avoid unjustified inheritance or composition.
```

1. Save to `models/original/class.puml`, render, review:
   - Classes are domain concepts — not screens, services, repositories or actions.
   - Attributes are the state R1–R3 actually need (a start, an end or duration, a status, a
     blocked flag).
   - **Read every association in both directions.** "One student makes 0..* bookings; each booking
     belongs to exactly 1 student." If a sentence sounds wrong, the multiplicity is wrong.
   - Inheritance only for a genuine "is a". Composition only if the part cannot exist without
     the whole — and then say why.
   - R2 cannot be drawn with multiplicities: it goes in a note.
2. Fill in §4.1 (each association read both ways), §4.2, §4.3 (assumptions) and §4.4.
3. Write `models/class.puml`, render to `models/img/class.png`. Commit.

### Part 3 — Task 3: ONE behaviour diagram (~8 min in class, finish at home)

Choose **3A** or **3B**. Doing both is the optional extension; it earns nothing extra.

**3A — Sequence** (interactions over time). Send **unchanged**:

```text
Generate PlantUML for Book room. Use Student, BookingService, and BookingRepository lifelines. Validate the supplied rules, then attempt the reservation. Show a successful confirmation and an unavailable-room alternative using alt. Label messages and replies. Explain new design components and all assumptions.
```

Review: every message has a sender, a receiver and a label · validation comes **before** anything
is created · a failure branch saves nothing · every `alt` branch has a guard · where are R1 and R3
checked — visibly, as a message, a guard or a note? · `BookingService` and `BookingRepository` are
design components, not domain classes: name them in §5 and say what each does.

**3B — Activity** (the workflow). Send **unchanged**:

```text
Generate a UML activity diagram in PlantUML for Book room. Show the initial node, actions, guarded decisions, and final nodes. Check the time range, blocked-room status, and overlapping bookings. Show confirmation after success and rejection after failure. Use branches rather than parallel paths unless concurrency is required.
```

Review: initial and final nodes · **three** decisions, one per rule (R1, R3, R2) — one combined
"all pass?" diamond cannot tell the student *why* they were rejected · every branch labelled ·
no `fork` — the checks are sequential · the booking is created only after the last check ·
confirmation on success, rejection on every failure path.

Save the original to `models/original/`, the revision to `models/`, the render to `models/img/`,
fill in §5, commit.

> A focused correction prompt ("the Booking end of Room–Booking should be 0..*, fix only that") is
> allowed. Paste it in §2.4 and log the change in §8 as usual. Rewriting by hand is equally fine.

### Part 4 — AI critique and consistency (~10 min, at home)

1. Open a **new chat** — a critique in the same chat tends to defend its own drafts. Paste
   `models/approved-stories.md` and your three **revised** `.puml` files, then send **unchanged**:

```text
Compare my diagrams with the requirements. Identify missing rules, inconsistent names, and unjustified elements. Cite each issue and propose a specific correction.
```

2. Record at least **three** issues in §6 with your verdict. The critique is a claim, not a
   verdict: **reject** what is wrong and say why. If you accept everything, say what you checked.
3. Fill in §7: one row per rule R1–R4 and one per use case, tracing each into the classes and
   the behaviour diagram. Fill in §8, the change log.

### Part 5 — Check, disclose, submit (~10 min, at home)

Two equal ways to run the checker. Neither costs you anything.

**Path A — Python on your own machine (3.8+, nothing to install):**

```text
cd week-04
python tests/check_models.py
```

**Path B — no Python on your machine:** open your repository in a **GitHub Codespace** (on
GitHub: Code → Codespaces → Create codespace on `week-04`). It runs in the browser, has Python
preinstalled and is free for students. Run the same two commands in its terminal. Commit and push
from there, or pull the result back to your machine.

A hand-marked checklist is **not** a checking path this week: your checker numbers are re-run
automatically and compared with what you declare, so they have to come from a real run.

**How many checks you see depends on what you submitted** — the checker only runs the checks for
diagrams that exist:

| Your folder | Checks |
| --- | --- |
| Untouched, or no behaviour diagram yet | 30 |
| Activity diagram | 35 |
| Sequence diagram | 37 (36 while `class.puml` is missing — CS4 needs it) |
| Both (the optional extension) | 43 |

A classmate with a different total has not found a check you lost. `validate_submission.py` learns
the total by running the checker, so the arithmetic in `submission.yml` can never fail on it.

The checker checks **shape, never quality**: it confirms files, required elements, the conventions
in §4 and that the worksheet is filled. A diagram can pass all of it and still be wrong. Paste the
full output in §9 and explain every FAIL you keep — some are legitimate (a composition you defend,
a use case you deliberately kept).

Then fill in `AI_USAGE.md` and **commit**. Now fill in `submission.yml` — last, once your checker
run is final:

```text
git rev-parse --short HEAD
python tests/validate_submission.py
```

- `checker.pass / fail / error`: the three numbers from the `SUMMARY` line, **exactly as printed**.
- `checker.commit`: the hash from `git rev-parse --short HEAD`, the commit you ran the checker at.
- `checker.kept_fails`: the ID of every FAIL you keep, e.g. `[CL5]` — `[]` if none.
- `assistant.model`: the exact model **with its version**. "ChatGPT" or "Claude" is not a model.

`submission.yml` holds facts only (same shape as Week 03); every explanation lives in
`lab-report.md`. Its two `assumptions` must match what you declared in §4.3.

**Your checker numbers are re-run automatically** at the commit you name. Numbers that do not match
what your repository actually produces are the one thing that costs the whole *evidence and
honesty* criterion. A FAIL you report and explain costs you nothing. Commit `submission.yml`, push,
open the PR.

---

## 6. Verdicts

```text
PASS   the check is satisfied
FAIL   the file is there and readable, but the check is not satisfied
ERROR  the file the check needs is missing or unreadable, so it could not run
```

A fresh copy of this folder prints **1 PASS · 8 FAIL · 21 ERROR** from `check_models.py` and
**5 PASS · 20 FAIL** from `validate_submission.py`. That is the intended start.

---

## 7. Submit

1. Branch `week-04`, all work inside `week-04/`. At least **3 meaningful commits**, including one
   made during the session.
2. Pull Request `week-04 → main` in your own repository. Title: `Week 04 — Modeling the System with
   UML`. **Description with the five headings from `SETUP.md` §4, spelled exactly** — *What I built ·
   AI tools used · What the AI got wrong · Time spent · What I would do differently*. In Week 03
   this was reported but not charged; **from this week it counts**, because it is checked
   automatically and your own headings are not recognised.
3. **Leave the PR open — do not merge it.**
4. In the Teams assignment: **+ Add work → Link → paste the pull request URL.**

The practice deck asks you to email screenshots at the end of class. **That does not apply to our
groups** — the PR link in Teams is the only submission, and it contains everything the email would
have (diagrams, source, prompts, original outputs, revisions, change log, tool and model).

**Deadline:** before the start of the next practice session. Late submissions per the course
policy; the Teams assignment closes at the end of the following week.

---

## 8. Grading — 1 point, 4 × 0.25

| Criterion | 0.25 when … |
| --- | --- |
| **Diagrams** | Revised use-case, class and one behaviour diagram render from their source; the AI's originals are kept unedited; a rendered image for each. |
| **Review** | §3–§5 findings name the element, the problem and the rule or story that proves it; §4.1 reads every association both ways; R2 is a note; assumptions are declared. |
| **Critique and consistency** | §6 has ≥ 3 issues with a reasoned verdict; §7 traces R1–R4 and every use case; §8 logs ≥ 3 real changes, one per diagram. |
| **Evidence and honesty** | §9 has the complete checker output with every kept FAIL explained; `AI_USAGE.md` complete; `submission.yml` passes the validator and its numbers match the automatic re-run; PR description uses the five `SETUP.md` headings; PR open with ≥ 3 meaningful commits. |

**A FAIL you report and explain costs you nothing. One you hide costs the whole criterion.**

**Not accepted:** declared checker numbers that the re-run at your commit does not reproduce ·
diagrams as images only, with no `.puml` source · an `original/` file that was
edited, or revised diagrams identical to the originals with no finding explaining why · checker
output that was edited, shortened or does not match your files · placeholder `<...>` rows ·
findings that cite no element and no rule ("the diagram is mostly fine") · a merged PR, a repo
link, or an emailed submission.

### What each check ID means

| ID | Check |
| --- | --- |
| UC1–UC3 | Student and Administrator declared, a named boundary, both actors outside it |
| UC4 | View availability, Book room, Cancel booking, Block/unblock room, Review usage present |
| UC5–UC6 | No actor linked to a confirmation; Student not linked to admin goals, Administrator not linked to Book or Cancel |
| UC7 | No screens, components or databases as use cases; no actor called System |
| UC8, CL5 | `' why:` above every include, extend, inheritance, composition, aggregation |
| UC9 | Revised use-case diagram differs from the original |
| CL1–CL4 | Student, Room, Booking; Booking associated with both; multiplicities at both ends; 1 ↔ 0..* |
| CL6–CL8 | No Service/Repository/Screen classes; start, end/duration, status, blocked present; R2 note |
| SQ1–SQ7 | Three lifelines; guarded alt; validation before creation; nothing saved on failure; all messages labelled; R1 and R3 visible |
| AC1–AC6 | Start/stop; decisions for R1, R3, R2; labelled guards; no fork; confirmation and rejection; create after the last check |
| FI1–FI2 | Original and image for every diagram |
| LR1–LR7, CS1–CS4 | Worksheet sections filled as the headings say; R1–R4 and every use case traced; lifelines explained |

---

## 9. FAQ

**Can I use a different assistant for the critique?** Yes — record it in `AI_USAGE.md`. It is still
another claim to evaluate, not independent evidence.

**The AI's first diagram looks right. Do I still have to revise it?** The use-case diagram, yes —
Task 1 asks for a revised diagram. If you genuinely find nothing, look again at the confirmation
and the actor links. For the others, an unchanged diagram is fine if §4/§5 show what you checked.

**Is "Send confirmation" a use case?** That is a modeling decision you make and defend. R4 makes
confirmation an outcome of booking, not something a student sets out to do. If you keep it, no
actor links to it directly and the `<<include>>` carries a `' why:`.

**Can I add an Administrator class, a User superclass, or a BookingStatus enum?** If a requirement
justifies it, yes — say which one in §4. "It is usual" is not a requirement.

**The checker FAILs something I believe is right.** Keep it, and explain it in §9. The checker is
dumb on purpose; you are not.

**Why the PR and not the email on slide 24?** Our groups submit through Teams. Everything the email
asks for is in the PR.
