# Lab report — Practice #03, Requirements Engineering with AI

Name: Shadi Yrysbek
Student ID: 24B031125
GitHub username: yrysbekshadi

---

## 1. Setup

| | |
| --- | --- |
| AI assistant (tool) | ChatGPT |
| Exact model name and version | GPT-5.6 Luna |
| Date of the session | 2026-09-27 |
| Diagram renderer used | PlantUML Online Server (linked render) |

One tool and one model were used for all three prompts.

---

## 2. Original AI output — user stories (Part 1)

Prompt used verbatim:

```text
You are a requirements analyst. For the Smart Campus study room booking
system, identify Student and Administrator goals. Write 6 to 8 user stories using: As a [role],
I want [goal], so that [reason]. Add a priority and one assumption to each story. Stay within the
supplied scenario.
```

Original unedited model output:

```text
1. As a Student, I want to view available study rooms and time slots, so that I can choose a suitable room for my study session.
Priority: High
Assumption: Availability reflects the current set of bookings.

2. As a Student, I want to book an available room for my chosen time, so that I can reserve a place to study without conflicts.
Priority: High
Assumption: Bookings can be made for up to two hours.

3. As a Student, I want to cancel my booking, so that I can release the room when I no longer need it.
Priority: Medium
Assumption: Only the student who created a booking can cancel it.

4. As a User, I want to receive a confirmation after booking or cancelling a room, so that I know my request was recorded.
Priority: Medium
Assumption: The system sends a confirmation immediately after a successful action.

5. As an Administrator, I want to block or unblock a study room, so that I can take a room out of service or return it to service.
Priority: High
Assumption: A blocked room cannot be booked.

6. As an Administrator, I want to review room usage over a period, so that I can understand how the rooms are being used.
Priority: Medium
Assumption: Usage is based on booking activity.

7. As a Student, I want to receive reminder notifications before my booking, so that I remember to attend my study session.
Priority: Low
Assumption: The system can send reminders before the booking.
```

---

## 3. Story review (Part 2)

| Story (as generated) | What I did | Why | Final ID |
| --- | --- | --- | --- |
| 1. Student — view availability | Kept, with wording tightened | It names a real stakeholder, has one testable outcome, and stays within UC-01. I made the assumption more explicit about bookings and room blocks. | US-01 |
| 2. Student — book room | Kept, with wording tightened | It matches UC-02 and the business rules. The final story explicitly says the time slot must be acceptable rather than implying only the reason. | US-02 |
| 3. Student — cancel booking | Kept, with wording tightened | It matches UC-03 and the scenario says the Student cancels a reservation the Student made. | US-03 |
| 4. User — receive confirmation | Rewrote stakeholder | "User" is not one of the two permitted stakeholders. The scenario names Student, so I changed the role to Student and kept the valuable outcome. | US-04 |
| 5. Administrator — block/unblock | Kept, with wording tightened | It matches UC-04 and gives a testable administrative outcome. | US-05 |
| 6. Administrator — review usage | Kept, with wording tightened | It matches UC-05 and stays at business-goal level. | US-06 |
| 7. Student — reminder notifications | Deleted | Reminder notifications are explicitly out of scope; the generated story also introduced attendance language. Keeping it would be scope creep. | — |

**Did the assistant invent anything outside the scenario?** Yes. Story 7 introduced reminder notifications, which are explicitly out of scope. It also referred to attending the study session, which is outside the stated functions because check-in/attendance is out of scope. I removed the story rather than weakening it into something that the scenario does not support.

**How many stories did you end with, and why that number?** I ended with 6. Six is enough to represent the six fixed business functions without keeping the out-of-scope reminder story or inventing an additional function.

---

## 4. Original AI output — acceptance criteria (Part 3)

Prompt used verbatim:

```text
For each selected story, write 3 to 5 acceptance criteria in Given, When, Then form. Include successful behavior, validation, and an error or alternative case. Apply these rules: bookings must be in the future, maximum duration is two hours, rooms cannot overlap, and blocked rooms cannot be booked. List assumptions before the criteria.
```

Original unedited model output:

```text
Assumptions
- Overlap: not allowed; a booking ending at the same time another booking begins is treated as an overlap.
- Duration: exactly two hours is allowed because the maximum is two hours.
- A cancellation is only possible for a booking created by the Student.

## US-02 — Book room

### AC-01
- Given a Student chooses a free room and a future one-hour time slot.
- When the Student books the room.
- Then the booking is created.

### AC-02
- Given the requested booking starts in the past.
- When the Student tries to book the room.
- Then the booking is rejected.

### AC-03
- Given the room already has a booking that overlaps the requested time.
- When the Student tries to book the room.
- Then the new booking is rejected.

### AC-04
- Given the room is blocked.
- When the Student tries to book the room.
- Then the new booking is rejected.

## US-03 — Cancel booking

### AC-05
- Given a Student has a booking.
- When the Student cancels it.
- Then the booking is removed from the schedule.

### AC-06
- Given a Student tries to cancel a booking that has already ended.
- When the Student submits the cancellation.
- Then the system rejects the cancellation.

### AC-07
- Given a Student has a booking.
- When the Student cancels it successfully.
- Then a confirmation is sent.

## US-05 — Block or unblock room

### AC-08
- Given a room is available.
- When the Administrator blocks it.
- Then the room becomes unavailable for booking.

### AC-09
- Given a room is blocked.
- When a Student tries to book it.
- Then the booking is rejected.

### AC-10
- Given a room is blocked.
- When the Administrator unblocks it.
- Then the room becomes available for booking.
```

---

## 5. Criteria review (Part 3)

| Criterion (as generated) | Problem | What I changed it to | Final ID |
| --- | --- | --- | --- |
| AC-01 | Happy path was testable, but it did not test the exact two-hour boundary. | Made the successful case exactly two hours in the future so the R2 boundary is explicit. | AC-01 |
| AC-02 | Good validation case and consistent with R1. | Kept, with wording made observable: rejected and no reservation created. | AC-02 |
| AC-03 | Good R3 validation case. | Kept, with explicit unchanged existing booking. | AC-03 |
| AC-04 | Good R4 validation case. | Kept, explicitly tied to a blocked room. | AC-04 |
| AC-05 | Correct successful cancellation case, but "removed from the schedule" was less precise than the UC wording. | Changed to "the reservation is released." | AC-05 |
| AC-06 | The scenario does not define a rule that past bookings cannot be cancelled. | Deleted this invented condition and replaced it with an alternative case based on the stated ownership of a Student's reservation. | — |
| AC-07 | Valid connection to UC-06, but "sent" is the business outcome and does not need an "immediately" timing assumption. | Kept the outcome and moved the observable condition to successful cancellation completion. | AC-06 |
| New alternative case | The AI did not cover the case where the Student has no reservation made by that Student. | Added a testable alternative that follows UC-03 without inventing a new business rule. | AC-07 |
| AC-08 | Correct administrative success case. | Kept with clearer availability wording. | AC-08 |
| AC-09 | Correctly covers R4. | Kept and explicitly states that the booking is rejected. | AC-09 |
| AC-10 | Correct administrative success case. | Kept with "returned to the available set" to match UC-04. | AC-10 |

**The two open questions.** I chose the boundary interpretations below because they are simple and consistent with the literal wording of the rules.

| Question | My decision | Why |
| --- | --- | --- |
| A booking ending exactly when another begins — overlap under R3? | allowed | The two bookings share no time, so they do not overlap. |
| Is exactly two hours allowed under R2? | allowed | "At most two hours" includes the two-hour boundary. |

**Which invalid or boundary case did the assistant leave out?** It did not explicitly test the exact two-hour boundary in its successful booking criteria. I added that boundary to AC-01. It also added an unsupported "past booking cannot be cancelled" rule in generated AC-06, which I removed.

---

## 6. Original AI output — use-case diagram (Part 4)

Prompt used verbatim:

```text
Create PlantUML code for a UML use-case diagram of the Smart Campus study room booking system. Place Student and Administrator outside the system boundary. Include View availability, Book room, Cancel booking, Block or unblock room, Review usage, and Send confirmation. Show only justified actor associations. Use include or extend only when the relationship is clear. Do not model screens, databases, or internal classes.
```

Original unedited PlantUML source:

```text
@startuml
left to right direction

actor Student
actor Administrator

rectangle "Smart Campus study room booking" {
  usecase "View availability" as UC01
  usecase "Book room" as UC02
  usecase "Cancel booking" as UC03
  usecase "Block or unblock room" as UC04
  usecase "Review usage" as UC05
  usecase "Send confirmation" as UC06
}

Student --> UC01
Student --> UC02
Student --> UC03
Student --> UC05

Administrator --> UC04
Administrator --> UC05

Student --> UC06
Administrator --> UC06

@enduml
```

Rendered diagram (image, or a link):

[Open the final PlantUML render](https://www.plantuml.com/plantuml/png/XP9BJiGm38RtFeNL3QjAC0-MQA0te1hsRkefqUI14cVG225n24x8IKWx7T4EI6GL__bi_xQoYK91aZLmXTl8fQB8s6hg0bdy-lZ4skPthCY-f8XHKdl4uBt5nlkzTXs0uPsWU0owUvQS6bY9zWw0bFY0TKvX9sDqtrhjT9H0EGBeMNATOIp-wLFW6o2co8F1uadpAzA1jA566ot70eT34RVLzSqKVSW5Xb8ZSZudT355AtAApK_BERgSLJLUxJ5Fb5mpNCSE9tGrHH_vqBjDaJekVXbOJz6QNOlAkvqEblejpiQwXNU0SPzObdUdKI-4nQMm19Xj_Qol_fRN09lielyHtm00)

The render shows two actors outside the system boundary and six use cases inside it.

---

## 7. Diagram review (Part 4)

| Element | Problem | What I changed |
| --- | --- | --- |
| Student → View availability | Correct responsibility. | Kept. |
| Student → Book room | Correct responsibility. | Kept. |
| Student → Cancel booking | Correct responsibility. | Kept. |
| Student → Review usage | Wrong association: reviewing usage is assigned to the Administrator in the supplied actor definition. | Removed. |
| Administrator → Block or unblock room | Correct responsibility. | Kept. |
| Administrator → Review usage | Correct responsibility. | Kept. |
| Student → Send confirmation | Wrong association: UC-06 describes the system confirming a booking/cancellation; it is not a separate action triggered by a person. | Removed. |
| Administrator → Send confirmation | Same problem: the Administrator does not trigger UC-06 in the supplied scenario. | Removed. |

**Associations.** The unjustified links were **Student → UC-05 Review usage**, **Student → UC-06 Send confirmation**, and **Administrator → UC-06 Send confirmation**. The first conflicts with the stated Administrator responsibility to watch usage. The latter two treat an automatic confirmation function as a person-triggered use case.

**Did any screen, database or internal component appear as a use case or an actor?** No.

---

## 8. Traceability (Part 5)

Summarise what the table in `requirements/traceability.md` shows:

- Use cases with **no story** behind them: none.
- Stories with **no use case** they belong to: none.
- Criteria that test **no rule** from section 1: AC-05, AC-06, AC-07, AC-08 and AC-10 primarily verify business outcomes rather than directly validating R1–R4. This is expected because the exercise also asks for successful behavior, not only rule checks.

**What does the largest gap tell you about the generated requirements?** The largest review issue was not missing coverage but incorrect responsibility boundaries. The original diagram connected people to functions they do not trigger, and the original criteria invented a cancellation rule. Traceability exposed that all six fixed use cases could still be represented without adding a new use case.

---

## 9. Checker runs

The requirements checker was run from inside `week-03/` after the revised artifacts were written.

```text
$ python tests/check_requirements.py
PASS   US-1  user-stories.md         no placeholders left
PASS   US-2  user-stories.md         6 stories, IDs US-01…US-06
PASS   US-3  user-stories.md         every story has the required sentence shape
PASS   US-4  user-stories.md         every story has a priority
PASS   US-5  user-stories.md         every story declares an assumption
PASS   US-6  user-stories.md         only Student and Administrator appear as roles
PASS   US-7  user-stories.md         nothing from the out-of-scope list appears
PASS   AC-1  acceptance-criteria.md  no placeholders left
PASS   AC-2  acceptance-criteria.md  three sections, all naming real stories: US-02, US-03, US-05
PASS   AC-3  acceptance-criteria.md  every section has 3 to 5 uniquely numbered criteria
PASS   AC-4  acceptance-criteria.md  all 10 criteria are complete Given/When/Then
PASS   AC-5  acceptance-criteria.md  every section covers an invalid or boundary case
PASS   AC-6  acceptance-criteria.md  3 assumptions listed before the criteria
PASS   AC-7  acceptance-criteria.md  both open questions are settled in the assumptions
PASS   PU-1  use-cases.puml          valid PlantUML block, no placeholders
PASS   PU-2  use-cases.puml          exactly two actors: Student, Administrator
PASS   PU-3  use-cases.puml          all six use cases present
PASS   PU-4  use-cases.puml          system boundary present
PASS   PU-5  use-cases.puml          no screens, databases or internal components
PASS   PU-6  use-cases.puml          no unjustified actor associations found
PASS   TR-1  traceability.md         all six use cases have a row
PASS   TR-2  traceability.md         every ID in the table resolves
PASS   TR-3  traceability.md         every story appears in the table
------------------------------------------------------------------------
23 PASS · 0 FAIL · 0 ERROR   (23 checks)
Shape is clean. This says nothing about whether the requirements are good.
```

The identity fields were filled for this revision. The final commit SHA is still pending because it must be the SHA of the commit in the student repository that contains the final week-03 files. It is not safe to invent or reuse a local/different commit hash.

```text
$ python tests/validate_submission.py
submission.yml — submission.yml
------------------------------------------------------------------------
PASS   schema                                    1
PASS   week                                      03
PASS   student.name                              Shadi Yrysbek
PASS   student.student_id                        24B031125
PASS   student.github                            yrysbekshadi
PASS   assistant.tool                            ChatGPT
PASS   assistant.model                           GPT-5.6 Luna
PASS   counts.user_stories                       6
PASS   counts.acceptance_criteria_sets           3
PASS   checker                                   23 PASS · 0 FAIL · 0 ERROR
NOTE   checker                                   you are claiming a clean run — it will be re-run at your commit, so make sure it is true
FAIL   checker.commit                            not a commit hash — use `git rev-parse --short HEAD`, got 'FINAL_COMMIT_SHA'
PASS   assumptions.overlap_touching_bookings     allowed
PASS   assumptions.exactly_two_hours             allowed
PASS   traceability.use_cases_not_covered        []
PASS   traceability.stories_not_traced           []
NOTE   traceability                              you are claiming full coverage in both directions — that is rare on a first pass, and it is checked
PASS   review_findings                           3 findings
PASS   review_findings[1]                        US-07 was removed because reminder notifications are explicitly out of scope.
PASS   review_findings[2]                        UC-05 Student → Review usage was removed because usage review belongs to the Administrator.
PASS   review_findings[3]                        UC-06 Send confirmation was left without actor associations because no person triggers the system confirmation function.
PASS   honesty.can_explain_everything_submitted  yes
PASS   honesty.ai_usage_disclosed                yes
------------------------------------------------------------------------
20 PASS · 1 FAIL · 0 ERROR · 2 note
The remaining FAIL is expected until the final repository commit SHA is known.
```

| | PASS | FAIL | ERROR |
| --- | --- | --- | --- |
| `check_requirements.py` | 23 | 0 | 0 |
| `validate_submission.py` | 20 | 1 | 0 |

Final values must be replaced after the last commit by running:

```text
git rev-parse --short HEAD
python tests/check_requirements.py
python tests/validate_submission.py
```

The final `checker.commit` in `submission.yml` and this section must match that exact commit.

**Every FAIL, one line each: what it is and what you decided to do about it.** The only remaining FAIL is the intentionally unfilled final commit SHA; no requirements-checker FAILs are present.

**Did you run the checks by hand instead of with Python?** No. The requirements checker and current declaration validator were run with Python; the declaration validator must be run once more after the final repository commit SHA is inserted.

---

## 10. Conclusion (150–200 words)

The most wrong part of the generated requirements was the responsibility mapping in the use-case diagram. The AI connected Student to Review usage and connected both actors to Send confirmation, even though the scenario assigns usage review to the Administrator and describes confirmation as something the system sends after a booking or cancellation. I caught that by checking every association against the two actor definitions and the six fixed use cases, not by relying on the structural checker.

The assistant was most useful for producing a complete first draft quickly: it covered the six main functions, gave each story a priority and assumption, and produced Given/When/Then structures that I could review rather than write from an empty page. That reduced mechanical drafting time.

The first requirement I would rewrite before handing the work to an implementer is US-04, the confirmation story. It is valid as a user outcome, but it crosses a system-triggered UC-06 with a Student-facing goal. I would make the distinction between the student's need for a recorded outcome and the system's automatic confirmation behavior explicit, so an implementer does not infer an extra person-triggered action.

