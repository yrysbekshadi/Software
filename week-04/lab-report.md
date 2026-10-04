# Week 04 — Lab report: Modeling the System with UML

## 1. Setup

| Field | Value |
| --- | --- |
| Name | Shadi Yrysbek |
| Group | Not specified in the handout |
| AI assistant | ChatGPT |
| Exact model | GPT-5.6 Luna |
| Renderer | PlantUML-compatible source with local PNG previews |
| Behaviour diagram | sequence |
| Stories used | the reference set from README §3 |

## 2. Prompts as sent

### 2.1 Task 1 — use-case prompt

```text
Using the supplied scenario and approved stories, generate PlantUML for a use-case diagram. Include Student and Administrator outside a named system boundary. Model their goals, show justified associations, and list assumptions. Use include or extend only with a clear reason.
```

### 2.2 Task 2 — class prompt

```text
Create a UML domain class diagram in PlantUML for Smart Campus. Start with Student, Room, and Booking. Add attributes, appropriate operations, and association multiplicities. Add other classes only when requirements justify them. Explain each relationship and list assumptions. Avoid unjustified inheritance or composition.
```

### 2.3 Task 3 — behaviour prompt (3A sequence)

```text
Generate PlantUML for Book room. Use Student, BookingService, and BookingRepository lifelines. Validate the supplied rules, then attempt the reservation. Show a successful confirmation and an unavailable-room alternative using alt. Label messages and replies. Explain new design components and all assumptions.
```

### 2.4 Focused correction prompts (if you sent any)

```text
none
```

### 2.5 Critique prompt

```text
Compare my diagrams with the requirements. Identify missing rules, inconsistent names, and unjustified elements. Cite each issue and propose a specific correction.
```

## 3. Task 1 — use-case review

**Assumptions the AI listed:** the original AI draft did not list assumptions. I therefore declared A1 and A2 in the revised model and in §4.3.

| # | Element | Problem | Rule or story | Fix |
| --- | --- | --- | --- | --- |
| 1 | `View room availability screen` | It models a UI screen rather than the student's goal. | US-02; scenario says students view room availability. | Renamed it to `View availability`, which is the user goal. |
| 2 | `Student → Send confirmation` | Confirmation is an outcome of a successful booking, not a separate student goal. | R4 and US-01. | Removed `Send confirmation` as a use case; confirmation is shown as a result in the sequence diagram. |
| 3 | `Administrator → Book room` | The scenario gives booking to students, not administrators. | Scenario and US-01. | Removed the Administrator association with `Book room`. |

## 4. Task 2 — class diagram review

### 4.1 Relationships, read both ways

| Association | Read left → right | Read right → left | Multiplicities |
| --- | --- | --- | --- |
| Student — Booking | One student makes 0..* bookings. | Each booking belongs to exactly 1 student. | `Student 1 / Booking 0..*` |
| Room — Booking | One room has 0..* bookings over time. | Each booking is for exactly 1 room. | `Room 1 / Booking 0..*` |

### 4.2 Constraints the multiplicities cannot show

- R2: `Booking` contains a note stating that active bookings for the same room cannot overlap; multiplicity cannot express temporal overlap.
- R1: the `Booking` note states that the start is in the future and duration is greater than 0 and at most 2 hours.
- R3: `Room.blocked` is the domain state used to represent whether new bookings are allowed.

### 4.3 Assumptions

- A1: Touching bookings are allowed. A booking ending at 12:00 and another starting at 12:00 do not overlap.
- A2: Blocking a room does not cancel or modify existing bookings; it only prevents new bookings.

### 4.4 Findings

| # | Element | Problem | Rule or story | Fix |
| --- | --- | --- | --- | --- |
| 1 | `Student 1 *-- 1..* Booking` | The original used composition and said every student already has at least one booking. A booking is not a permanent part of a student. | Domain-model guidance in the handout; US-01 and US-03 allow students to have zero or more bookings. | Changed to a plain association `Student 1 -- 0..* Booking`. |
| 2 | `Room 1 -- 1..* Booking` | `1..*` incorrectly requires every room to have at least one booking. | Scenario permits free rooms and US-02 is about viewing free rooms. | Changed Booking multiplicity to `0..*`. |
| 3 | `Booking --> BookingService` | `BookingService` is a design component, not a domain concept. | Handout §4.2 says the domain class diagram should contain domain concepts only. | Removed it from the class diagram; kept it as a lifeline only in the sequence diagram and explained it in §5. |

## 5. Task 3 — behaviour diagram review

**Option chosen and why:** 3A sequence, because it makes the order of validation, persistence, failure, and confirmation directly visible.

**Design components added beyond the domain model:** `BookingService` validates R1, R3 and R2, coordinates the booking attempt, and returns the outcome; `BookingRepository` checks existing bookings and persists a successful booking.

| # | Element | Problem | Rule or story | Fix |
| --- | --- | --- | --- | --- |
| 1 | `BookingService -> BookingRepository: create booking` before validation | The original attempted to create a booking before checking the rules, which could persist an invalid reservation. | R1-R3; the handout explicitly requires validation before creation and nothing saved on failure. | Moved validation before persistence and only save inside the `created` branch. |
| 2 | `save failed booking` in the unavailable branch | The failure path still saved a booking, contradicting the rejection semantics. | R1-R3 and sequence review rule. | Removed every save/create message from the `unavailable` branch. |
| 3 | `alt [success]` / `else [unavailable]` | The handout's PlantUML convention says sequence guards must be written without square brackets. | PlantUML conventions in the handout. | Changed to `alt created` / `else unavailable`. |

## 6. AI critique

| # | Issue the AI raised | Element it cited | Verdict | Why |
| --- | --- | --- | --- | --- |
| 1 | `BookingService` and `BookingRepository` should appear in the class diagram because they are used in the sequence diagram. | `class.puml`, `BookingService`, `BookingRepository` | reject | The task explicitly asks for a **domain** class diagram and the review guidance says services and repositories do not belong there. They are design components for the sequence only. |
| 2 | The confirmation should be modeled as its own use case because R4 requires confirmation. | `use-case.puml`, confirmation | reject | R4 defines an outcome of a successful booking, not an independent actor goal. Making an actor perform confirmation would contradict the use-case review rule. |
| 3 | `Block / unblock room` could be split into two use cases because the stories are US-04 and US-05. | `use-case.puml`, `Block / unblock room` | reject | The scenario explicitly gives administrators the goal to block or unblock rooms, and the combined goal traces to both US-04 and US-05. Splitting it would add detail without a requirement. |
| 4 | The sequence should make the overlap decision explicit before creating the booking. | `sequence.puml`, overlap check | accept | This is consistent with R2. The revised sequence sends `check active booking overlap (R2)` before `create and save booking`, so no booking is persisted when a conflict exists. |

## 7. Consistency table

| Requirement / story | Use case | Classes | Behaviour element |
| --- | --- | --- | --- |
| R1 | `Book room` | `Booking.start`, `Booking.end` | `validate time range (R1)` before creation |
| R2 | `Book room`, `Cancel booking` | `Room`, `Booking`, R2 note, `Booking.status` | `check active booking overlap (R2)` |
| R3 | `Book room`, `Block / unblock room` | `Room.blocked` | `validate room status (R3)` |
| R4 | `Book room` | `Booking` | `confirmation (R4)` after `booking saved` |
| US-01 | `Book room` | `Student`, `Room`, `Booking` | validation → `create and save booking` → confirmation |
| US-02 | `View availability` | `Room`, `Booking` | not part of the chosen Book room sequence |
| US-03 | `Cancel booking` | `Student`, `Booking`, `Room` | not part of the chosen Book room sequence |
| US-04 | `Block / unblock room` | `Room.blocked` | not part of the chosen Book room sequence |
| US-05 | `Block / unblock room` | `Room.blocked` | not part of the chosen Book room sequence |
| US-06 | `Review usage` | `Room`, `Booking` | not part of the chosen Book room sequence |

## 8. Change log

| # | Diagram | Before (AI's original) | After (your revision) | Reason |
| --- | --- | --- | --- | --- |
| 1 | use case | `View room availability screen`; `Send confirmation`; Administrator linked to `Book room`. | `View availability`; no confirmation use case; Administrator only linked to `Block / unblock room` and `Review usage`. | Use cases must be actor goals and must match scenario responsibilities; R4 is an outcome. |
| 2 | class | `Student 1 *-- 1..* Booking`; `Room 1 -- 1..* Booking`; `BookingService` included as a class. | Plain `1 / 0..*` associations between Student/Booking and Room/Booking; only domain classes retained; R2 moved to a note. | Correct multiplicities, remove unjustified composition/design classes, and state R2 as a constraint. |
| 3 | sequence | Booking was created before validation and the failure branch saved a failed booking; guards used square brackets. | R1, R3 and R2 are validated first; save happens only in `created`; failure only rejects; guards are `created` / `unavailable`. | Enforces R1-R3 and the supplied PlantUML sequence conventions. |

## 9. Checker output

```text
Week 04 structural check - shape only, never quality

UC1  PASS  Student and Administrator declared
UC2  PASS  named system boundary: "Smart Campus"
UC3  PASS  all actors declared outside the boundary
UC4  PASS  all scenario goals present (5 use cases)
UC5  PASS  no actor is associated with a confirmation use case
UC6  PASS  actor responsibilities match the scenario
UC7  PASS  use cases are goals, not screens or components
UC8  PASS  every include / extend / generalization carries a ' why: comment (or there are none)
UC9  PASS  revised diagram differs from the original
CL1  PASS  Student, Room and Booking present
CL2  PASS  Booking is associated with Student and with Room
CL3  PASS  every association has multiplicities at both ends
CL4  PASS  1 student / 1 room per booking, 0..* bookings per student and per room
CL5  PASS  every inheritance / composition / aggregation carries a ' why: comment (or there are none)
CL6  PASS  only domain concepts in the class diagram
CL7  PASS  attributes needed by R1-R3 are present
CL8  PASS  a note states R2 (no overlapping active bookings)
SQ1  PASS  Student, BookingService and BookingRepository lifelines present
SQ2  PASS  alt block with a guard on every branch (2 branches)
SQ3  PASS  validation happens before creation
SQ4  PASS  nothing is saved on a failure branch
SQ5  PASS  every message is labelled
SQ6  PASS  R1 (time range) is visible - checked or stated as a precondition
SQ7  PASS  R3 (blocked room) is visible
FI1  PASS  the AI's original output is kept for every diagram
FI2  PASS  a rendered image for every diagram
LR1  PASS  §1 setup filled (tool and model recorded)
LR2  PASS  5 prompts pasted in §2
LR3  PASS  3 use-case findings in §3
LR4  PASS  §4 relationships read both ways, 2 assumption(s) declared
LR5  PASS  3 behaviour-diagram findings in §5
LR6  PASS  4 critique issues with a verdict
LR7  PASS  3 change-log rows covering all three diagrams
CS1  PASS  6 approved stories
CS2  PASS  §7 traces R1-R4 into the diagrams
CS3  PASS  every use case traces to an approved story
CS4  PASS  every lifeline is a domain class or an explained design component

SUMMARY pass=37 fail=0 error=0
A FAIL you report and explain costs you nothing. One you hide costs the criterion.
```

**FAILs I am keeping, and why:** none

## 10. Conclusion (120–180 words)

The class diagram was the part the AI got most wrong. Its first version used composition between Student and Booking and `1..*` at the Booking end, which incorrectly implied that every student already has a booking and that every room must already have at least one booking. It also put BookingService in the domain model even though the handout separates domain concepts from design components. The error most likely to reach implementation was the sequence diagram's creation-before-validation order: without review, an invalid or conflicting booking could be created before R1-R3 were checked. The critique found that BookingService and BookingRepository might appear in the class diagram, but I rejected that because the required class model is explicitly a domain model. It also suggested splitting Block / unblock room and making confirmation a use case; I rejected both because the reference stories support the combined administrator goal and R4 describes confirmation as a successful-booking outcome. The final diagrams now trace all four rules and all six approved stories consistently.
